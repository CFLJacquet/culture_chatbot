#Notes to myself: 

## activer le bouton "get started": 
télécharger le plugin 'postman' sur Chrome et 'importer' une requête cURL en texte brut : 

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

## Suppression webhook
quand on supprime le webhook et on le réactive, penser à l'associer à la page FB

## scrapy: 
* exports options !!! https://doc.scrapy.org/en/1.2/topics/feed-exports.html#std:setting-FEED_EXPORT_ENCODING

* appeler d'autres scraper dans le scraper principal
https://stackoverflow.com/questions/33589136/scrapy-understanding-how-do-items-and-requests-work-between-callbacks 


## avoir derniere version du master:
- git pull --rebase master (prendre les modif qui ont été mergé pdt ce temps)

git add [fichier en conflit]

=> git push -f (force push)

## Changer de repo git pour pousser

* git remote -v : regarde vers où pointe le git
* git remote set-url origin [lien vers nouveau repo git]

## Git stash

* git stash : pour mettre en cache les modifs
* git checkout (-b) [branch] : se mettre sur une nouvelle branche
* git stash pop : récupérer les modifs
* git add / commit / push

## Créer serveur de test 

1. créer une Test-app
2. créer une nouvelle page dans [Génération de tokens]
3a. sélectionner la page pour récupérer le token
3b. remplacer le token dans "server.py" ---> ATTENTION, il faudra le remplacer à nouveau avant de commit&push
4a. Dans [Webhooks], cliquer sur configurer des webhooks
- dans url de rappel: mettre le lien https de ngrok
- dans vérifier le jeton: mettre 'secret'
- cocher 'messages' et 'messaging_postback'
4b. toujours dans [Webhooks], sélectionner la page à laquelle souscrire le webhook

## TreeTaggerWrapper

The biggest problem encountered with command-line version of TreeTagger tools which come with the package is the restart of TreeTagger itself at each new text to tag. At each process start, TreeTagger must reload all its language-dependant data. Not a problem to tag few files, it become too time consuming when you try to tag hundreds or thousands files.

The solution we adopt is to start TreeTagger once, with ad-hoc options for the target language, with control over its input and output streams, and to keep communications opened as long as we want/need.

https://perso.limsi.fr/pointal/doku.php?id=dev:treetaggerwrapper 