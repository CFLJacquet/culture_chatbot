import json
from operator import itemgetter
from datetime import datetime as dt
from pprint import pprint

def get_genre():
    """ Returns a tuple: list of exhibition genres + cards to be used in quick replies """
    
    with open("backend/exhibition/data_exhibition.json", 'r') as f:
        data = json.load(f)

    genre = []
    for elt in data:
        if elt['genre'] not in genre and not isinstance(elt['genre'], list) : 
            print(elt['genre'])
            genre.append(elt['genre'])
    
    btns = []
    for g in genre:                 #create button list to be sent
        btns.append(
        {
            "content_type":"text",
            "title": str(g),
            "payload": str(g) + "-1"
        })
    btns.append(
        {
            "content_type":"text",
            "title":"Autre chose",
            "payload":"Not_interested"
        })

    return genre, btns

def get_exhib(genre, iteration):
    """ returns tuple: data of 5 exhibitions of the desired genre + cards to send """

    with open("backend/exhibition/data_exhibition.json", 'r') as f:
        data = json.load(f)
    
    #Appends exhibitions from the selected genre, if it is still shown 
    exhibs = []
    for elt in data:
        if str(elt['genre']) == genre and dt.strptime(elt['d_end'], "%Y-%m-%d") >= dt.today():
            exhibs.append(elt)

    #Results sorted by rank then ascending date of end , 
    per_date = sorted(exhibs, key = itemgetter('d_end'))
    per_rank = sorted(per_date, key= itemgetter('rank'), reverse=True)[(iteration-1)*5 : iteration*5]

    cards=[]
    for i, r in enumerate(per_rank):
        cards.append(
            {
            "title": r['title'],
            "image_url": r['img_url'], 
            "subtitle": r['location'] + "\nJusqu'au " + dt.strptime(r['d_end'], "%Y-%m-%d").strftime('%d/%m'),
            "buttons":[{
                "type":"web_url",
                "url": "https://www.google.fr/maps/search/"+r['location'],
                "title":"C'est où ?"
                },
                {
                "type":"postback",
                "title":"C'est quoi ?",
                "payload":"Summary_expo*-/{}*-/{}*-/{}".format(r['genre'] ,i, iteration)
                }]      
            }
        )

    return per_rank, cards

def get_exhib_query(exhib_ID_list, iteration):
    """ returns tuple: data of 5 exhibitions from the list of exhibition found by vect_search + cards to send """

    with open("backend/exhibition/data_exhibition.json", 'r') as f:
        data = json.load(f)
    
    #Appends exhibitions from the list, if it is still shown 
    exhibs = []
    for ID in exhib_ID_list:
        exhib = [ x for x in data if x['ID'] == int(ID)] # and dt.strptime(x['d_end'], "%Y-%m-%d") >= dt.today()
        exhibs.append(exhib[0])        

    #Results sorted by rank then ascending date of end , 
    #per_date = sorted(exhibs, key = itemgetter('d_end'))
    #per_rank = sorted(per_date, key= itemgetter('rank'), reverse=True)[(iteration-1)*5 : iteration*5]

    cards=[]
    for i, r in enumerate(exhibs[:10]):
        cards.append(
            {
            "title": r['title'],
            "image_url": r['img_url'], 
            "subtitle": r['location'] + "\nJusqu'au " + dt.strptime(r['d_end'], "%Y-%m-%d").strftime('%d/%m'),
            "buttons":[{
                "type":"web_url",
                "url": "https://www.google.fr/maps/search/"+r['location'],
                "title":"C'est où ?"
                },
                {
                "type":"postback",
                "title":"C'est quoi ?",
                "payload":"Summary_expo*-/{}*-/{}*-/{}".format(r['genre'] ,i, iteration)
                }]      
            }
        )

    return cards


if __name__ == "__main__":    
    #---to test get genre function, uncomment the following line
    # print(get_genre())
    
    #---to test get exhibition function, uncomment the following line
    # pprint(get_exhib('Art contemporain', 1))

    #---to test get exhibition per query function, uncomment the following line
    # the list corresponds to the sentence input "je veux voir une expo de peinture"
    pprint(get_exhib_query(['263', '117', '102', '62', '280', '246', '94', '249', '220', '296', '135', '179', '265', '275', '204'], 1))