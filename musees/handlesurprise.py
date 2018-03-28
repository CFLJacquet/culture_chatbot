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
import base64
import pathlib
from urllib.request import urlopen
from io import StringIO, BytesIO
from pprint import pprint # for a more readable json output
import os
from backend.messenger.msg_fct import send_quick_rep, send_card, send_button
#from flask import Flask, request
import logging
# from scraper-musees-surprise.py import MuseesParis
#
#
# def start_request(reponse):
#     approbation = ["Oui", "oui", "Yes", "yes", "ok", "Ok", "OK", "go", "Yep", "yep"]
#     if reponse in approbation :
#         scraper-musees-surprise.process.crawl(MuseesParis)
#         scraper - musees - surprise.process.start()
#         try:
#             return json.loads(results)
#         except Exception as e:
#             return results





def liste_surprise_categories():
	""" Transforme le document json en dictionnaire avec comme clefs les catégories et comme
	 	valeurs les musées dans ces catégories """

	with open("musees/spiders/musees/musees/listeM.json", 'r') as f:
		musees = json.load(f)

	categories = {}
	for i in range(0, len(musees)):

		if musees[i]["Categorie"] not in categories:
			categories[musees[i]["Categorie"]] = []

		if musees[i]["name"] not in categories[musees[i]["Categorie"]]:
			categories[musees[i]["Categorie"]] += [musees[i]["name"]]

	return categories

print(liste_surprise_categories())


def liste_surprise_infos_musees():
	""" Transforme le document json en dictionnaire avec comme clefs les musées et comme valeurs
	 	les informations sur chacun des musées """

	with open("musees/spiders/musees/musees/listeM.json", 'r') as f:
		musees = json.load(f)

	infos_musees = {}
	for i in range(0, len(musees)):

		if musees[i]["name"] not in infos_musees:
			infos_musees[musees[i]["name"]] = {}

		infos_musees[musees[i]["name"]]["adresse"] = musees[i]["location"]
		infos_musees[musees[i]["name"]]["image"] = musees[i]["image"]
		if "Descriptif" in musees[i]["infos_utiles"]:
			infos_musees[musees[i]["name"]]["description"] = musees[i]["infos_utiles"]
		else :
			infos_musees[musees[i]["name"]]["description"] = "Nous n'avons pas encore de description !"
		infos_musees[musees[i]["name"]]["prix_horaires"] = musees[i]["prix_horaires"]

	return infos_musees

print(liste_surprise_infos_musees())
print(type(liste_surprise_infos_musees()))


def get_musees_surprise() :
	with open("musees/spiders/musees/musees/listeM.json", 'r') as f:
		musees = json.load(f)






def get_categorie_surprise():

	toutes_categories = liste_surprise_categories()

	choix_categories = []
	for key in toutes_categories:
		# if elt["Categorie"] == musees:
		#     categories.append(elt)
		if key not in choix_categories:
			choix_categories += [key]

	cards = []
	for cat in choix_categories :
		cards.append(
			{
				"nom": cat["name"],
			}
		)
			# 	"image_url": cat["image"],
			# 	"subtitle": cat["location"],
			# 	"buttons": [{
			# 	"type": "text",
			# 	"content": cat["prix_horaires"]["Visite libre"],
			# 	"title": "Prix et horaire d'une visite libre"
			# 	},
			# 			# {
			# 			# "type": "text",
			# 			# "url": cat["prix_horaires"]["Visite libre"],
			# 			# "title": "Prix et horaire d'une visite libre"
			# 			# }
			# 	{
			# 	"type": "postback",
			# 	"title": "Détails",
			# 	"payload": cat["infos_utiles"]["Descriptif"],
			# 	},
			# 	{
			# 	"type": "image",
			# 	"image_url": cat["image"],
			# 	"subtitle": cat["name"],
            #
			# 	}]
			# }
			# )

	return choix_categories, cards


def get_musee_surprise(categorie) :
	tous_les_musees_par_categorie = liste_surprise_categories()
	toutes_les_infos_par_musee = liste_surprise_infos_musees()

	cards = []
	for cat in tous_les_musees_par_categorie :
		if cat == categorie :
			for musee in tous_les_musees_par_categorie[cat]:
				cards.append(
					{
						"nom" : musee,
						"adresse" : toutes_les_infos_par_musee[musee]["adresse"],
						"image" : toutes_les_infos_par_musee[musee]["image"],
					}
				)





# donnees = jsonlines.open("musees/spiders/musees/musees/listeM.jsonl")
# musees = list(donnees)
# print(musees[0])
# print(type(musees[0]))
# print(type(musees))
# print(len(musees))


with open("musees/spiders/musees/musees/listeM.json", 'r') as f:
	musees = json.load(f)

print(type(musees))
print(len(musees))

# categories = {}
# infos_musees = {}
# for i in range(0, len(musees)) :
# 	if musees[i]["Categorie"] not in categories :
# 		categories[musees[i]["Categorie"]] = []
# 	if musees[i]["name"] not in categories[musees[i]["Categorie"]] :
# 		categories[musees[i]["Categorie"]] += [musees[i]["name"]]
# for i in range(0, len(musees)) :
# 	if musees[i]["name"] not in infos_musees :
# 		infos_musees[musees[i]["name"]] = {}
# 	infos_musees[musees[i]["name"]]["adresse"] = musees[i]["location"]
# 	infos_musees[musees[i]["name"]]["image"] = musees[i]["image"]
# 	infos_musees[musees[i]["name"]]["description"] = musees[i]["infos_utiles"]
# 	infos_musees[musees[i]["name"]]["prix_horaires"] = musees[i]["prix_horaires"]
#
#
#
# print(categories)
# #print(categories["Les musées insolites de Paris"])
# #print(len(categories["Les musées insolites de Paris"]))
# print(infos_musees)



# with open("musees/spiders/musees/musees/listeM.jsonl", "wb") as f :
# 	d = pickle.Pickler(f)
# 	d.dump(True)
#
# print(type(d))