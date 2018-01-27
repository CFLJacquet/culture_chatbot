from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import time
import datetime # to read datetime objects in exhibition data
import pickle

from backend.cinema.allocine import get_last_movies
from backend.messenger.msg_fct import user_details, typing_bubble, send_msg, send_button, send_card, send_quick_rep
from backend.exhibition.handle_expo import get_genre, get_exhib, get_exhib_query, get_detail_exhib
from backend.language.handle_text import get_meaning
from backend.language.handle_text_query import vect_search
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

ACCESS_TOKEN = "EAACQPdicZCwQBANH7jaSrjqWSGqMZBezC7ouYsq2YbUpxn9QsDurCmtq66cZAlglVigOw99kklESqL2jZCfmiDKUplfcf3Ue0RFPAGUBPxxL2pr0I864Q1jQDlbdy0DoRkIRvZBsiNcwtFmrYNXyYdNZBZBX2M4g8rmpZAZARCcEFqwZDZD"

@app.route('/test')
def test():
    return "<h1>Le serveur fonctionne correctement !</h1>"

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
    
    typing_bubble(sender, ACCESS_TOKEN)

    if "message" in event:
        #handles quick replies (buttons at the bottom of the conversation)     
        if 'quick_reply' in event['message'] :
            payload = event['message']['quick_reply']['payload']
            if payload[:12] == "sorties_cine":
                num = int(payload[-1])
                film_display(num, sender, latest)
            
            elif payload[:10] == "exhibition":
                num = int(payload[-1])
                exhibition_display(num, sender)
            elif payload[:-2] in get_genre()[0]:
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
                send_msg(sender, "Nice sticker {} !".format(user)[1], ACCESS_TOKEN)

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
            answer = get_meaning(message)
            if answer[0] == 1:
                welcome(sender, user)
            if answer[1] == 1:
                film_display(0, sender, latest)
            if answer[2] == 1:
                time.sleep(1)
                send_msg(sender, "J'ai trouvé ça, certaines devraient te plaire !", ACCESS_TOKEN)
                send_card(sender, get_exhib_query(vect_search(message), 1), ACCESS_TOKEN)
                #exhibition_display(0, sender)
            if answer[3] == 1:
                send_msg(sender, "A bientôt !", ACCESS_TOKEN)
            if answer == [0,0,0,0]:
                send_msg(sender, "Je n'ai pas compris ce que tu as dit... 😰", ACCESS_TOKEN)
                send_msg(sender, "Tu peux me demander des infos sur des expos ou des films. Si tu as eu les informations souhaitées, dis moi juste 'stop' ou 'merci' :)", ACCESS_TOKEN)


    elif "postback" in event:
        if event['postback']['payload'] == "first_conv":
            welcome(sender, user)
        
        elif event['postback']['payload'][:12] == "Summary_cine":
            i = int(event['postback']['payload'][-1])
            send_msg(sender, "-- "+latest[i]['title']+" -- Résumé -- \n\n"+latest[i]['summary'], ACCESS_TOKEN)
        
        elif event['postback']['payload'][:12] == "Summary_expo":
            x = event['postback']['payload'].split("*-/") 
            
            # x[0]: 'Summary_expo' / x[1]: exhib_ID
            data = get_detail_exhib(x[1])
            
            send_msg(sender, "Description: "+data['summary'], ACCESS_TOKEN)
            send_msg(sender, "Horaires: "+data['timetable'], ACCESS_TOKEN)
            send_msg(sender, "Prix: "+data['price'], ACCESS_TOKEN)
            time.sleep(10)
            start_buttons(sender, "Autre chose ?")
        
    else: 
        send_msg(sender, "Je n'ai pas compris ta demande... 😰", ACCESS_TOKEN)
        
    return "ok"




def welcome(sender, user):
    time.sleep(1)
    answer="Salut {}, je suis Electre ! Je connais les meilleurs films et expos de Paris.".format(user[1])
    send_msg(sender, answer, ACCESS_TOKEN)
    start_buttons(sender, "Qu'est-ce qui t'intéresserait ?")

def start_buttons(sender, text):
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
            "title":"Autre chose",
            "payload":"Not_interested"
        }
    ]
    send_quick_rep(sender, text, btns ,ACCESS_TOKEN)


def film_display(num, sender, latest):
    """ returns cards with films from the "latest" var (extracted with API) """

    time.sleep(1)
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
            "title":"Merci Electre",
            "payload":"Thanks"
        }
    ]
    if num == 0:
        send_quick_rep(sender, "Veux-tu voir d'autres films ?", btns ,ACCESS_TOKEN)
        
def exhibition_display(num, sender, payload =""):
    time.sleep(1)
    if num == 0 :
        msg = "Il y a plusieurs types d'expositions, qu'est-ce qui t'intéresse le plus ?"
        btns_genre = get_genre()[1]
        send_quick_rep(sender, msg, btns_genre ,ACCESS_TOKEN)

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



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)