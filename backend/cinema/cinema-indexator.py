import re
import json
from math import log10, sqrt
from nltk.probability import FreqDist
import regex as re
import treetaggerwrapper as ttw

tagger = ttw.TreeTagger(TAGLANG='fr')
stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read().split("\n")

with open('backend/cinema/cinema_allocine.json', 'r') as f:
    DB = json.load(f)


def create_collection_cine():
    collection = []

    for elt in DB:
        # lower some bits because TreeTagger lemmatizes according to both caps and full stops
        text = elt['title'].lower() + ". " + elt['critique_1'] + ". " + elt['critique_2']
        terms = tf_text(text, elt['ID'])
        collection += terms

    s_list = sorted(collection)

    return s_list