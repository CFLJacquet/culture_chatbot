
import pickle
from dateparser import parse
import json
from unicodedata import normalize
import scrapy
from scrapy.crawler import CrawlerProcess

def transform_opening_hours(prog):
    "Tous les jours (sauf lun) 14h-19h."
    x = prog
    return x

def merge_results():
    """ Fusionne la liste des spectacles de l'office des spectacles et le détail de chaque page pour avoir le résumé. \
        les dates de début et fin sont aussi transformées en objets date"""

    main = []
    with open('backend/exhibition/expo_scraper/extracted_data/offSpec_main.jsonl') as f:
        for line in f:
            main.append(json.loads(line))

    extra = []
    with open('backend/exhibition/expo_scraper/extracted_data/offSpec_details.jsonl') as f:
        for line in f:
            extra.append(json.loads(line))
    
    merged = []

    for eltm in main:
        for elte in extra:
            if eltm['url'] == elte['url']:
                eltm['d_start'] = parse(eltm['date_start']).date()
                eltm['d_end'] = parse(eltm['date_end']).date()
                eltm['summary'] = elte['summary']
                eltm['price'] = elte['price']
                merged.append( eltm)

    with open("backend/exhibition/data_exhibition", 'wb') as f:
        p = pickle.Pickler(f)
        p.dump(merged)


if __name__ == "__main__":
    #---to test the opening hours transformation function, uncomment the following line
    #transform_opening_hours( "Tous les jours (sauf lun) 14h-19h.")

    #---to get merged result of scraped data, uncomment the following line
    merge_results()