# -*- coding: utf-8 -*-
# code found here: https://github.com/thomasRousseau/python-allocine-api


from backend.cinema.transform_json import critique_movie
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


def stock_last_movies():

    # ATTENTION - count parameter not working, len(last_release)=100 movies ! => filtering in return
    last_release = movielist(0, count=50, page=None, profile="medium", filter="nowshowing", order="toprank", format="json")
    last_release=last_release["feed"]["movie"]

    all_films=[]
    for num, elt in enumerate(last_release):
        print("ok")
        pprint(elt)
        details_film = {}
        details_film["title"]=elt["title"]
        details_film["summary"]=elt["synopsisShort"]
        if "actors" in elt["castingShort"]:
            details_film["actors"]=elt["castingShort"]["actors"]
        else:
            details_film["actors"]=""
        details_film["directors"]=elt["castingShort"]["directors"]
        details_film["genre"] = []
        for i in elt["genre"]:
            if i['$'] in ["Thriller", 'Aventure','Policier','Suspens']:
                details_film["genre"].append("Action")
            elif i['$'] == 'Science fiction':
                details_film["genre"].append('Fantastique')
            elif i['$'] in ["Guerre", 'Biopic']:
                details_film["genre"].append('Historique')
            elif i['$'] == 'Comédie dramatique' :
                details_film["genre"].append('Drame')
            elif i['$'] in ['Comédie musicale', "Dessin animé"]:
                details_film["genre"].append("Comédie")
            else :
                details_film["genre"].append(i["$"])

        details_film["movieType"]=elt["movieType"]["$"]
        details_film["rankTopMovie"]=elt['statistics']["rankTopMovie"]
        details_film["userRating"]=elt['statistics']["userRating"]
        details_film["pressRating"] = elt['statistics']["userRating"]
        details_film["film_url"]=elt["link"][0]["href"]
        details_film["img_url"]=elt["poster"]["href"]
        details_film["ID"] = "c" + str(num)
        all_films.append(details_film)

    #changer le path (avec backend etc.. comme handle_expo) avant de faire tourner le serveur

    with open("/Users/constanceleonard/Desktop/strolling/backend/cinema/cinema_allocine.json", 'w') as fichier: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        json.dump(all_films,fichier)


def get_details_cinema():
    #print(os.getcwd())
    with open("/Users/constanceleonard/Desktop/strolling/backend/cinema/cinema_allocine.json") as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        data = json.load(f)

    results = []
    for i in range(0, len(data)):
        genres = []
        for item in data[i]["genre"]:
            genres.append(item['$'])
        results.append({
            "allocine_ID": data[i]["ID"],
            "title": data[i]["title"],
            "notespectateur": data[i].get('userRating', -1),
            "notepresse": data[i].get('pressRating', -1),
            "img_url": data[i]["img_url"],
            "url": data[i]["film_url"],
            "summary": data[i].get('summary', '').replace('<span>', '').replace('</span>', '').replace(
                '<br/>', '').replace('\xa0', ''),
            "genre": genres,
            "critique1": "Note 1: "+data[i]["note_critique_1"]+"\n\n"+"Critique 1: "+data[i]["critique_1"]+"\n\n"+"Lien critique 1: "+data[i]["critique_1_url"],
            "critique2": "Note 2: "+data[i]["note_critique_2"]+"\n\n"+"Critique 2: "+data[i]["critique_2"]+"\n\n"++ "Lien critique 2: "+data[i]["critique_2_url"]
        })
    results = sorted(results, key=lambda x: x["notepresse"], reverse=True)
    return results


def get_topmovies_genre(genre):
    #return the top movies filtered by the genre selected by the user of the chatbot:

    with open("/Users/constanceleonard/Desktop/strolling/backend/cinema/cinema_full.json", 'r') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        data = json.load(f)
        #pprint(data)

    results_genre = []
    for i in range(0, len(data)):
        genre_informations = data[i]["genre"]
        #print(genre_informations)
        film_genre=[x["$"] for x in genre_informations]
        #print(film_genre)
        if genre in film_genre:
            results_genre.append({
            "ID": data[i]["ID"],
            "title": data[i]["title"],
            "notespectateur": data[i].get('userRating', -1),
            "notepresse": data[i].get('pressRating', -1),
            "img_url": data[i]["img_url"],
            "url": data[i]["film_url"],
            "summary": data[i].get('summary', '').replace('<span>', '').replace('</span>', '').replace(
                '<br/>', '').replace('\xa0', ''),
            "critique1": "Note 1: "+data[i]["note_critique_1"]+"\n\n"+"Critique 1: "+data[i]["critique_1"]+"\n\n"+"Lien critique 1: "+data[i]["critique_1_url"],
            "critique2": "Note 2: "+data[i]["note_critique_2"]+"\n\n"+"Critique 2: "+data[i]["critique_2"]+"\n\n"++ "Lien critique 2: "+data[i]["critique_2_url"]
        })
    results_genre = sorted(results_genre, key=lambda x: x["notepresse"], reverse=True)
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

def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def fusion():
    with open("/Users/constanceleonard/Desktop/strolling/backend/cinema/cinema_allocine.json", 'r') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        allocine = json.load(f)

    scrapy = []
    with open('/Users/constanceleonard/Desktop/strolling/backend/cinema/senscritiquescrapping/extracted-data/critiques_films.jsonl') as f:
        for line in f:
            scrapy.append(json.loads(line))

    fichier_merged = []
    for i in range(0, len(allocine)):
        found = False
        for critique in scrapy:
            if allocine[i]["title"].lower() == critique["titre"].lower():
                fichier_merged.append(merge_two_dicts(allocine[i], critique))
                print("merged", allocine[i]["title"])
                found=True
        if found is False:
            fichier_merged.append(allocine[i])


    with open('/Users/constanceleonard/Desktop/strolling/backend/cinema/cinema_full.json', 'w') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        json.dump(fichier_merged, f)


def get_cine_query(cine_ID_list, filter_cine, iteration):
    """ returns tuple: data of 10 exhibitions from the list of exhibition found by vect_search + cards to send """

    with open("/Users/constanceleonard/Desktop/strolling/backend/cinema/cinema_full.json", 'r') as f:
        data = json.load(f)

    # Retranslate categories
    for i, genre in enumerate(filter_cine):
        filter_cine[i] = filter_cine[i].capitalize()
        if genre in ["Thriller", "Aventure",'Policier','Suspens']:
            filter_cine[i] = "Action"
        elif genre == 'Science fiction':
            filter_cine[i] = 'Fantastique'
        elif genre in ["Guerre", 'Biopic']:
            filter_cine[i] = 'Historique'
        elif genre == 'Comédie dramatique':
            filter_cine[i] = 'Drame'
        elif genre in ['Comédie musicale',"Dessin animé"]:
            filter_cine[i] = "Comédie"

    if filter_cine == ["All"]:
        filter_cine = ('Romance','Fantastique','Opera','Documentaire','Famille','Comédie','Epouvante','Horreur','Policier','Action','Divers','Dessin animé','Animation','Drame','Historique','Western','Suspens')

    # We display in total 10 exhibitions: we take the first 7 of the relevant categories,
    # then 3 exhibs from other categories which got a good score
    cine = []
    temp = []
    while len(cine) + len(temp) < 10:
        for x in data:
            if [1 for genre in filter_cine if x[genre] == 1] and len(cine) < 7:
                cine.append(x)
            else:
                temp.append(x)
        cine += temp

    cards = []
    for i, r in enumerate(cine[:10]):
        cards.append(
            {
                "title": r['title'],
                "image_url": r['img_url'],
                "subtitle": r['location'] + "\nJusqu'au " + dt.strptime(r['d_end'], "%Y-%m-%d").strftime('%d/%m'),
                "buttons": [{
                    "type": "web_url",
                    "url": "https://www.google.fr/maps/search/" + r['location'],
                    "title": "C'est où ?"
                },
                    {
                        "type": "postback",
                        "title": "C'est quoi ?",
                        "payload": "Summary_expo*-/{}".format(r['ID'])
                    }]
            }
        )

    return cards

if __name__ == '__main__':
    #print(sys.stdout.encoding)
    stock_last_movies()
    #fusion()
 #   with open("/Users/constanceleonard/Desktop/strolling/backend/cinema/cinema_allocine.json", 'r') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
 #       allocine = json.load(f)

#    pprint(allocine)
