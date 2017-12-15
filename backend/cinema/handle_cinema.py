# -*- coding: utf-8 -*-
# code found here: https://github.com/thomasRousseau/python-allocine-api

import pickle
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
import pathlib
from pprint import pprint # for a more readable json output
from flask import Flask, request
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
    last_release = movielist(0, count=9, page=None, profile="medium", filter="nowshowing", order="toprank", format="json")
    last_release=last_release["feed"]["movie"]
    print(last_release)

    #changer le path (avec backend etc.. comme handle_expo) avant de faire tourner le serveur
    with open("cinema_allocine", 'wb') as fichier:
        allocine_pickle = pickle.Pickler(fichier)
        allocine_pickle.dump(last_release)


def get_details():

    with open("cinema_allocine", 'rb') as f:
        d = pickle.Unpickler(f)
        data = d.load()

    results = []
    for i in range(0, len(data)):
        genres = []
        for item in data[i]["genre"]:
            genres.append(item['$'])
        results.append({
            "title": data[i]["title"],
            "notespectateur": data[i]["statistics"].get('userRating', -1),
            "notepresse": data[i]["statistics"].get('pressRating', -1),
            "img_url": data[i]["poster"]["href"],
            "url": data[i]["link"][0]["href"],
            "summary": data[i].get('synopsisShort', '').replace('<span>', '').replace('</span>', '').replace(
                '<br/>', '').replace('\xa0', ''),
            "genre": genres
        })
    results = sorted(results, key=lambda x: x["notepresse"], reverse=True)
    return results


def get_genre():
    """ Returns a tuple: list of exhibition genres + cards to be used in quck replies """

    with open("cinema_allocine", 'rb') as f:
        d = pickle.Unpickler(f)
        data = d.load()
        pprint(data)

    genre = []
    for i in range(0, len(data)):
        sous_genres = []
        for item in data[i]["genre"]:
            sous_genres.append(item['$'])
        genre.extend(sous_genres)
        no_duplicates = list(set(genre))
        genre = sorted(no_duplicates)  # genre list without duplicates
        print(type(genre))

        btns = []
        for g in genre:  # create button list to be sent
            btns.append(
                {
                    "content_type": "text",
                    "title": g,
                    "payload": g + "-1"
                })
        btns.append(
            {
                "content_type": "text",
                "title": "Aucun de ces genres",
                "payload": "Not_interested"
            })

        return genre, btns


#faire deux if (un par genre et un pour gérer les cartes comme à partir de la ligne 64 de serveur), essayer de garder dans le serveur tout ce qui permet de récupérer le genre et de faire apparaître ce que l'on veut mais de définir la fonction qui permet d'obtenir le top film par genre dans handle cinema:
def topmovies_bygenre():

    with open("cinema_allocine", 'rb') as f:
        d = pickle.Unpickler(f)
        data = d.load()

    #extraire les ranktopmovie par ordre descendant et prendre les cinq premiers


if __name__ == '__main__':
    print(sys.stdout.encoding)
    print(get_genre())