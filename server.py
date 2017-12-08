from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import requests
import json
from backend.cinema.allocine import get_last_movies 


#Block to create logs
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

ACCESS_TOKEN = "EAAHSfldMxYcBAAt4D30ZAzVHSnhhFqxV15wMJ0RwZCOBH4MZALBJOa8gTvUV0OTL5t3Q4ZBOosziQ3AXIwYpgpdbJCRRkbJKBuB7FASzhnZAcZCsy6expZATAbflsnln2Hd5I1Yo8J2Ddny170yI13r7A224a20yBWczLeYZAzZBDTQZDZD"

def user_details(sender):
        
    url = "https://graph.facebook.com/v2.6/"+str(sender)
    params = {'fields':'first_name,last_name,profile_pic,gender,locale', 'access_token':ACCESS_TOKEN}
    user_details = requests.get(url, params).json()
    
    if user_details['gender'] == 'male':
        user_gender="M"
    else:
        user_gender="Mme"

    logging.info('USER DETAIL: {}'.format(user_details))

    return user_gender,user_details['first_name'],user_details['last_name']

def send_msg(recipient, answer):

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": ACCESS_TOKEN},
        data=json.dumps({
            "recipient": {"id": recipient},
            "message": {"text": answer}
            }),
        headers={'Content-type': 'application/json'})
    if r.status_code != 200:
        logging.info('STATUS CODE - MSG: {} - {}'.format(r.status_code, r.text))

    return 'sent'

def send_button(recipient,text,title,payload):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": ACCESS_TOKEN},
        data=json.dumps({
            "recipient":{"id":recipient},
            "message":{
                "attachment":{
                    "type":"template",
                    "payload":{
                        "template_type":"button",
                        "text":text,
                        "buttons":
                        [{
                            "type":"postback",
                            "title":title,
                            "payload":payload
                        }]      
                    }
                }
            }
        }),
        headers={'Content-type': 'application/json'})
    if r.status_code != 200:
        logging.info('STATUS CODE - BUTTON: {} - {}'.format(r.status_code, r.text))

def send_card(recipient, cards):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": ACCESS_TOKEN},
        data=json.dumps({
            "recipient":{"id":recipient},
            "message":{
                "attachment":{
                    "type":"template",
                    "payload":{
                        "template_type":"generic",
                        "elements":cards
                    }
                }
            }
        }),
        headers={'Content-type': 'application/json'})
    if r.status_code != 200:
        logging.info('STATUS CODE - CARD: {} - {}'.format(r.status_code, r.text))



@app.route('/', methods=['GET'])
def handle_verification():
    logging.info(request.args['hub.challenge'])
    return request.args['hub.challenge']

@app.route('/', methods=['POST'])
def handle_event():
    #On devrait mettre un try: / except: pour indiquer à l'utilisateur si notre appel API a foiré
    latest = get_last_movies()
    logging.info('LATEST FILMS :'+str(latest))
    
    data = request.json
    logging.info("DATA: {}".format(data))

    event = data['entry'][0]['messaging'][0]
    sender = event['sender']['id']

    if "message" in event: 
        message = event['message']['text'].lower()

        if message == "bonjour":
            user = user_details(sender)
            
            answer="Bonjour {} {} {}, bienvenue sur Strolling. Je suis Iris votre majordome, je vais vous trouver le divertissement qui vous plaira.".format(user[0],user[1],user[2])
            send_msg(sender, answer)
            send_button(sender,"Seriez-vous intéressé par une séance de cinéma ?","Oui","sorties_cine")
        else:
            answer='Et si vous me disiez "bonjour" ?'
            send_msg(sender, answer)

    #Gestion de l'evenement "je veux des infos sur le cinema"
    if "postback" in event:
        if event['postback']['payload'] == "sorties_cine":
            send_msg(sender,'Voici les meilleurs films en salle')

            cards=[]
            for i in range (0,3):
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
            send_card(sender,cards)

        if event['postback']['payload'][:7] == "Summary":
            i = int(event['postback']['payload'][8:])
            send_msg(sender, "-- "+latest[i]['title']+" -- Résumé -- \n\n"+latest[i]['summary'])
            

    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)