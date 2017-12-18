#Next steps: indexation des descriptions pour gestion du NLP 

import pickle
from dateparser import parse

def get_genre():
    """ Returns a tuple: list of exhibition genres + cards to be used in quck replies """
    
    with open("backend/exhibition/data_exhibition", 'rb') as f:
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

    with open("backend/exhibition/data_exhibition", 'rb') as f:
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
                "url": "https://www.google.fr/maps/search/"+r['location'],
                "title":"C'est où ?"
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
    #---to test get genre function, uncomment the following line
    #print(get_genre())
    
    #---to test get exhibition function, uncomment the following line
    print(get_exhib('Art contemporain', 1))