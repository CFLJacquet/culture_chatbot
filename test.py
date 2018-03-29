import json
from pprint import pprint
from backend.language.handle_text_query_cine import vect_search

with open('backend/cinema/cinema_full.json', 'r') as f:
    DB = json.load(f)

pprint(DB[0])

all_genre= []
for i in DB:
    for k in i["genre"]:
        all_genre.append(k["$"])
all_genre=list(set(all_genre))
pprint(all_genre)
print(len(all_genre))
