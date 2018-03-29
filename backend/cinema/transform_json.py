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
        critique1=data[num]["critique_1"]
        critique2=data[num]["critique_2"]
        note_critique1=data[num]["note_critique_1"]
        note_critique2=data[num]["note_critique_1"]
        url_critique1=data[num]["critique_1_url"]
        url_critique2=data[num]["critique_2_url"]
    return print("Voici la première critique:", critique1), print("Voici la deuxième critique:", critique2)

if __name__ == '__main__':
    print(sys.stdout.encoding)
    print(critique_movie("La Belle et la belle"))
