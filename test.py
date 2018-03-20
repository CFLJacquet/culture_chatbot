# from backend.exhibition.expo_scraper.handle_exhibition_data import run_spiders, append_to_full, merge_results
from backend.exhibition.indexator import *
import nltk
import unidecode
# import json


pattern = r'''(?x)              # set flag to allow verbose regexps
            aujourd'hui             # exception 1
            | prud'hom\w+           # exception 2
            | \w'                   # contractions d', l', j', t', s'
            | \d+(?:,\d+)?%?€?      # currency and percentages, e.g. 12,40€, 82%        
            | (?:[A-Z]\.)+          # abbreviations, e.g. U.S.A.
            | \w+(?:-\w+)*          # words with optional internal hyphens
            #| [][.,;"'?():_`-]     # these are separate tokens; includes ], [
        '''

a = "Baas\u00a0est probablement l'un des designers hollandais les plus influents de ce d\u00e9but de XXIe si\u00e8cle.\
 N\u00e9 en 1979, il grandit dans le sud de la Hollande. \u00c0 la suite \u00e0 son dipl\u00f4me secondaire, il part \u00e9tudier dans \
 la prestigieuse \u00e9cole de design, la\u00a0Design Academy\u00a0d'Eindhoven en 1996. Son oeuvre rebelle, amusante, intellectuelle, th\u00e9\u00e2trale, \
 oscille entre l'art et le design. Cette subtilit\u00e9 cr\u00e9ative lui a ainsi permis d'affirmer sa singularit\u00e9 dans le monde du design. Son travail\
  couvre aujourd'hui diff\u00e9rents domaines d'application de l'installation \u00e0 l'espace public, s'exprimant \u00e0 travers l'architecture, l'int\u00e9rieur,\
   la sc\u00e9nographie, le th\u00e9\u00e2tre et des performances.\nSes travaux sont conserv\u00e9s dans les collections du MoMA,\u00a0Victoria & Albert Museum, Les\
    Arts Decoratifs, San Francisco Museum of Modern Art, Die Neue Sammlung, Stedelijk Museum et Rijksmuseum, ou encore celles de personnalit\u00e9s telles que\u00a0Brad\
     Pitt, Kanye West, Ian Schrager\u00a0et Adam Lindemann. Il est \u00e9galement en contrat avec Louis Vuitton, Swarovski, Gramercy Park Hotel, Dior, Dom Ruinard et Berlutti.\
     \nL'exposition de la\u00a0Carpenters Workshops Gallery vous propose ainsi de d\u00e9couvrir l'\u0153uvre essentielle d'un des plus importants designers contemporains."

s2 = unidecode.unidecode(a.lower())

words = nltk.regexp_tokenize(s2, pattern)

#['baas', 'est', 'probablement', "l'", 'un', 'des', 'designers', 'hollandais', 'les', 'plus', 'influents', 'de', 'ce', 'début', 'de', 'xxie', 'siècle', 'né', 'en', '1979', 'il', 'grandit', 'dans', 'le', 'sud', 'de', 'la', 'hollande', 'à', 'la', 'suite', 'à', 'son', 'diplôme', 'secondaire', 'il', 'part', 'étudier', 'dans', 'la', 'prestigieuse', 'école', 'de', 'design', 'la', 'design', 'academy', "d'", 'eindhoven', 'en', '1996', 'son', 'oeuvre', 'rebelle', 'amusante', 'intellectuelle', 'théâtrale', 'oscille', 'entre', "l'", 'art', 'et', 'le', 'design', 'cette', 'subtilité', 'créative', 'lui', 'a', 'ainsi', 'permis', "d'", 'affirmer', 'sa', 'singularité', 'dans', 'le', 'monde', 'du', 'design', 'son', 'travail', 'couvre', "aujourd'hui", 'différents', 'domaines', "d'", 'application', 'de', "l'", 'installation', 'à', "l'", 'espace', 'public', "s'", 'exprimant', 'à', 'travers', "l'", 'architecture', "l'", 'intérieur', 'la', 'scénographie', 'le', 'théâtre', 'et', 'des', 'performances', 'ses', 'travaux', 'sont', 'conservés', 'dans', 'les', 'collections', 'du', 'moma', 'victoria', 'albert', 'museum', 'les', 'arts', 'decoratifs', 'san', 'francisco', 'museum', 'of', 'modern', 'art', 'die', 'neue', 'sammlung', 'stedelijk', 'museum', 'et', 'rijksmuseum', 'ou', 'encore', 'celles', 'de', 'personnalités', 'telles', 'que', 'brad', 'pitt', 'kanye', 'west', 'ian', 'schrager', 'et', 'adam', 'lindemann', 'il', 'est', 'également', 'en', 'contrat', 'avec', 'louis', 'vuitton', 'swarovski', 'gramercy', 'park', 'hotel', 'dior', 'dom', 'ruinard', 'et', 'berlutti', "l'", 'exposition', 'de', 'la', 'carpenters', 'workshops', 'gallery', 'vous', 'propose', 'ainsi', 'de', 'découvrir', "l'", 'œuvre', 'essentielle', "d'", 'un', 'des', 'plus', 'importants', 'designers', 'contemporains']

print(words)
# #---to run all the spiders, uncomment the following line
# #run_spiders()

# #---to get merged result of scraped data, uncomment the following line
# #append_to_full(merge_results("backend/exhibition/expo_scraper/extracted_data/all_expo.jsonl"))


# #---to create the reverse index for words, uncomment the following line
# c = create_collection()
# a = aggregate(c)
# with open('backend/exhibition/index_word.json', 'w') as outfile :
#     json.dump(a, outfile)
# print("the index contains {} words".format(len(a)))

# #---to create the document (exhibition) length index , uncomment the following line    
# doc_vector_length()