import sys
import json
import random
from pprint import pprint # for a more readable json output
import os
from backend.messenger.msg_fct import send_quick_rep, send_card, send_button


def norm_indice():
	""" pour ajouter les ID aux musees """
	musees = []
	with open("backend/musees/musees/listeM.jsonl", 'r') as f:
		for e, line in enumerate(f):
			temp = json.loads(line)
			temp["ID"] = "m"+str(e)
			musees.append(temp)

	with open("backend/musees/musees/listeM.json", 'w') as file:
		json.dump(musees, file)

def liste_surprise_categories():
	""" Transforme le document json en dictionnaire avec comme clefs les catégories et comme
	 	valeurs les musées dans ces catégories """

	with open("backend/musees/musees/listeM.json", 'r') as f:
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

	with open("backend/musees/musees/listeM.json", 'r') as f:
		musees = json.load(f)

	infos_musees = {}
	for i in range(0, len(musees)):

		if musees[i]["name"] not in infos_musees:
			infos_musees[musees[i]["name"]] = {}

		infos_musees[musees[i]["name"]]["ID"] = musees[i]["ID"]
		infos_musees[musees[i]["name"]]["adresse"] = musees[i]["location"]
		infos_musees[musees[i]["name"]]["image"] = musees[i]["image"]
		if "Descriptif" in musees[i]["infos_utiles"]:
			infos_musees[musees[i]["name"]]["description"] = musees[i]["infos_utiles"]
		else :
			infos_musees[musees[i]["name"]]["description"] = "Nous n'avons pas encore de description !"
		infos_musees[musees[i]["name"]]["prix_horaires"] = musees[i]["prix_horaires"]

	return infos_musees


def get_categorie_surprise(sender, text, ACCESS_TOKEN):

	toutes_categories = liste_surprise_categories()

	choix_categories = []
	for key in toutes_categories:
		if key not in choix_categories:
			choix_categories += [key]

	dict_choix_categories = {"Musées de beaux-arts à Paris" : "Beaux Arts",
							 "Histoire et cultures d'ailleurs" : "Histoire",
							 "Les musées les plus visités" : "Les plus visités",
							 "Les musées insolites de Paris" : "Insolite",
							 "Musées d'art moderne et contemporain" : "Art moderne",
							 "Les musées à découvrir en famille à Paris" : "Famille"
							 }

	btns = []
	for cat in dict_choix_categories :
		btns.append(
			{
				"content_type": "text",
				"title": dict_choix_categories[cat],
				"payload": "surprise_cat*-/{}".format(cat)
			}
		)
	
	send_quick_rep(sender, text, btns, ACCESS_TOKEN)


def get_musee_surprise(sender, categorie, ACCESS_TOKEN):
	tous_les_musees_par_categorie = liste_surprise_categories()
	toutes_les_infos_par_musee = liste_surprise_infos_musees()

	musees_possibles = []
	for cat in tous_les_musees_par_categorie :
		if cat == categorie :
			musees_possibles += tous_les_musees_par_categorie[cat]

	random.shuffle(musees_possibles)
	cards = []
	for musee in musees_possibles[:6] :

		cards.append(
			{
				"title" : musee,
				"image_url" : toutes_les_infos_par_musee[musee]["image"],
				"subtitle" : toutes_les_infos_par_musee[musee]["adresse"],
				"buttons" :
					[{
						"type" : "postback",
						"title" : "Tarifs",
						"payload" : "surprise_tarifs*-/{}".format(toutes_les_infos_par_musee[musee]["ID"]),
					},
					{
						"type": "postback",
						"title": "Description",
						"payload": "surprise_description*-/{}".format(toutes_les_infos_par_musee[musee]["ID"]),
					}
					]}
		)

	send_card(sender, cards, ACCESS_TOKEN)
	

def get_details_surprise(ID, action):
	
	with open("backend/musees/musees/listeM.json", 'r') as f:
		musees = json.load(f)
	
	result = [ x for x in musees if x["ID"] == ID][0]
	if action  == 'surprise_tarifs' :
		return result['prix_horaires']['Visite libre']
	else: 
		return result['infos_utiles']['Descriptif']


if __name__ == "__main__":
	print(liste_surprise_infos_musees())
	print(type(liste_surprise_infos_musees()))
	print(liste_surprise_infos_musees()["Musée d'Orsay"]["description"]["Descriptif"])
