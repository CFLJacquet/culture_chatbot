from nltk.tokenize import RegexpTokenizer
import json
import os
from pprint import pprint
from operator import itemgetter

tokenizer = RegexpTokenizer(r'\w+')

def transform_opening_hours(prog):
    "Tous les jours (sauf lun) 14h-19h."
    x = prog
    return x

def merge_results():
    """ Merges the data from scrapped sites (ParisBouge, Offi des Spectacles, TimeOut). Returns a list of dict """

    # Format of data
    # i = {}
    # i['title']
    # i['img_url']
    # i['url']
    # i['genre']
    # i['location']
    # i['d_start']
    # i['d_end']
    # i['timetable']
    # i['reviews']
    # i['rank']
    # i['summary']
    # i['price']

    merged = []
    with open('backend/exhibition/expo_scraper/extracted_data/offSpectacles.jsonl') as f:
        for line in f:
            if not any(d['title'].lower() == json.loads(line)['title'].lower() for d in merged):
                merged.append(json.loads(line))

    parisBouge = []
    with open('backend/exhibition/expo_scraper/extracted_data/parisBouge.jsonl') as f:
        for line in f:
            if not any(d['title'].lower() == json.loads(line)['title'].lower() for d in parisBouge):
                parisBouge.append(json.loads(line))
    
    timeout = []
    with open('backend/exhibition/expo_scraper/extracted_data/timeout.jsonl') as f:
        for line in f:
            timeout.append(json.loads(line))

    # Merge Parisbouge and Officiel des Spectacles
    extra = []
    for parisBouge_elt in parisBouge:
        found = False
        p = tokenizer.tokenize(parisBouge_elt['title'].lower())
        for offSpectacles_elt in merged:
            o = tokenizer.tokenize(offSpectacles_elt['title'].lower())
            if len(o) < len(p):
                small = o
            else: 
                small = p
            
            if set(o) & set(p) == set(small) :
                offSpectacles_elt['reviews'] += "\n" + parisBouge_elt['summary']
                offSpectacles_elt['rank'] += 1
                found = True
                break
        if found == False:
            extra.append(parisBouge_elt)
    
    sorted_exhib = sorted(merged + extra, key=itemgetter('title')) 

    for timeout_elt in timeout:
        t = tokenizer.tokenize(timeout_elt['title'].lower())
        for elt in sorted_exhib:
            s = tokenizer.tokenize(elt['title'].lower())
            if len(s) < len(t):
                small = s
            else: 
                small = t
            
            if set(s) & set(t) == set(small) :
                elt['reviews'] += "\n" + timeout_elt['review']
                elt['rank'] += 1
                break

    return sorted_exhib


def append_to_full(new_list_of_exhib):
    """ Appends only the new exhibitions to the existing list of exhibitions """

    i = 0
    try: 
        with open('backend/exhibition/data_exhibition.json', 'r') as f:
            data = json.load(f)
        print('the database already contains {} exhibitions'.format(len(data)))
    except: 
        data = []
        print('creating new file')

    for elt in new_list_of_exhib:
        if not any(d['title'] == elt['title'] for d in data):
            data.append(elt)
            i += 1
    
    with open('backend/exhibition/data_exhibition.json', 'w') as outfile:
        json.dump(data, outfile)
    
    print("Appended {} new exhibitions".format(i))

if __name__ == "__main__":
    #---to test the opening hours transformation function, uncomment the following line
    #transform_opening_hours( "Tous les jours (sauf lun) 14h-19h.")

    #---to get merged result of scraped data, uncomment the following line
    append_to_full(merge_results())