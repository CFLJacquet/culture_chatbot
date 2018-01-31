from flask import Flask, request, session
# from flask_oauthlib.client import OAuth, OAuthException

import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import time
import datetime # to read datetime objects in exhibition data
import pickle

from backend.cinema.handle_cinema import get_details, get_topmovies_genre
#resize_image_from_url
from backend.messenger.msg_fct import user_details, send_msg, send_button, send_card, send_quick_rep
from backend.exhibition.handle_expo import get_genre_exhib, get_exhib
from backend.others.bdd_jokes import random_joke


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

#Bloc créant des logs
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler("activity.log", 'w', 1000000, 1) #/Users/constanceleonard/Desktop/projet_osy/strolling/log/
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


ACCESS_TOKEN = "EAARN3pzNsFABAC3PnSWAHNhmjzBM02dHNgOGw2jTJaCdQId2AcgEC4LvPTnIANNzaPyHOJDVc9ZCu4pIpgJflfnyRjG0i3kaClxGTn9LA3Oa9XbHg02z3qIULOsUZBgqMeigjWwgzbQ6OmoxtE5JyRJStiFD6REZCen9JZBILgZDZD"


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
    logging.info("DATA: {}".format(data))

    event = data['entry'][0]['messaging'][0]

    latest = get_details()
    logging.info('LATEST FILMS :'+str(latest))

    sender = event['sender']['id']
    user = user_details(sender, ACCESS_TOKEN)

    if "message" in event:
        message = event['message']['text'].lower()
        print(event['message'])
        if not 'quick_reply' in event['message']:
            welcome(sender, user)

        else:
            if event['message']['quick_reply']['payload'][:12] == "sorties_cine":
                num = int(event['message']['quick_reply']['payload'][-1])
                film_display(num, sender, latest)
                send_msg(sender, " ", ACCESS_TOKEN)
            elif event['message']['quick_reply']['payload'][:12] == "genres_cine":
                send_msg(sender, "Quel genre vous intéresse?", ACCESS_TOKEN)
                get_genre_movie(sender)
                send_msg(sender, " ", ACCESS_TOKEN)
                #intégrer NLP dialogflow:
                #boucle pour récupérer le genre du film:
            elif event['message']['quick_reply']['payload'] in get_genre_movie(sender)[2]:
                #on récupère le genre du film pour obtenir une liste des derniers films sortis mais filtrée par le genre
                p = event['message']['quick_reply']['payload'][0:-2]
                print(p)
                ranking= get_topmovies_genre(p)
                print(ranking)
                film_display_genre(sender, p)
                send_msg(sender, " ", ACCESS_TOKEN)
            elif event['message']['quick_reply']['payload'][:10] == "exhibition":
                num = int(event['message']['quick_reply']['payload'][-1])
                exhibition_display(num, sender)
            #boucle pour récupérer le genre de l'exposition:
            elif event['message']['quick_reply']['payload'] in get_genre_exhib()[1]:
                p = event['message']['quick_reply']['payload']
                num = int(p[-1])
                exhibition_display(num, sender, p)

            elif event['message']['quick_reply']['payload'] == "Not_interested":
                send_msg(sender, "Dommage... Voici une dadjoke de consolation:", ACCESS_TOKEN)
                send_msg(sender, random_joke(), ACCESS_TOKEN)
                send_msg(sender, "A bientôt !", ACCESS_TOKEN)

            elif event['message']['quick_reply']['payload'] == "Thanks":
                send_msg(sender, "Ravie d'avoir pu vous aider ! A bientôt :)", ACCESS_TOKEN)

            else :
                send_msg(sender, "Et si vous me disiez bonjour ?", ACCESS_TOKEN)

    if "postback" in event:
        if event['postback']['payload'] == "first_conv":
            welcome(sender, user)

        elif event['postback']['payload'][:12] == "Summary_cine":
            logging.info("in summury_ciné")
            i = int(event['postback']['payload'][-1])
            send_msg(sender, "-- "+latest[i]['title']+" -- Résumé -- \n\n"+latest[i]['summary'], ACCESS_TOKEN)

        elif event['postback']['payload'][:12] == "Summary_expo":
            x = event['postback']['payload'].split("*-/")

            # x[0]: 'Summary_expo' / x[1]: genre / x[2]: card n° / x[3]: iteration
            data = get_exhib(x[1], int(x[3]))[0][int(x[2])]

            send_msg(sender, "Description: "+data['summary'], ACCESS_TOKEN)
            time.sleep(10)
            send_msg(sender, "Horaires: "+data['prog'], ACCESS_TOKEN)
            time.sleep(2)
            send_msg(sender, "Prix: "+data['price'], ACCESS_TOKEN)


    return "ok"


def welcome(sender, user):
    answer="Bonjour {} {} {}, je suis Electre, je vais vous trouver le \
            divertissement qui vous plaira.".format(user[0],user[1],user[2])
    send_msg(sender, answer, ACCESS_TOKEN)
    btns =[
        {
            "content_type":"text",
            "title":"Cinéma",
            "payload":"sorties_cine-0"
        },
        {
            "content_type":"text",
            "title":"Exposition",
            "payload":"exhibition-0"
        },
        {
            "content_type":"text",
            "title":"Rien de tout ça",
            "payload":"Not_interested"
        }
    ]
    send_quick_rep(sender, "Qu'est ce qui vous intéresserait ?", btns ,ACCESS_TOKEN)


def film_display(num, sender, latest):
    """ returns cards with films from the "latest" var (extracted with API) """

    if num == 0 :
        send_msg(sender,'Voici les meilleurs films en salle', ACCESS_TOKEN)

    cards=[]
    for i in range (num, num+3):
        etoile = u'\U0001F31F' * int(round(latest[i]['notepresse']))
        cards.append(
            {
            "title": latest[i]['title'],
            "image_url": latest[i]['img_url'],
            "subtitle":"Note Presse : {}/5 \n Genre: {}".format(etoile, ', '.join(latest[i]['genre'])),
            "buttons":[{
                "type": "web_url",
                "url": latest[i]['url'],
                "title":"Voir sur Allociné"
                },
                {
                "type":"postback",
                "title":"Résumé",
                "payload":"Summary_cine-{}".format(i)
                }]      
            }
        )
    send_card(sender,cards, ACCESS_TOKEN)
    btns =[
        {
            "content_type":"text",
            "title":"Plus de films !",
            "payload":"sorties_cine-3"
        },
        {
            "content_type": "text",
            "title": "Choisir un genre !",
            "payload": "genres_cine"
        },
        {
            "content_type":"text",
            "title":"Merci Iris",
            "payload":"Thanks"
        }
    ]
    if num == 0:
        send_quick_rep(sender, "Voulez-vous voir d'autres films ? Ou souhaitez-vous voir un genre de film particulier?", btns ,ACCESS_TOKEN)

def get_genre_movie(sender):

    with open("backend/cinema/cinema_allocine", 'rb') as f: #/Users/constanceleonard/Desktop/projet_osy/strolling/
        d = pickle.Unpickler(f)
        data = d.load()

    genre = []
    for i in range(0, len(data)):
        sous_genres = []
        for item in data[i]["genre"]:
            sous_genres.append(item['$'])
        genre.extend(sous_genres)
        no_duplicates = list(set(genre))
        genre = sorted(no_duplicates)  # genre list without duplicates
        genre = [x for x in genre if x not in ['Comédie dramatique', 'Fantastique', 'Aventure']]

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

    send_quick_rep(sender, "Voici les genres possibles: ", btns , ACCESS_TOKEN)

    return genre, btns, list_payload


def film_display_genre(sender, genre):

        send_msg(sender, "Voici donc les meilleurs films pour le genre sélectionné ! ", ACCESS_TOKEN)

        movies_filtered= get_topmovies_genre(genre)

        cards=[]
        for i in range(0, len(movies_filtered)):
            cards.append(
                {
                    "title": movies_filtered[i]['title'],
                    "image_url": movies_filtered[i]['img_url'],
                    "subtitle": "Note Presse : {}/5 ".format(movies_filtered[i]['notepresse']),
                    "buttons": [{
                        "type": "web_url",
                        "url": movies_filtered[i]['url'],
                        "title": "Voir sur Allociné"
                    },
                        {
                            "type": "postback",
                            "title": "Résumé",
                            "payload": "Summary_cine-{}".format(i)
                        }]
                }
            )
        send_card(sender, cards, ACCESS_TOKEN)
        btns = [
            {
                "content_type": "text",
                "title": "Plus de films !",
                "payload": "sorties_cine-3"
            },
            {
                "content_type": "text",
                "title": "Merci Electre",
                "payload": "Thanks"
            }
        ]
        send_quick_rep(sender, "Voulez-vous voir d'autres films ?", btns , ACCESS_TOKEN)


def exhibition_display(num, sender, payload =""):
    if num == 0 :             
        send_msg(sender, "Une petite expo donc ! ", ACCESS_TOKEN)
        msg = "Il y a plusieurs types d'expositions, qu'est ce qui vous intéresse le plus ?"
        
        btns_genre = get_genre_exhib()[1]
        send_quick_rep(sender, msg, btns_genre, ACCESS_TOKEN)

    elif num in range(1,4):
        cards = get_exhib(payload[:-2], int(payload[-1]))[1]
        send_card(sender, cards, ACCESS_TOKEN)
        
        btns =[
            {
                "content_type":"text",
                "title":"Plus d'expos !",
                "payload":"{}-{}".format(payload[:-2], int(payload[-1]) + 1)
            },
            {
                "content_type":"text",
                "title":"Un autre genre",
                "payload":"exhibition-0"
            },
            {
                "content_type":"text",
                "title":"Merci Iris",
                "payload":"Thanks"
            }
        ]
        time.sleep(10)
        send_quick_rep(sender, "Voulez-vous voir d'autres expos ?", btns ,ACCESS_TOKEN)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)