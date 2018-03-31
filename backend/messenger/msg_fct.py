
import logging
import requests
import json
from datetime import date as dt

def user_details(sender, ACCESS_TOKEN):
    """ :param sender: takes the sender ID as input
    :return: user_gender,user_details['first_name'],user_details['last_name'], user_details
    """
    # Make request to Graph API
    url = "https://graph.facebook.com/v2.12/"+str(sender)
    params = {'fields':'first_name,\
last_name,\
profile_pic,\
gender,\
age_range,\
locale', 'access_token':ACCESS_TOKEN}
    user_details = requests.get(url, params).json()
    logging.info('USER DETAIL: {}'.format(user_details))
    print(user_details)

    # Transform and load in DB, and exception if user ID not found
    with open("backend/others/users_DB.json", "r") as f:
        users_DB = json.load(f)
    
    try : 
        if "error" in user_details:
            user_gender, first_name , last_name = "","toi",""

        else:
            if user_details['gender'] == 'male':
                user_gender="M"
            elif user_details['gender'] == 'female':
                user_gender="Mme"
            else: 
                user_gender=""
            first_name , last_name = user_details["first_name"], user_details["last_name"]

            if sender not in users_DB:
                users_DB[sender] = {
                    "last": str(dt.today()), 
                    "gender": user_details["gender"],
                    "first_name": user_details["first_name"], 
                    "last_name": user_details["last_name"], 
                    "locale": user_details["locale"],
                    "nb_interactions": 1}
            elif sender in users_DB:
                users_DB[sender]["last"] = str(dt.today())
                users_DB[sender]["nb_interactions"] += 1    
                
            with open("backend/others/users_DB.json", "w") as jsonFile:
                json.dump(users_DB, jsonFile)    

    except Exception as e: 
        logging.error("USER DETAIL ERROR : {}".format(e))
        user_gender, first_name , last_name = "","toi",""

    return user_gender, first_name , last_name

def typing_bubble(recipient, ACCESS_TOKEN):

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": ACCESS_TOKEN},
        data=json.dumps({
            "recipient": {"id": recipient},
            "sender_action": "typing_on"
            }),
        headers={'Content-type': 'application/json'})
    if r.status_code != 200:
        logging.info('STATUS CODE - TYPING BUBBLE: {} - {}'.format(r.status_code, r.text))

    return 'sent'

def start_buttons(sender, text,ACCESS_TOKEN):
    btns =[
        {
            "content_type":"text",
            "title":"Cinéma",
            "payload":"sorties_cine-0"
        },
        {
            "content_type":"text",
            "title":"Art",
            "payload":"art-0"
        },
        {
            "content_type":"text",
            "title":"Autre chose",
            "payload":"Not_interested"
        }
    ]
    send_quick_rep(sender, text, btns ,ACCESS_TOKEN)



def art_buttons(sender, text,ACCESS_TOKEN):
    btns =[
        {
            "content_type":"text",
            "title":"Exposition",
            "payload":"exhibition-0"
        },
        {
            "content_type":"text",
            "title": "Pas d'idée !",
            "payload": "surprise-0"
        },
        # {
        #     "content_type":"text",
        #     "title":"Autre chose",
        #     "payload":"Not_interested"
        # }
    ]
    send_quick_rep(sender, text, btns ,ACCESS_TOKEN)



def send_msg(recipient, answer, ACCESS_TOKEN):

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

def send_quick_rep(recipient, text, btns, ACCESS_TOKEN):

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": ACCESS_TOKEN},
        data=json.dumps({
            "recipient": {"id": recipient},
            "message": {
                "text": text, 
                "quick_replies": btns
            }
            }),
        headers={'Content-type': 'application/json'})
    if r.status_code != 200:
        logging.info('STATUS CODE - QCK: {} - {}'.format(r.status_code, r.text))

    return 'sent'


def send_button(recipient,text,title,payload, ACCESS_TOKEN):
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

def send_card(recipient, cards, ACCESS_TOKEN):
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

