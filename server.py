from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import requests
import json

from backend.cinema.allocine import get_last_movies
from backend.messenger.msg_fct import user_details, send_msg, send_button, send_card, send_quick_rep

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
    #On devrait mettre un try: / except: pour indiquer à l'utilisateur si notre appel API a foiré + actualiser chaque semaine
    latest = get_last_movies()
    logging.info('LATEST FILMS :'+str(latest))
    
    data = request.json
    logging.info("DATA: {}".format(data))

    event = data['entry'][0]['messaging'][0]
    sender = event['sender']['id']

    if "message" in event: 
        message = event['message']['text'].lower()

        if message == "bonjour":
            user = user_details(sender, ACCESS_TOKEN)
            
            answer="Bonjour {} {} {}, bienvenue sur Strolling.  \
                Je suis Iris votre majordome, je vais vous trouver le \
                divertissement qui vous plaira.".format(user[0],user[1],user[2])
            send_msg(sender, answer, ACCESS_TOKEN)
            btns =[
                {
                    "content_type":"text",
                    "title":"Oh oui !",
                    "payload":"sorties_cine-0"
                },
                {
                    "content_type":"text",
                    "title":"Bof",
                    "payload":"Not_interested"
                }
            ]
            send_quick_rep(sender, "Seriez-vous intéressé par une séance de cinéma ?", btns ,ACCESS_TOKEN)
        else:
            if event['message']['quick_reply']['payload'][:12] == "sorties_cine":
                num = int(event['message']['quick_reply']['payload'][13:])
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
                            "payload":"Summary-{}".format(i)
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
                    
            
            elif event['message']['quick_reply']['payload'] == "Not_interested":
                send_msg(sender, "Dommage ! A bientôt", ACCESS_TOKEN)

            elif event['message']['quick_reply']['payload'] == "Thanks":
                send_msg(sender, "Ravie d'avoir pu t'aider ! A bientôt :)", ACCESS_TOKEN)

            else : 
                send_msg(sender, "Et si vous me disiez bonjour ?", ACCESS_TOKEN)

    if "postback" in event:
        if event['postback']['payload'][:7] == "Summary":
            i = int(event['postback']['payload'][8:])
            send_msg(sender, "-- "+latest[i]['title']+" -- Résumé -- \n\n"+latest[i]['summary'], ACCESS_TOKEN)
           
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)