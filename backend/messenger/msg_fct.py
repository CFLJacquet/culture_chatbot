
import logging
import requests
import json

def user_details(sender, ACCESS_TOKEN):
    """ :param sender: takes the sender ID as input
    :return: user_gender,user_details['first_name'],user_details['last_name'], user_details
    """
    url = "https://graph.facebook.com/v2.6/"+str(sender)
    params = {'fields':'first_name,\
last_name,\
profile_pic,\
gender,\
age_range,\
locale', 'access_token':ACCESS_TOKEN}
    user_details = requests.get(url, params).json()

    logging.info('USER DETAIL: {}'.format(user_details))
    
    if user_details['gender'] == 'male':
        user_gender="M"
    else:
        user_gender="Mme"

    return user_gender,user_details['first_name'],user_details['last_name'], user_details

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
            "title": "A court d'inspiration !",
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

