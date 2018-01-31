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
                eltm['summary'] = elte['summary']
                eltm['price'] = elte['price']
                merged.append(eltm)

    with open("backend/exhibition/expo_offspect", 'wb') as f:
        p = pickle.Pickler(f)
        p.dump(merged)

def get_genre_exhib():
    """ Returns a tuple: list of exhibition genres + cards to be used in quick replies """
    
    with open("backend/exhibition/expo_offspect", 'rb') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
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

def get_exhib(genre, iteration):
    """ returns tuple: data of 5 exhibitions of the desired genre + cards to send """

    with open("backend/exhibition/expo_offspect", 'rb') as f:
        d = pickle.Unpickler(f)
        data = d.load()
    exhibs = []
    for elt in data:
        if elt['type'] == genre:
            exhibs.append(elt)

    #Results sorted by ascending date of start, 
    results = sorted(exhibs, key=lambda k: k['d_start'])[(iteration-1)*5 : iteration*5]

    cards=[]
    for i, r in enumerate(results):
        cards.append(
            {
            "title": r['title'],
            "image_url": r['img_url'], 
            "subtitle": r['location'] + "\nJusqu'au" + r['date_end'],
            "buttons":[{
                "type":"web_url",
                "url": r['url'],
                "title":"Voir sur Offi"
                },
                {
                "type":"postback",
                "title":"Détails",
                "payload":"Summary_expo*-/{}*-/{}*-/{}".format(r['type'] ,i, iteration)
                }]      
            }
        )

    return results, cards


if __name__ == "__main__":
    #---to get merged result of scraped data, uncomment the following line
    #merge_offspect()
    
    #---to test get exhibition function, uncomment the following line
    test = get_exhib('Art contemporain', 1)
    print(test)