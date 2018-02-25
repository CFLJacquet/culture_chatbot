import json
from operator import itemgetter
from datetime import datetime as dt
from pprint import pprint

def get_genre_exhib():
    """ Returns a tuple: list of exhibition genres + cards to be used in quick replies """

    # NB: les genres sont rangés par ordre de préférence, mais il n'y pas de mécanisme de retour 
    # utilisateur => besoin d'augmenter la valeur quand un utilisateur clique dessus + option: 
    # "plus de genres"

    with open("backend/exhibition/genre_popularity.json", 'r') as f:
        data = json.load(f)

    genre = [(genre, rank) for genre, rank in data.items()]
    genre.sort(key=lambda x:x[1], reverse=True)

    btns = []
    for g in genre[:9]:                 #create button list to be sent
        btns.append(
        {
            "content_type":"text",
            "title": str(g[0]),
            "payload": str(g[0]) + "-1"
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
    exhibs = [ elt for elt in data if elt[genre] == 1 \
    and dt.strptime(elt['d_end'], "%Y-%m-%d") >= dt.today() \
    and dt.strptime(elt['d_start'], "%Y-%m-%d") <= dt.today()] 

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
                "payload":"Summary_expo*-/{}".format(r['ID'])
                }]      
            }
        )

    return cards

def get_exhib_query(exhib_ID_list, iteration):
    """ returns tuple: data of 5 exhibitions from the list of exhibition found by vect_search + cards to send """

    with open("backend/exhibition/data_exhibition.json", 'r') as f:
        data = json.load(f)
    
    #Appends exhibitions from the list, if it is still shown 
    exhibs = []
    for ID in exhib_ID_list:
        exhib = [ x for x in data if x['ID'] == int(ID) \
        and dt.strptime(x['d_end'], "%Y-%m-%d") >= dt.today() \
        and dt.strptime(x['d_start'], "%Y-%m-%d") <= dt.today()] 
        if exhib:
            exhibs.append(exhib[0])   


    #Results sorted by rank then ascending date of end , 
    per_date = sorted(exhibs[:20], key = itemgetter('d_end'))
    per_rank = sorted(per_date, key= itemgetter('rank'), reverse=True)[(iteration-1)*5 : iteration*5]

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
                "payload":"Summary_expo*-/{}".format(r['ID'])
                }]      
            }
        )

    return cards

def get_detail_exhib(ID):
    """ Returns the full info (dict) about the required exhibition """

    with open("backend/exhibition/data_exhibition.json", 'r') as f:
        data = json.load(f)

    return [ x for x in data if x['ID'] == int(ID)][0]

if __name__ == "__main__":    
    #---to test get genre function, uncomment the following line
    # print(get_genre()[0])

    
    #---to test get exhibition function, uncomment the following line
    #pprint(get_exhib('Photographie', 1))

    #---to test get exhibition per query function, uncomment the following line
    # the list corresponds to the sentence input "trouve moi une expo d'art moderne"
    pprint(get_exhib_query(['266', '193', '105', '251', '81', '221', '182', '174', '89', '249', '243', '137', '211', '51', '50', '297', '98', '127', '64', '264'], 1))
