import json
import sys

data = []
with open('/Users/constanceleonard/Desktop/strolling/backend/cinema/senscritiquescrapping/extracted-data/critiques_films.jsonl') as f:
    for line in f:
        data.append(json.loads(line))
print(data)
for d in data:
    print(d)

def critique_movie(film_nom):
    film_à_laffiche_extracted=[]
    for i in range(0, len(data)):
        film_à_laffiche_extracted.append(data[i]["titre"])
    print(film_à_laffiche_extracted)
    if film_nom in film_à_laffiche_extracted:
        num=film_à_laffiche_extracted.index(film_nom)
        print(num)
        prem_critique=data[num]["critique_1"]
        deux_critique=data[num]["critique_2"]
    return print("Voici la première critique:", prem_critique), print("Voici la deuxième critique:", deux_critique)

if __name__ == '__main__':
    print(sys.stdout.encoding)
    print(critique_movie("La Belle et la belle"))
