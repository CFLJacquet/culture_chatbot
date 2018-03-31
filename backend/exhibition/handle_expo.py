import json
from operator import itemgetter
from datetime import datetime as dt
from pprint import pprint
import logging

def get_genre_exhib():
    """ Returns a tuple: list of exhibition genres + cards to be used in quick replies """

    # NB: les genres sont rangés par ordre de préférence, mais il n'y pas de mécanisme de retour 
    # utilisateur => besoin d'augmenter la valeur quand un utilisateur clique dessus + option: 
    # "plus de genres"

    with open("backend/exhibition/genre_popularity.json", 'r') as f:
        data = json.load(f)

    genre_to_sort = [(genre, rank) for genre, rank in data.items()]
    genre_to_sort.sort(key=lambda x:x[1], reverse=True)
    genre = [ g[0] for g in genre_to_sort ]

    btns = []
    for g in genre[:9]:                 #create button list to be sent
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

def get_exhib_query(exhib_ID_list, filter_exhib, iteration):
    """ returns tuple: data of 10 exhibitions from the list of exhibition found by vect_search + cards to send """

    with open("backend/exhibition/data_exhibition.json", 'r') as f:
        data = json.load(f)
    
    #Take out exhibs not on display anymore and Sort data based on ID_list
    data = [x for x in data if x['ID'] in exhib_ID_list]
    order_dict = {color: index for index, color in enumerate(exhib_ID_list)}
    data.sort(key=lambda x: order_dict[x["ID"]])

    #Retranslate categories
    for i, genre in enumerate(filter_exhib):
        filter_exhib[i] = filter_exhib[i]
        if genre in ['architecture', 'archi', 'batiment']:
            filter_exhib[i] = "Architecture"
        elif genre in ['histoire', 'civilisation', 'culture']:
            filter_exhib[i] = 'Histoire / Civilisations'
        elif genre in ['sculpture', 'design', 'artisanat','sculpteur']:
            filter_exhib[i] = 'Sculpture'
        elif genre in ['peinture','dessin','plastique','peintre','gravure']:
            filter_exhib[i] = 'Peinture'
        elif genre in ['musique','chanteur','rock','pop']:
            filter_exhib[i] = 'Musique'
        elif genre in ['littérature','auteur','livre']:
            filter_exhib[i] = 'Littérature'
        elif genre in ['danse','ballet', 'opéra']:
            filter_exhib[i] = 'Danse'
        elif genre in ['photographie', 'photographe','image']:
            filter_exhib[i] = 'Photographie'
        elif genre in ['mode','fashion']:
            filter_exhib[i] = 'Mode'
        elif genre in ['beaux-arts','classique','renaissance','flamand']:
            filter_exhib[i] = 'Beaux-Arts'
        elif genre in ['contemporain', 'moderne','abstrait']:
            filter_exhib[i] = 'Art contemporain'
        elif genre in ['famille']:
            filter_exhib[i] = 'Famille'
        else:
            filter_exhib[i] = filter_exhib[i].capitalize()

    if filter_exhib == ["All"]:
        filter_exhib = ['Architecture', 'Sculpture', 'Peinture', 'Musique', 'Littérature', 'Danse', 'Cinéma', 
    'Photographie', 'Mode', 'Beaux-Arts', 'Art contemporain', 'Histoire / Civilisations', 'Famille']
    
    # We display in total 10 exchibitions: we take the first 7 of the relevant categories, 
    # then 3 exhibs from other categories which got a good score
    exhibs = []
    temp = []
    #logging.info("clean genre expo: {}".format(filter_exhib))
    while len(exhibs)+len(temp)<10:
        for x in data:
            if dt.strptime(x['d_start'], "%Y-%m-%d") <= dt.today() and [1 for genre in filter_exhib if x[genre]==1] and len(exhibs)<7:
                exhibs.append(x)
            else:
                temp.append(x)
    exhibs += temp

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
    pprint(get_exhib_query(['266', '193', '105', '251', '81', '221', '182', '174', '89', '249', '243', '137', '211', '51', '50', '297', '98', '127', '64', '264'],"All", 1))
