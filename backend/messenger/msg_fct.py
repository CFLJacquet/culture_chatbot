
import logging
import requests
import json

def user_details(sender, ACCESS_TOKEN):
        
    url = "https://graph.facebook.com/v2.6/"+str(sender)
    params = {'fields':'first_name,last_name,profile_pic,gender,locale', 'access_token':ACCESS_TOKEN}
    user_details = requests.get(url, params).json()
    
    if user_details['gender'] == 'male':
        user_gender="M"
    else:
        user_gender="Mme"

    logging.info('USER DETAIL: {}'.format(user_details))

    return user_gender,user_details['first_name'],user_details['last_name']

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

