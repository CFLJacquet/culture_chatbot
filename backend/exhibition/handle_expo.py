import json

main = []
with open('backend/exhibition/expo_scraper/expo_offspect.jsonl') as f:
    for line in f:
        main.append(json.loads(line))

extra = []
with open('backend/exhibition/expo_scraper/expo_offspect_detail.jsonl') as f:
    for line in f:
        extra.append(json.loads(line))

for eltm in main:
    for elte in extra:
        if eltm['url'] == elte['url']:
            eltm['summary'] = elte['summary']
            eltm['price'] = elte['price']

print(eltm)