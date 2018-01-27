from nltk.tokenize import RegexpTokenizer
import json
import re
import os
from pprint import pprint
from operator import itemgetter

import pandas as pd
import numpy as np
from sklearn.externals import joblib

from scrapy.crawler import CrawlerProcess
from expo_scraper.spiders.spider_expoInTheCity import Expo_expoInTheCity_Spider
from expo_scraper.spiders.spider_offSpectacles import Expo_offspec_Spider
from expo_scraper.spiders.spider_parisBouge import Expo_parisbouge_Spider
#from expo_scraper.spiders.spider_timeout import Expo_timeout_Spider

tokenizer = RegexpTokenizer(r'\w+')
stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read().split("\n")

def run_spiders():
    ''' Runs all the spiders (expoInTheCity, offspec, parisbouge, timeout) '''
    try:
        os.remove("backend/exhibition/expo_scraper/extracted_data/all_expo.jsonl")
    except OSError:
        pass

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/all_expo.jsonl'
    })
    
    process.crawl(Expo_expoInTheCity_Spider)
    process.crawl(Expo_offspec_Spider)
    process.crawl(Expo_parisbouge_Spider)
    #process.crawl(Expo_timeout_Spider)
    process.start() # the script will block here until the crawling is finished

def aggregate(basis, new):
    """ Aggregates the values of a duplicate exhib from 'new' if exhib is already in 'basis' list """
    already = []

    for clean_elt in basis:
        for elt in new:
            
            merge = False
            title_check = set(elt["title_check"]) & set(clean_elt["title_check"])
            date_check = (np.array(elt["date_check"]) == np.array(clean_elt["date_check"]))
            location_check = set(elt["location_check"]) & set(clean_elt["location_check"])
            
            # if the title contains 1 word only, check if dates are almost equal or location is almost equal 
            if len(elt["title_check"]) == 1 or clean_elt["title_check"] == 1:
                if len(title_check) == 1 and ((6 - sum(date_check) <= 1 ) or (len(location_check) >= min(len(elt["location_check"]), len(clean_elt["location_check"])))):
                    merge = True
            # if title is longer than 1 word
            else :   
                if len(title_check) > 1 and ((6 - sum(date_check) <= 1 ) or (len(location_check) >= min(len(elt["location_check"]), len(clean_elt["location_check"])))):
                    merge = True
            # if date is default one, check if title is almost identical
            if elt["d_start"] == "2000-01-01":
                if len(title_check) >= min(len(elt["title_check"]), len(clean_elt["title_check"])):
                    merge = True

            if merge == True:
                already.append(elt["title"])

                clean_elt['reviews'] += "\n" + elt['summary']
                clean_elt['rank'] += 1
                clean_elt["tags"] += elt["tags"]
                if elt["img_url"] != "" or elt["img_url"] != "/res/img/photo_vide_small.png":
                    clean_elt["img_url"] = elt["img_url"] 

                #replace missing values
                if "indisp." in clean_elt["price"]:
                    clean_elt["price"] = elt["price"]
                if "indisp." in clean_elt["timetable"]:
                    clean_elt["timetable"] = elt["timetable"]
                if "indisp." in clean_elt["summary"]:
                    clean_elt["summary"] = elt["summary"]
                if "indisp." in clean_elt["timetable"]:
                    clean_elt["timetable"] = elt["timetable"]
                if "indisp." in clean_elt["location"]:
                    clean_elt["location"] = elt["location"]

                merge = False
    
    return basis, already

def tok_title(cell):
    """ for merging operation, to detect duplicates """
    words = tokenizer.tokenize(cell.lower())
    return [word for word in words if word not in stopwords]

def merge_results(file_name):
    """ Merges the data from scrapped sites (ParisBouge, Offi des Spectacles, TimeOut). Returns a DataFrame """

    # Format of data (columns)
    # ['title']['img_url']['url']['genre']['location']['d_start']['d_end']['timetable']
    # ['reviews']['rank']['summary']['price']['source']['tags']
    
    all_ex = pd.read_json(file_name, lines=True)
    all_ex.drop_duplicates(subset=['title', 'd_end', 'd_start', 'source'], keep='first', inplace=True)

    all_ex["title_check"] = all_ex['title'].apply(lambda x: tok_title(x))
    all_ex["location_check"] = all_ex['location'].apply(lambda x: tok_title(x))
    all_ex["date_check"] = (all_ex["d_end"]+" "+all_ex["d_start"]).apply(lambda x: tok_title(x))
    
    offspec = all_ex[all_ex["source"]=="5-offSpectacles"].to_dict(orient = "records")
    expoITC = all_ex[all_ex["source"]=="3-expoInTheCity"].to_dict(orient = "records")
    pb = all_ex[all_ex["source"]=="4-parisBouge"].to_dict(orient = "records")

    n1 = aggregate(offspec, pb)
    for elt in pb:
        if elt['title'] not in n1[1]:
            n1[0].append(elt)
            n1[1].append(elt['title'])
            
    n2 = aggregate(n1[0], expoITC)
    for elt in expoITC:
        if elt['title'] not in n2[1]:
            n2[0].append(elt)
            n2[1].append(elt['title'])

    clean = pd.DataFrame(n2[0]).sort_values("rank", ascending=False)
    clean.drop(["title_check", "location_check", "date_check"], axis = 1, inplace = True)

    clean["price"].replace(['0', '0,00', 'Entrée libre', 'entrée libre', ' entrée libre.', ' entréelibre.', 'Billets expositions temporaires\nGratuit : Entrée libre. )',  'GRATUIT', 'gratuit', 'accès libre'], 'Gratuit', inplace=True)
    clean["img_url"].replace(['', '/res/img/photo_vide_small.png'], "http://fotomelia.com/wp-content/uploads/edd/2015/08/photo-gratuite-libre-de-droit-domaine-public17-1560x1040.jpg")
    clean["Gratuit"] = clean["price"].map({"Gratuit" : 1})
    clean["Gratuit"].fillna(0, inplace=True)

    return clean


def append_to_full(new_list):
    """ Appends only the new exhibitions to the existing list of exhibitions """

    hist = pd.read_json("backend/exhibition/data_exhibition.json")
    hist.to_json("backend/exhibition/data_exhibition_backup.json", orient="records")
    
    print("The database contains {} exhibitions.".format(hist.shape[0]))
    
    to_predict = pd.DataFrame(columns = hist.columns)

    ID = max(hist["ID"])+1
    for index, row in new_list.iterrows():
        if row["title"] not in hist["title"].values:
            row["ID"] = ID
            to_predict = to_predict.append(row, ignore_index=True)
            ID +=1
    
    tags = ['Architecture', 'Sculpture', 'Peinture', 'Musique', 'Littérature', 'Danse', 'Cinéma', 
    'Photographie', 'Mode', 'Beaux-Arts', 'Art contemporain', 'Histoire / Civilisations', 'Famille']
    for elt in tags:
        name = elt.replace(' / ', '_').replace(' ', '_')
        clf = joblib.load('backend/exhibition/expo_scraper/expo_classifiers/classifier_{}.pkl'.format(name)) 
        input_d = to_predict['title']+" "+ to_predict['reviews']+" "+ to_predict['summary']+" "+ to_predict['location']+" "+ to_predict['tags'].apply(lambda x: str(x)*4)
        #call ML models to classify exhibition
        to_predict[elt] = clf.predict(input_d)
    
    full = hist.append(to_predict, ignore_index=True)
    full["Other"] = np.where(full[tags].sum(axis = 1) == 0, 1, 0)
    full.to_json("backend/exhibition/data_exhibition.json", orient="records")
    print("Appended {} new exhibitions.\nThe database now contains {} exhibitions.".format(to_predict.shape[0], full.shape[0]))

if __name__ == "__main__":
    #---to run all the spiders, uncomment the following line
    run_spiders()

    #---to get merged result of scraped data, uncomment the following line
    append_to_full(merge_results("backend/exhibition/expo_scraper/extracted_data/all_expo.jsonl"))
