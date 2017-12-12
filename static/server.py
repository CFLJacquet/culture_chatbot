from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import datetime # to read datetime objects in exhibition data
import pickle

from backend.cinema.allocine import get_last_movies
from backend.messenger.msg_fct import user_details, send_msg, send_button, send_card, send_quick_rep
from backend.exhibition.handle_expo import get_genre, get_exhib
from backend.others.bdd_jokes import random_joke


#Bloc créant des logs
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

ACCESS_TOKEN = "EAAHSfldMxYcBAAt4D30ZAzVHSnhhFqxV15wMJ0RwZCOBH4MZALBJOa8gTvUV0OTL5t3Q4ZBOosziQ3AXIwYpgpdbJCRRkbJKBuB7FASzhnZAcZCsy6expZATAbflsnln2Hd5I1Yo8J2Ddny170yI13r7A224a20yBWczLeYZAzZBDTQZDZD"




@app.route('/', methods=['GET'])
def handle_verification():
    logging.info(request.args['hub.challenge'])
    return request.args['hub.challenge']

@app.route('/', methods=['POST'])
def handle_event():
    #NB: la requête API est effectuée à chaque msg entrant
    latest = get_last_movies()
    logging.info('LATEST FILMS :'+str(latest))
    
    data = request.json
    logging.info("DATA: {}".format(data))

    event = data['entry'][0]['messaging'][0]
    sender = event['sender']['id']
    user = user_details(sender, ACCESS_TOKEN)

    if "message" in event: 
        message = event['message']['text'].lower()

        if message == "bonjour":
            welcome(sender, user)
            
        else:
            if event['message']['quick_reply']['payload'][:12] == "sorties_cine":
                num = int(event['message']['quick_reply']['payload'][13:])
                film_display(num, sender, latest)
            
            elif event['message']['quick_reply']['payload'][:10] == "exhibition":
                num = int(event['message']['quick_reply']['payload'][11:])
                exhibition_display(num, sender)
            elif event['message']['quick_reply']['payload'][:-2] in get_genre()[0]:
                num = int(event['message']['quick_reply']['payload'][-1])
                exhibition_display(num, sender, event['message']['quick_reply']['payload'])      
            
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
            i = int(event['postback']['payload'][13:])
            send_msg(sender, "-- "+latest[i]['title']+" -- Résumé -- \n\n"+latest[i]['summary'], ACCESS_TOKEN)
        
        elif event['postback']['payload'][:12] == "Summary_expo":
            x = event['postback']['payload'].split("*-/") 
            
            # x[0]: 'Summary_expo' / x[1]: genre / x[2]: card n° / x[3]: iteration
            data = get_exhib(x[1], int(x[3]))[0][int(x[2])]

            send_msg(sender, "Description: "+data['summary'], ACCESS_TOKEN)
            send_msg(sender, "Horaires: "+data['prog'], ACCESS_TOKEN)
            send_msg(sender, "Prix: "+data['price'], ACCESS_TOKEN)
        

    return "ok"




def welcome(sender, user):
    answer="Bonjour {} {} {}, bienvenue sur Strolling.  \
            Je suis Iris votre majordome, je vais vous trouver le \
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
        cards.append(
            {
            "title": latest[i]['title'],
            "image_url": latest[i]['img_url'], 
            "subtitle":"Note Presse : {}/5 \n Genre: {}".format(latest[i]['notepresse'], ', '.join(latest[i]['genre'])),
            "buttons":[{
                "type":"web_url",
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
            "content_type":"text",
            "title":"Merci Iris",
            "payload":"Thanks"
        }
    ]
    if num == 0:
        send_quick_rep(sender, "Voulez-vous voir d'autres films ?", btns ,ACCESS_TOKEN)
        
def exhibition_display(num, sender, payload =""):
    if num == 0 :             
        send_msg(sender, "Une petite expo donc ! ", ACCESS_TOKEN)
        msg = "Il y a plusieurs types d'expositions, qu'est ce qui vous intéresse le plus ?"
    elif num == 1 :
        cards = get_exhib(payload[:-2], int(payload[-1]))[1]
        send_card(sender, cards, ACCESS_TOKEN)
        msg = "Un autre genre d'expo ?"
    else : 
        msg = "Un autre genre d'expo ?"


    btns_genre = get_genre()[1]
    send_quick_rep(sender, msg, btns_genre ,ACCESS_TOKEN)





if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)