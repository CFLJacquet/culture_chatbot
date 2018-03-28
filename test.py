from backend.musees.handlesurprise import get_details_surprise, get_musee_surprise
import json
from pprint import pprint

# with open("backend/musees/musees/spiders/musees/musees/listeM.json", 'r') as f:
# 	musees = json.load(f)

# liste_insolites = []
# for element in musees :
#     if element["Categorie"] == "Les mus\u00e9es insolites de Paris" :
#         liste_insolites += [element["image"]]


with open("backend/musees/musees/listeM.json", 'r') as f:
    musees = json.load(f)

print(musees)

# get_musee_surprise('esf', 'Les musées insolites de Paris', 'oiofnz')

