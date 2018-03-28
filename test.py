import json
from pprint import pprint

with open("backend/musees/musees/spiders/musees/musees/listeM.json", 'r') as f:
    musees = json.load(f)

pprint(musees[0])