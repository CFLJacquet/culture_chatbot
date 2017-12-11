#Next steps: indexation des descriptions pour gestion du NLP 

import json
import pickle
from dateparser import parse

def merge_offspect():
    """ Fusionne la liste des spectacles de l'office des spectacles et le détail de chaque page pour avoir le résumé. \
        les dates de début et fin sont aussi transformées en objets date"""

    main = []
    with open('backend/exhibition/expo_scraper/expo_offspect.jsonl') as f:
        for line in f:
            main.append(json.loads(line))

    extra = []
    with open('backend/exhibition/expo_scraper/expo_offspect_detail.jsonl') as f:
        for line in f:
            extra.append(json.loads(line))
    
    merged = []

    for eltm in main:
        for elte in extra:
            if eltm['url'] == elte['url']:
                eltm['d_start'] = parse(eltm['date_start']).date()
                eltm['d_end'] = parse(eltm['date_end']).date()
                eltm['summary'] = elte['summary'].encode("utf-8")
                eltm['price'] = elte['price']
                merged.append(eltm)

    with open("backend/exhibition/expo_offspect", 'wb') as f:
        p = pickle.Pickler(f)
        p.dump(merged)

def get_genre():
    """ Returns a tuple: list of exhibition genres + cards to be used in quck replies """
    
    with open("backend/exhibition/expo_offspect", 'rb') as f:
        d = pickle.Unpickler(f)
        data = d.load()

    genre = []
    for elt in data:
        genre.append(elt['type'])
    no_duplicates = list(set(genre))
    genre = sorted(no_duplicates)        # genre list without duplicates
    
    btns = []
    for g in genre:                 #create button list to be sent
        btns.append(
        {
            "content_type":"text",
            "title": g,
            "payload": g + "-1"
        })
    btns.append(
        {
            "content_type":"text",
            "title":"Rien de tout ça",
            "payload":"Not_interested"
        })

    return genre, btns



if __name__ == "__main__":
    #merge_offspect()
    test = get_genre()
    print(test)