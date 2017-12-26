Notes to myself: 

- activer le bouton "get started": télécharger le plugin 'postman' sur Chrome et 'importer' une requête cURL en texte brut : 

curl -X POST -H "Content-Type: application/json" -d '{
  "greeting": [
            {
               "locale": "default",
               "text": "A bot which finds you the best activities in Paris"
            },
            {
               "locale": "fr_FR",
               "text": "Un bot qui te trouve les meilleures activités à Paris"
            }
         ],
  "get_started": {
    "payload":"first_conv"
  }
  ...
}' "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=<XXXXXX>"

- quand on supprime le webhook et on le réactive, penser à l'associer à la page FB

- scrapy: exports options !!! https://doc.scrapy.org/en/1.2/topics/feed-exports.html#std:setting-FEED_EXPORT_ENCODING

- scrapy: appeler d'autres scraper dans le scraper principal
https://stackoverflow.com/questions/33589136/scrapy-understanding-how-do-items-and-requests-work-between-callbacks 


avoir derniere version du master:
- git pull --rebase master (prendre les modif qui ont été mergé pdt ce temps)

git add [fichier en conflit]

=> git push -f (force push)
