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
import jsonlines
import base64
import pathlib
# from PIL import Image
from urllib.request import urlopen
from io import StringIO, BytesIO
from pprint import pprint # for a more readable json output
import os
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




def liste_surprise_infos_musees():
	""" Transforme le document json en dictionnaire avec comme clefs les musées et comme valeurs
	 	les informations sur chacun des musées """

	donnees = open("musees/spiders/musees/musees/listeM.json")
	musees = list(donnees)

	infos_musees = {}
	for i in range(982, len(musees)):

		if musees[i]["name"] not in infos_musees:
			infos_musees[musees[i]["name"]] = {}

		infos_musees[musees[i]["name"]]["adresse"] = musees[i]["location"]
		infos_musees[musees[i]["name"]]["image"] = musees[i]["image"]
		infos_musees[musees[i]["name"]]["description"] = musees[i]["infos_utiles"]
		infos_musees[musees[i]["name"]]["prix_horaires"] = musees[i]["prix_horaires"]

	return infos_musees




def get_musees_surprise() :
	with open("backend/cinema/cinema_allocine", 'rb') as f:
		d = pickle.Unpickler(f)
		data = d.load()




def get_categorie_surprise():

	toutes_categories = liste_surprise_categories()

	categories = []
	for key in toutes_categories:
		# if elt["Categorie"] == musees:
		#     categories.append(elt)
		if key not in categories:
			categories += [key]

	cards = []
	for cat in categories:
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

	return categories, cards


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
						"image" : 
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

categories = {}
infos_musees = {}
for i in range(0, len(musees)) :
	if musees[i]["Categorie"] not in categories :
		categories[musees[i]["Categorie"]] = []
	if musees[i]["name"] not in categories[musees[i]["Categorie"]] :
		categories[musees[i]["Categorie"]] += [musees[i]["name"]]
for i in range(0, len(musees)) :
	if musees[i]["name"] not in infos_musees :
		infos_musees[musees[i]["name"]] = {}
	infos_musees[musees[i]["name"]]["adresse"] = musees[i]["location"]
	infos_musees[musees[i]["name"]]["image"] = musees[i]["image"]
	infos_musees[musees[i]["name"]]["description"] = musees[i]["infos_utiles"]
	infos_musees[musees[i]["name"]]["prix_horaires"] = musees[i]["prix_horaires"]



print(categories)
#print(categories["Les musées insolites de Paris"])
#print(len(categories["Les musées insolites de Paris"]))
print(infos_musees)



# with open("musees/spiders/musees/musees/listeM.jsonl", "wb") as f :
# 	d = pickle.Pickler(f)
# 	d.dump(True)
#
# print(type(d))