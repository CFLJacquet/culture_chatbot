# -*- coding: utf-8 -*-

from flask import Flask, request, session
import traceback
# from flask_oauthlib.client import OAuth, OAuthException

import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import time
import datetime # to read datetime objects in exhibition data
from datetime import date as dt
import pickle

from backend.exhibition.handle_expo import get_genre_exhib, get_exhib, get_exhib_query, get_detail_exhib
from backend.messenger.msg_fct import user_details, typing_bubble, send_msg, send_button, send_card, send_quick_rep, start_buttons, art_buttons
from backend.cinema.handle_cinema import get_details_cinema, get_topmovies_genre
from backend.musees.handlesurprise import get_details_surprise, get_musee_surprise, get_categorie_surprise

from backend.language.handle_text import analyse_text
from backend.language.handle_text_query import vect_search
from backend.others.bdd_jokes import random_joke


# Real page access token:
# EAAHSfldMxYcBAAjHjAxYeZC1HOEYXurvr7sJ8No6vxoiScJkYd8r5TJ1WtpSNMEGByZBRZCgsV9jwxp2LgfFZAiddVk0KX2nryb7Hy68CTKLYzTAPBgEj0B1FP20eXaYWuZCeSDx2QJYtt8QOZBXhqI8ZADwv2MZBoR1P4NUkMKUaQZDZD

# TestJ access token: 
# EAACQPdicZCwQBAJAkOaE8Na9V0aHSV0mNdQvYrXcySeLtPVffB10NGk4EkwiZBy7qdDWUwz8jKdLN4vOIu14HK6DKoGMBO3X0vyVy1Y0EDqzEV6QK0h1PZCxTTtaklO7NqdqrY9UCjtxUR2uEYdNWBh4cDhLLaBcXgNAhNrXgZDZD
ACCESS_TOKEN = "EAAHSfldMxYcBAAjHjAxYeZC1HOEYXurvr7sJ8No6vxoiScJkYd8r5TJ1WtpSNMEGByZBRZCgsV9jwxp2LgfFZAiddVk0KX2nryb7Hy68CTKLYzTAPBgEj0B1FP20eXaYWuZCeSDx2QJYtt8QOZBXhqI8ZADwv2MZBoR1P4NUkMKUaQZDZD"


# Flask config
# SQLALCHEMY_DATABASE_URI = 'sqlite:///facebook.db'
# SECRET_KEY = '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
# DEBUG = True

# FACEBOOK_APP_ID = '1211518415646800'
# FACEBOOK_APP_SECRET = '9ab82022f2a95642265a4cc195074ab6'

app = Flask(__name__)
# app.debug = True
# app.secret_key = 'development'
# oauth = OAuth(app)

# facebook = oauth.remote_app(
#     'facebook',
#     consumer_key=FACEBOOK_APP_ID,
#     consumer_secret=FACEBOOK_APP_SECRET,
#     request_token_params={'scope': 'email'},
#     base_url='https://graph.facebook.com',
#     request_token_url=None,
#     access_token_url='/oauth/access_token',
#     access_token_method='GET',
#     authorize_url='https://www.facebook.com/dialog/oauth'
# )

#Bloc creant des logs
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler("activity.log", 'w', 1000000, 1) #/Users/constanceleonard/Desktop/projet_osy/strolling/log/
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# @facebook.tokengetter
# def get_facebook_oauth_token():
#     return session.get('access_token')

@app.route('/test')
def test():
    return "<h1> Le serveur fonctionne correctement !</h1>"

# @app.route('/facebook/authorized')
# def authorized():
#     # check to make sure the user authorized the request
#     if not 'code' in request.args:
#         flash('You did not authorize the request')
#         return redirect(url_for('index'))

#     # make a request for the access token credentials using code
#     redirect_uri = url_for('authorized', _external=True)
#     data = dict(code=request.args['code'], redirect_uri=redirect_uri)

#     session = facebook.get_auth_session(data=data)

#     # the "me" response
#     me = session.get('me').json()

#     User.get_or_create(me['username'], me['id'])

#     flash('Logged in as ' + me['name'])
#     return redirect(url_for('index'))

@app.route('/', methods=['GET'])
def handle_verification():
    logging.info(request.args['hub.challenge'])
    return request.args['hub.challenge']


@app.route('/', methods=['POST'])
def handle_event():
    #NB: la requête API est effectuée à chaque msg entrant
    data = request.json

    # Verifie que c'est la 1e fois que le message est recu => empeche spam
    # with open("backend/others/msg_spam.json", "r") as f:
    #     msg_spam = json.load(f) 

    # if data['entry'][0]['time'] in msg_spam:
    #     return ""
    logging.info("DATA: {}".format(data))

    event = data['entry'][0]['messaging'][0]

    #Log user details in the database
    sender = event['sender']['id']
    user = user_details(sender, ACCESS_TOKEN)

    typing_bubble(sender, ACCESS_TOKEN)

    if "message" in event:
        #handles quick replies (buttons at the bottom of the conversation)     
        if 'quick_reply' in event['message'] :
            payload = event['message']['quick_reply']['payload']
        
        # Gestion du cas cinema
            if payload[:12] == "sorties_cine":
                latest = get_details_cinema()
                num = int(event['message']['quick_reply']['payload'].split("-")[1])
                #on affiche les cartes des films
                film_display(num, sender, latest)
            elif payload[:12] == "cine_around":
                send_location(sender)
                send_msg(sender," ", ACCESS_TOKEN)
            elif "genres_cine" in event['message']['quick_reply']['payload']:
                send_msg(sender, "Quel genre t'intéresse?", ACCESS_TOKEN)
                btns = get_genre_movie(sender)[1]
                send_quick_rep(sender, "Voici les genres possibles: ", btns , ACCESS_TOKEN)

                #boucle pour récupérer le genre du film:
            elif event['message']['quick_reply']['payload'] in [ genre for genre in get_genre_movie(sender)[2] if genre != "Not_interested" ]:
                #on récupère le genre du film pour obtenir une liste des derniers films sortis mais filtrée par le genre
                p = event['message']['quick_reply']['payload'][:-2]
                ranking= get_topmovies_genre(p)
                #on affiche les cartes des films triés par genre
                film_display_bygenre(sender, p)
            
        # Gestion des cas sur l'art
            elif payload[:3] == "art":
                art_buttons(sender, "Clique sur ce qui t'intéresse",ACCESS_TOKEN)

        # Si l'utilisateur veut une surprise
            elif payload == "surprise-0":
                get_categorie_surprise(sender, "Voila les catégories disponibles !", ACCESS_TOKEN)
            elif payload[:12] == "surprise_cat":
                category = payload.split("*-/")[1]
                get_musee_surprise(sender, category, ACCESS_TOKEN)

        # Si l'utilisateur veut une expo
            elif payload[:10] == "exhibition":
                num = int(payload[-1])
                exhibition_display(num, sender)
            elif payload[:-2] in get_genre_exhib()[0]:
                num = int(payload[-1])
                exhibition_display(num, sender, payload)      
            
            elif payload == "Not_interested":
                send_msg(sender, "Je suis en train d'apprendre de nouvelles choses, mais pour l'instant je ne peux que te conseiller en cinéma et en expo ! Pour la peine, voici une dadjoke de consolation:", ACCESS_TOKEN)
                send_msg(sender, random_joke(), ACCESS_TOKEN)                
                send_msg(sender, "A bientôt !", ACCESS_TOKEN)

            elif payload == "Thanks":
                send_msg(sender, "Ravie d'avoir pu t'aider ! A bientôt :)", ACCESS_TOKEN)
        
        #handles stickers sent by user. For the moment, only the like button is recognized
        elif 'sticker_id' in event['message'] :
            sticker = event['message']['sticker_id']
            if int(sticker) == 369239263222822 :        # Like button sticker
                send_msg(sender, "De rien ! ;)", ACCESS_TOKEN)
            else:
                send_msg(sender, "Nice sticker {} !".format(user[1]), ACCESS_TOKEN)

        #handles attachments (images, selfies, docs...)
        elif 'attachments' in event['message'] :
            attachments = event['message']['attachments'][0]
            if attachments['type'] == 'image':
                if ".gif" in attachments['payload']['url']:
                    send_msg(sender, "Super GIF !", ACCESS_TOKEN)
                else: 
                    send_msg(sender, "Jolie image :)", ACCESS_TOKEN)
            else: 
                send_msg(sender, "J'ai bien reçu ton fichier, mais pour l'instant je ne peux pas le traiter !", ACCESS_TOKEN)

        #handles text sent by user (including unicode emojis 😰, 😀)
        else:
            message = event['message']['text'].lower()
            analyse_text(message, sender, user, ACCESS_TOKEN)

    elif "postback" in event:
        if event['postback']['payload'] == "first_conv":
            welcome(sender, user)

        elif "Summary_cine" in event['postback']['payload'] :
            ID = event['postback']['payload'].split("*-/")[1]
            latest = get_details_cinema()
            result = [ x for x in latest if x["ID"] == ID][0]
            send_msg(sender, "-- "+result['title']+" -- Résumé -- \n\n"+result['summary'], ACCESS_TOKEN)
            time.sleep(4)
            start_buttons(sender, "Autre chose ?", ACCESS_TOKEN)

        elif "Critiques_cine" in event['postback']['payload'] :
            ID = event['postback']['payload'].split("*-/")[1]
            latest = get_details_cinema()
            result = [x for x in latest if x["ID"] == ID][0]
            if "good_critique" in result:
                send_msg(sender, "-- " + result['title'] + " -- Critiques -- \n\n" + result['good_critique'], ACCESS_TOKEN)
                send_msg(sender, result['bad_critique'], ACCESS_TOKEN)
            else : 
                send_msg(sender, "Je n'ai malheureusement pas trouvé de critiques", ACCESS_TOKEN)
            time.sleep(8)
            start_buttons(sender, "Autre chose ?", ACCESS_TOKEN)

        elif "surprise" in event['postback']['payload'] :
            action, ID = event['postback']['payload'].split("*-/")
            info = get_details_surprise(ID, action)
            send_msg(sender, info, ACCESS_TOKEN)


        elif event['postback']['payload'][:12] == "Summary_expo":
            x = event['postback']['payload'].split("*-/") 
            
            # x[0]: 'Summary_expo' / x[1]: exhib_ID
            data = get_detail_exhib(x[1])
            
            send_msg(sender, "Description: "+data['summary'], ACCESS_TOKEN)
            send_msg(sender, "Horaires: "+data['timetable'], ACCESS_TOKEN)
            send_msg(sender, "Prix: "+data['price'], ACCESS_TOKEN)
        
    else: 
        send_msg(sender, "Je n'ai pas compris ta demande... 😰", ACCESS_TOKEN)
        
    return "ok"

def welcome(sender, user):
    time.sleep(1)
    answer="Salut {}, je suis Electre ! Je connais les meilleurs films et expos de Paris.\n\
A tout moment tu peux me demander des choses comme \'Est ce qu'il y a des expos d'art moderne ?\' ou \
\'donne moi le meilleur film comique au ciné\'\n\n\
Si tu préfères être guidé, tape 'menu' et des boutons apparaîtront !".format(user[1])
    send_msg(sender, answer, ACCESS_TOKEN)
    
    start_buttons(sender, "Qu'est-ce qui t'intéresserait ?",ACCESS_TOKEN)



def film_display(num, sender, latest):
    """ returns cards with films from the "latest" var (extracted with API) """

    time.sleep(1)
    if num == 0 :
        send_msg(sender,'Voici les meilleurs films en salle', ACCESS_TOKEN)

    cards=[]
    for i in range (num, num+9):
        etoile = u'\U0001F31F' * int(round(latest[i]['pressRating']))
        cards.append(
            {
            "title": latest[i]['title'],
            "image_url": latest[i]['img_url'],
            "subtitle":"Note Presse : {}/5 \n Genre: {}".format(etoile, ', '.join(latest[i]['genre'])),
            "buttons":[{
                "type": "web_url",
                "url": latest[i]['film_url'],
                "title":"Voir sur Allociné"
                },
                {
                "type":"postback",
                "title":"Résumé",
                # rajout du séparateur *-/, derrière il y a l'ID du film
                "payload": "Summary_cine*-/{}".format(latest[i]["ID"])
                },
                {
                "type": "postback",
                "title": "Match des Critiques",
                # rajout du séparateur *-/, derrière il y a l'ID du film
                "payload": "Critiques_cine*-/{}".format(latest[i]["ID"])
                }]
            }
        )
    send_card(sender,cards, ACCESS_TOKEN)
    btns =[
        {
            "content_type":"text",
            "title":"Plus de films",
            "payload":"sorties_cine-10"
        },
        {
            "content_type": "text",
            "title": "Choisir un genre",
            "payload": "genres_cine"
        },
        {
            "content_type":"text",
            "title":"Merci Electre",
            "payload":"Thanks"
        }
    ]
    if num == 0:
        time.sleep(4)
        send_quick_rep(sender, "Tu veux voir d'autres films ? Ou plutôt voir un genre de film particulier ?", btns ,ACCESS_TOKEN)

def get_genre_movie(sender):
    """ returns : genre, btns, list_payload"""

    with open("backend/cinema/cinema_full.json", 'r') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        data = json.load(f)

    genre = []
    for elt in data:
        genre += elt['genre']
    no_duplicates = list(set(genre))
    genre = sorted(no_duplicates)[:10]  # genre list without duplicates

    btns = []
    i=0
    for g in genre:  # create button list to be sent
        btns.append(
                {
                    "content_type": "text",
                    "title": g,
                    "payload": g+"-"+str(i)
                })
        i += 1
    btns.append(
            {
                "content_type": "text",
                "title": "Aucun de ces genres",
                "payload": "Not_interested"
            })

    list_payload=[]
    for i in range(0, len(btns)):
        list_payload.append(btns[i]['payload'])

    return genre, btns, list_payload


def film_display_bygenre(sender, genre):

        send_msg(sender, "Voici donc les meilleurs films pour le genre sélectionné ! ", ACCESS_TOKEN)

        movies_filtered= get_topmovies_genre(genre)

        cards=[]
        for i in range(10):
            etoile = u'\U0001F31F' * int(round(movies_filtered[i]['pressRating']))
            cards.append(
                {
                    "title": movies_filtered[i]['title'],
                    "image_url": movies_filtered[i]['img_url'],
                    "subtitle": "Note Presse : {}/5 ".format(etoile),
                    "buttons": [{
                        "type": "web_url",
                        "url": movies_filtered[i]['film_url'],
                        "title": "Voir sur Allociné"
                    },
                        {
                            "type": "postback",
                            "title": "Résumé",
                            # rajout du séparateur *-/, derrière il y a l'ID du film
                            "payload": "Summary_cine*-/{}".format(movies_filtered[i]["ID"])
                        },
                        {
                            "type": "postback",
                            "title": "Match des Critiques",
                            # rajout du séparateur *-/, derrière il y a l'ID du film
                            "payload": "Critiques_cine*-/{}".format(movies_filtered[i]["ID"])
                        }]
                }
            )
        send_card(sender, cards, ACCESS_TOKEN)
        send_msg(sender, "Si tu veux voir un autre film ou une expo, n'hésite pas !", ACCESS_TOKEN)


def send_location(sender):
    send_msg(sender, "Pourriez-vous nous indiquer votre position en cliquant sur le bouton ci-dessous? ", ACCESS_TOKEN)
    btns = [
        {
            "content_type": "location",
            "title": "Je me géocalise",
            "payload": "bouton_geocalisation"
        }
    ]
    send_quick_rep(sender, "Merci beaucoup nous allons trouver les films qui se situent autour de vous!", btns,
                   ACCESS_TOKEN)


def exhibition_display(num, sender, payload =""):
    time.sleep(1)
    if num == 0 :
        msg = "Il y a plusieurs types d'expositions, qu'est-ce qui t'intéresse le plus ?"
        
        btns_genre = get_genre_exhib()[1]
        send_quick_rep(sender, msg, btns_genre, ACCESS_TOKEN)

    elif num in range(1,4):
        cards = get_exhib(payload[:-2], int(payload[-1]))
        send_card(sender, cards, ACCESS_TOKEN)
        
        btns =[
            {
                "content_type":"text",
                "title":"Voir plus d'expos",
                "payload":"{}-{}".format(payload[:-2], int(payload[-1]) + 1)
            },
            {
                "content_type":"text",
                "title":"Un autre genre",
                "payload":"exhibition-0"
            },
            {
                "content_type":"text",
                "title":"Merci Electre",
                "payload":"Thanks"
            }
        ]
        send_quick_rep(sender, "Veux-tu voir d'autres expos ?", btns ,ACCESS_TOKEN)

@app.errorhandler(500)
def internal_error(exception):
    """ Used to log internel errors & the return "200" prevent the bot from spamming """
    logging.error(traceback.format_exc())
    return "200"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
