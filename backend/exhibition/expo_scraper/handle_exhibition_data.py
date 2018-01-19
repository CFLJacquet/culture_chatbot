from nltk.tokenize import RegexpTokenizer
import json
import re
import os
from pprint import pprint
from operator import itemgetter
import pandas as pd

from scrapy.crawler import CrawlerProcess
from expo_scraper.spiders.spider_expoInTheCity import Expo_expoInTheCity_Spider
from expo_scraper.spiders.spider_offSpectacles import Expo_offspec_Spider
from expo_scraper.spiders.spider_parisBouge import Expo_parisbouge_Spider
#from expo_scraper.spiders.spider_timeout import Expo_timeout_Spider

tokenizer = RegexpTokenizer(r'\w+')
stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read()

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

def transform_opening_hours(prog):
    "Tous les jours (sauf lun) 14h-19h."
    x = prog
    return x

def tok_title(cell):
    """ for merging operation, to detect duplicates """
    words = tokenizer.tokenize(cell.lower())
    return [word for word in words if word not in stopwords]

def merge_results():
    """ Merges the data from scrapped sites (ParisBouge, Offi des Spectacles, TimeOut). Returns a list of dict """

    # Format of data (columns)
    # ['title']['img_url']['url']['genre']['location']['d_start']['d_end']['timetable']
    # ['reviews']['rank']['summary']['price']['source']['tags']
    
    data = pd.read_json("backend/exhibition/expo_scraper/extracted_data/all_expo.jsonl", lines=True)
    data.drop_duplicates(subset=['title', 'summary', 'source'], keep='first', inplace=True)

    data["title_check"] = data['title'].apply(lambda x: tok_title(x))
    data["sort"] = data["title_check"].apply(lambda x : ''.join(x))
    data.sort_values(by=['sort', 'source'], ascending=[False, False], inplace=True)

    clean = pd.DataFrame(columns = data.columns)
    for index, row in data.iterrows():
        try:
            if set(row["title_check"]).issubset(set(clean.tail(1)["title_check"].tolist()[0])):
                clean.iloc[-1, clean.columns.get_loc("reviews")]  += "\n" + row["summary"]
                clean.iloc[-1, clean.columns.get_loc("rank")] += 1
                clean.iloc[-1, clean.columns.get_loc("tags")] += row["tags"]
                if clean.iloc[-1, clean.columns.get_loc("img_url")] == "":
                    clean.iloc[-1, clean.columns.get_loc("img_url")] = row["img_url"]
            else:
                clean = clean.append(row, ignore_index=True)
        except:
            #needed to append the first line of the table
            clean = clean.append(row, ignore_index=True)

    clean.drop(["title_check", "sort"], axis=1, inplace=True)

    return clean


def append_to_full(new_list):
    """ Appends only the new exhibitions to the existing list of exhibitions """

    hist = pd.read_json("backend/exhibition/data_exhibition.json")
    print("The database contains {} exhibitions.".format(hist.shape[0]))
    
    ID = max(hist["ID"])+1
    nb_add =0
    for index, row in new_list.iterrows():
        if row["title"] not in hist["title"].values:
            row["ID"] = ID
            hist = hist.append(row, ignore_index=True)
            nb_add +=1
            ID +=1

    hist.to_json("backend/exhibition/data_exhibition.json", orient="records")
    
    print("Appended {} new exhibitions.\nThe database now contains {} exhibitions.".format(nb_add, hist.shape[0]))

if __name__ == "__main__":
    #---to test the opening hours transformation function, uncomment the following line
    #transform_opening_hours( "Tous les jours (sauf lun) 14h-19h.")

    #---to run all the spiders, uncomment the following line
    # run_spiders()

    #---to get merged result of scraped data, uncomment the following line
    append_to_full(merge_results())