# -*- coding: utf-8 -*-
# code found here: https://github.com/thomasRousseau/python-allocine-api


import sys
import hashlib
from base64 import b64encode
try: # python3
	from urllib.parse import urlencode
except: #python2
	from urllib import urlencode
import requests
import time
import json
import base64
import pathlib
from PIL import Image
from urllib.request import urlopen
from io import StringIO, BytesIO
from pprint import pprint # for a more readable json output
import os
#from flask import Flask, request
import logging

ALLOCINE_BASE_URL = "http://api.allocine.fr/rest/v3/"
ALLOCINE_PARTNER_KEY = '100043982026'
ALLOCINE_SECRET_KEY = '29d185d98c984a359e6e6f26a0474269'
ANDROID_USER_AGENT = 'Dalvik/1.6.0 (Linux; U; Android 4.2.2; Nexus 4 Build/JDQ39E)'



def do_request(method, params):
    sed = time.strftime("%Y%m%d")
    sha1 = hashlib.sha1()
    PARAMETER_STRING = "partner=" + ALLOCINE_PARTNER_KEY + "&" + "&".join([k + "=" + params[k] for k in params.keys()]) + "&sed=" + sed
    SIG_STRING = bytes(ALLOCINE_SECRET_KEY + PARAMETER_STRING, 'utf-8')
    sha1.update(SIG_STRING)
    SIG_SHA1 = sha1.digest()
    SIG_B64 = b64encode(SIG_SHA1).decode('utf-8')
    sig = urlencode({SIG_B64: ''})[:-1]
    URL = ALLOCINE_BASE_URL + method + "?" + PARAMETER_STRING + "&sig=" + sig
    headers = {'User-Agent': ANDROID_USER_AGENT}
    results = requests.get(URL, headers=headers).text
    try:
        return json.loads(results)
    except Exception as e:
        return results


# movielist : movie list in theater
#   code : person id (should be an integer)
#   count (optionnal) : number of results to return (should be an integer)
#   page (optionnal) : number of the results page to return (default is 10 results by page)
#   profile (optionnal) : information level to be returned ("small", "medium", "large")
#   filter (optionnal) : filter results by type ("nowshowing", "comingsoon", separated by a comma)
#   order (optionnal) : order to sort the results ("datedesc", "dateasc", "theatercount", "toprank")
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def movielist(code, count=None, page=None, profile=None, filter=None, order=None, format="json"):
    data = {"code": str(code), "format": format}
    if count is not None:
        data["count"] = str(count)
    if page is not None:
        data["page"] = page
    if profile is not None:
        data["profile"] = profile
    if filter is not None:
        data["filter"] = filter
    if order is not None:
        data["order"] = order
    return do_request("movielist", data)


def get_genre_allocine():
    
    last_release = movielist(0, count=100, page=None, profile="medium", filter="nowshowing", order="toprank", format="json")
    last_release=last_release["feed"]["movie"]

    all_films=[]
    for elt in last_release:
        for i in elt["genre"]:
            all_films.append(i['$'])
    print(set(all_films))

def stock_last_movies():

    last_release = movielist(0, count=50, page=None, profile="medium", filter="nowshowing", order="toprank", format="json")
    last_release=last_release["feed"]["movie"]

    all_films=[]
    for num, elt in enumerate(last_release):
        details_film = {}
        details_film["title"]=elt["title"]
        details_film["summary"] = elt["synopsisShort"].replace('<span>', '').replace('</span>', '').replace('<br/>', '').replace('\xa0', '') if "synopsisShort" in elt else "Résumé Indisponible"
        details_film["actors"]=elt["castingShort"]["actors"] if "castingShort" in elt and "actors" in elt["castingShort"] else ""
        details_film["directors"]=elt["castingShort"]["directors"] if "castingShort" in elt and "directors" in elt["castingShort"] else ""
        details_film["genre"] = []

        for i in elt["genre"]:
            if i['$'] in ['Policier', 'Action', 'Guerre', 'Aventure','Thriller', 'Western', 'Judiciaire'] and "Action" not in details_film["genre"]:
                details_film["genre"].append("Action")

            elif i['$'] == 'Sport event' :
                details_film["genre"].append('Sport') 
            elif i['$'] == 'Epouvante-horreur' :
                details_film["genre"].append('Horreur') 

            elif i['$'] in ['Erotique', 'Romance'] and "Romantique" not in details_film["genre"]:
                details_film["genre"].append('Romantique')

            elif i['$'] in ['Opera', 'Musical'] and "Musique" not in details_film["genre"]:
                details_film["genre"].append('Musique')

            elif i['$'] == 'Science fiction' and "Fantastique" not in details_film["genre"]:
                details_film["genre"].append('Fantastique') 

            elif i['$'] in ['Documentaire', 'Biopic'] and "Historique" not in details_film["genre"]:
                details_film["genre"].append('Historique')

            elif i['$'] == 'Comédie dramatique' and "Drame" not in details_film["genre"]:
                details_film["genre"].append('Drame')
            elif i['$'] == 'Comédie musicale' and "Comédie" not in details_film["genre"]:
                details_film["genre"].append("Comédie")
            elif i['$'] in ['Dessin animé'] and "Animation" not in details_film["genre"]:
                details_film["genre"].append("Animation")

            else :
                details_film["genre"].append(i["$"])

        details_film["movieType"]=elt["movieType"]["$"] if "movieType" in elt else ""
        details_film["rankTopMovie"]=elt['statistics']["rankTopMovie"] if 'statistics' in elt and "rankTopMovie" in elt['statistics'] else ""
        details_film["userRating"]=elt['statistics']["userRating"] if  'statistics' in elt and "userRating" in elt['statistics'] else 0
        details_film["pressRating"] = elt['statistics']["userRating"] if  'statistics' in elt and "userRating" in elt['statistics'] else 0
        details_film["film_url"]=elt["link"][0]["href"]
        details_film["img_url"]=elt["poster"]["href"] if "poster" in elt else "https://www.elegantthemes.com/blog/wp-content/uploads/2017/07/404-error.png"
        details_film["ID"] = "c" + str(num)
        all_films.append(details_film)

    with open("backend/cinema/allocine/cinema_allocine.json", 'w') as fichier: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        json.dump(all_films,fichier)


def fusion():
    with open("backend/cinema/allocine/cinema_allocine.json", 'r') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        allocine = json.load(f)

    scrapy = []
    with open('backend/cinema/senscritiquescrapping/extracted-data/critiques_films.jsonl') as f:
        for line in f:
            scrapy.append(json.loads(line))

    fichier_merged = []
    for i in range(0, len(allocine)):
        found = False
        for critique in scrapy:
            if allocine[i]["title"].lower() == critique["titre"].lower():
                temp = allocine[i]
                if int(critique["note_critique_1"]) < int(critique["note_critique_2"]):
                    temp["bad_critique"] = "Mauvaise note:"+critique["note_critique_1"]+"/10\n\n"+"Critique : "+critique["critique_1"]+"\n\n"+"Suite de la critique: "+critique["critique_1_url"]
                    temp["good_critique"] = "Bonne note:"+critique["note_critique_2"]+"/10\n\n"+"Critique : "+critique["critique_2"]+"\n\n"+ "Suite de la critique: "+critique["critique_2_url"]
                else:
                    temp["good_critique"] = "Bonne note:"+critique["note_critique_1"]+"/10\n\n"+"Critique : "+critique["critique_1"]+"\n\n"+"Suite de la critique: "+critique["critique_1_url"]
                    temp["bad_critique"] = "Mauvaise note:"+critique["note_critique_2"]+"/10\n\n"+"Critique : "+critique["critique_2"]+"\n\n"+ "Suite de la critique: "+critique["critique_2_url"]
                fichier_merged.append(temp)
                print("merged", allocine[i]["title"])
                found=True
        if found is False:
            fichier_merged.append(allocine[i])

    with open('backend/cinema/cinema_full.json', 'w') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        json.dump(fichier_merged, f)



def get_details_cinema():
    with open("backend/cinema/cinema_full.json") as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        data = json.load(f)

    results = sorted(data, key=lambda x: x["pressRating"], reverse=True)
    return results


def get_topmovies_genre(genre):
    """return the top movies filtered by the genre selected by the user of the chatbot"""

    with open("backend/cinema/cinema_full.json", 'r') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        data = json.load(f)

    results_genre = []
    for i in range(0, len(data)):
        film_genre = data[i]["genre"]
        #print(film_genre)
        if genre in film_genre:
            results_genre.append({
            "ID": data[i]["ID"],
            "title": data[i]["title"],
            "userRating": data[i]['userRating'],
            "pressRating": data[i]['pressRating'],
            "img_url": data[i]["img_url"],
            "film_url": data[i]["film_url"],
            "summary": data[i]["summary"],
            "genre": data[i]["genre"],
            "good_critique": data[i]["good_critique"] if "good_critique" in data[i] else "",
            "bad_critique": data[i]["bad_critique"] if "bad_critique" in data[i] else ""
            })
    results_genre = sorted(results_genre, key=lambda x: x["pressRating"], reverse=True)
    return results_genre

# def resize_image_from_url(url):
#
#     #Pour transformer les images il faut toujours utiliser PIL (pillow)
#     file = BytesIO(urlopen(url).read())
#     img = Image.open(file)
#     # On retraite l'image pour l'obtenir dans la bonne taille en préservant l'aspect ratio:
#     size = 128, 128
#     img.thumbnail(size)
#     # stockage temporaire de l'image en bytes
#     img.save('./cache/tmp.png', format="PNG")
#     # On transforme l'image en base 64 pour obtenir un url resized
#     print("test")
#     # On envoie le png en base 64 (ie sous forme de chaine de caractères)
#     return ""


#Liste des cinémas dans un rayon de 5km par rapport à notre géocalisation
#   radius : radius around the location (between 1 and 500 km)
#   theater : theater code (should be an integer)
#   location : string identifying the theater
#   format (optionnal) : returns the result in JSON or XML format ("json" or "xml", default set to JSON)
def theaterlist(zip=None, lat=48.84127721747719, long=2.339015007019043, radius=5, location=None, format="json"):
    data = {"format": format}
    if zip is not None:
        data["zip"] = str(zip)
    if lat is not None:
        data["lat"] = str(lat)
    if long is not None:
        data["long"] = str(long)
    if radius is not None:
        data["radius"] = str(radius)
    if location is not None:
        data["location"] = location
    return do_request("theaterlist", data)


def movies_around(latitude,longitude):

    results=[]
    data= theaterlist(zip=None, lat=latitude, long=longitude, radius=5, location=None, format="json")["feed"]["theater"]
    for i in range (0,len(data)):
        results.append({
            "name": data[i]["name"],
            "codepostal": data[i]["postalCode"],
            "adresse": data[i]["address"],
        })
    pprint(results)




def get_cine_query(cine_ID_list, filter_cine, iteration):
    """ returns tuple: data of 10 exhibitions from the list of exhibition found by vect_search + cards to send """

    filter_cine = [filter_cine] if isinstance(filter_cine, str) else filter_cine
    with open("backend/cinema/cinema_full.json") as f: 
        data = json.load(f)
    
    # Sort data based on ID_list given by vectorial search
    order_dict = {color: index for index, color in enumerate(cine_ID_list)}
    data.sort(key=lambda x: order_dict[x["ID"]])
    
    # Retranslate categories
    if filter_cine == ["All"]:
        clean_cat = ['Action', 'Animation', 'Biopic', 'Musique', 'Aventure', 'Comédie', 'Romantique', 'Fantastique', 'Drame', 'Historique', 'Horreur', 'Divers', 'Thriller', 'Famille']
    else: 
        clean_cat = []
        for filt in filter_cine:
            genre = filt.capitalize()
            if genre in ['Suspens', 'Suspense','Policier', 'Action', 'Guerre', 'Aventure','Thriller', 'Western', 'Judiciaire']:
                clean_cat.append("Action")
            elif genre in ['Sf','Science','Fiction','Fantastique', "Magie"]:
                clean_cat.append('Fantastique')
            elif genre in ['Rigolo', 'Amusant', 'Marrer', 'Comique', 'Fun','Comédie']:
                clean_cat.append("Comédie")
            elif genre in ['Documentaire','Biopic','Autobiographique']:
                clean_cat.append('Historique')
            elif genre in ['Amour','Romance',"Coeur"]:
                clean_cat.append("Romantique")
            elif genre in ['Peur','Epouvante','Horreur',"Flipper"]:
                clean_cat.append("Horreur")
            elif genre in ['Dessin', 'Animé','Animation',"Enfant"]:
                clean_cat.append("Animation")
            elif genre in ['Dramatique', 'Triste', 'Badant']:
                clean_cat.append('Drame')
            elif genre in ['Opera', 'Musique']:
                clean_cat.append("Musique")
            else:
                clean_cat.append(genre)

    # We display in total 10 movies: we take the first 7 of the relevant categories,
    # then 3 exhibs from other categories which got a good score
    cine = []
    temp = [] 
    while len(cine) + len(temp) < 10:
        for x in data:
            clean_cat = list(clean_cat) if len(clean_cat)==1 else clean_cat
            # print(set(clean_cat) & set(x["genre"]), "clean:", set(clean_cat),"data:", set(x["genre"]) )
            if set(clean_cat) & set(x["genre"]) and len(cine) < 7:
                cine.append(x)
            else:
                temp.append(x)
        cine += temp

    cards = []
    for i, r in enumerate(cine[:10]):
        etoile = u'\U0001F31F' * int(round(r['pressRating']))
        cards.append({
                "title": r['title'],
                "image_url": r['img_url'],
                "subtitle": "Note Presse : {}/5 \n Genre: {}".format(etoile, ', '.join(r['genre'])),
                "buttons":[
                    {
                    "type": "web_url",
                    "url": r['film_url'],
                    "title":"Voir sur Allociné"
                    },
                    {
                    "type":"postback",
                    "title":"Résumé",
                    # rajout du séparateur *-/, derrière il y a l'ID du film
                    "payload": "Summary_cine*-/{}".format(r["ID"])
                    },
                    {
                    "type": "postback",
                    "title": "Match des Critiques",
                    # rajout du séparateur *-/, derrière il y a l'ID du film
                    "payload": "Critiques_cine*-/{}".format(r["ID"])
                    }
                ]})

    return cards

if __name__ == '__main__':
    
    #--- To download the latest movies and fusion it with sens critique 
    # stock_last_movies()
    # fusion()

    #--- Other tests
    # print(get_details_cinema()[:5])
    # pprint(get_topmovies_genre("Action"))
    pprint(get_cine_query(['c5', 'c34', 'c35', 'c36', 'c37', 'c38', 'c1', 'c2', 'c3', 'c4', 'c0', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c12', 'c13', 'c14', 'c15', 'c16', 'c17', 'c18', 'c19', 'c20', 'c21', 'c22', 'c23', 'c24', 'c25', 'c26', 'c27', 'c28', 'c29', 'c30', 'c31', 'c32', 'c33', 'c39', 'c40', 'c41', 'c42', 'c43', 'c44', 'c45', 'c46', 'c47', 'c48', 'c49'], ["Action"],1))