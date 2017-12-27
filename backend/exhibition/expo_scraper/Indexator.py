import re
import json
from math import log10
from nltk.probability import FreqDist
import treetaggerwrapper as ttw 

tagger = ttw.TreeTagger(TAGLANG='fr')
stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read()

def create_collection():

    with open('backend/exhibition/data_exhibition.json', 'r') as f:
        db = json.load(f)
    collection = []

    for elt in db:
        text = elt['title'] + elt['summary'] + elt['reviews']
        terms = tf_text(text.lower(), elt['id'])
        collection += terms
    
    s_list = sorted(collection)

    return s_list

def tf_text(text_title_summary_reviews, docID):
    """ Returns a list of filtered terms: (term, (docID, tf)) """

    tags = tagger.tag_text(text_title_summary_reviews)
    tags2 = ttw.make_tags(tags)

    keywords =[]
    fdist = FreqDist()

    for elt in tags2:
        try:
            if not elt.lemma.lower() in stopwords:
                keywords.append(elt.lemma)
        except:
            pass

    fdist = FreqDist(keywords)
    result = [(x[0],(docID, 1+log10(x[1]))) for x in fdist.items()]

    return result

def aggregate(full_collection_terms):
    """ Creates the reverse index: list of (term, collection_freq, [posting_list: (docID, tf-idf)]) """

    term = [(x[0], 1, [x[1]]) for x in full_collection_terms]
    
    d =[term[0]]
    for i in range (1, len(term)):
        if term[i][0] != term[i-1][0]:
            d.append(term[i])
        else:
            print()
            d[len(d)-1] = (d[len(d)-1][0], d[len(d)-1][1] + 1, d[len(d)-1][2] + term[i][2])

    result = []
    for elt in d:
        term = [elt[0], elt[1], []]
        for posting in elt[2]:
            r = posting[0], posting[1] * log10( len(d) / elt[1] )
            term[2].append(r)
        result.append(term)

    return result

if __name__ == "__main__":
    
    c = create_collection()
    a = aggregate(c)
    
    with open('backend/exhibition/index.json', 'w') as outfile :
        json.dump(a, outfile)
    print("the index contains {} words".format(len(a)))

