import re
import json
from math import log10, sqrt
from nltk.probability import FreqDist
import regex as re
import treetaggerwrapper as ttw 

tagger = ttw.TreeTagger(TAGLANG='fr')
stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read()

with open('backend/exhibition/data_exhibition.json', 'r') as f:
    DB = json.load(f)

def create_collection():

    collection = []

    for elt in DB:
        # lower some bits because TreeTagger lemmatizes according to both caps and full stops
        text = elt['title'].lower() +". "+ elt['summary'] +". "+ elt['reviews'] +". "+ str(elt['genre']).lower() +". "+ str(elt['tags']).lower() +". "+ elt['location']
        terms = tf_text(text, elt['ID'])
        collection += terms
    
    s_list = sorted(collection)

    return s_list

def tf_text(text_title_summary_reviews, docID):
    """ Returns a list of filtered terms: (term, (docID, tf/sqrt(len(keywords)))) """

    tags = tagger.tag_text(re.sub(r"[^\w+ \' \.]", " ", text_title_summary_reviews))
    tags2 = ttw.make_tags(tags)

    keywords =[]
    fdist = FreqDist()

    for elt in tags2:
        try:
            if not elt.lemma.lower() in stopwords:
                keywords.append(elt.lemma.lower())
        except:
            pass

    fdist = FreqDist(keywords)
    result = [(x[0],( docID, (1+log10(x[1])) / sqrt(len(keywords)) )) for x in fdist.items()]

    return result

def aggregate(full_collection_terms):
    """ Creates the reverse index: list of (term, collection_freq, [posting_list: (docID, tf-idf)]) """

    term = [(x[0], 1, [x[1]]) for x in full_collection_terms]
    
    d =[term[0]]
    for i in range (1, len(term)):
        if term[i][0] != term[i-1][0]:
            d.append(term[i])
        else:
            d[len(d)-1] = (d[len(d)-1][0], d[len(d)-1][1] + 1, d[len(d)-1][2] + term[i][2])

    result = []
    for elt in d:
        term = [elt[0], elt[1], []]
        for posting in elt[2]:
            r = posting[0], posting[1] * log10( len(DB) / elt[1] )
            term[2].append(r)
        result.append(term)

    return result

def doc_vector_length():
    """ Create json file with exhibition vectors length = sum( (tf-idf)² ) """

    with open('backend/exhibition/index_word.json', 'r') as f:
        index = json.load(f)
    
    doc_index = {}
    for elt in DB :
        doc_index[elt["ID"]] = 0

    for word in index:
        postings = word[2]
        for doc in postings:
            doc_index[doc[0]] += doc[1] ** 2            

    with open('backend/exhibition/index_doc.json', 'w') as outfile :
        json.dump(doc_index, outfile)

if __name__ == "__main__":
    
    #---to create the reverse index for words, uncomment the following line
    c = create_collection()
    a = aggregate(c)
    with open('backend/exhibition/index_word.json', 'w') as outfile :
        json.dump(a, outfile)
    print("the index contains {} words".format(len(a)))

    #---to create the document (exhibition) length index , uncomment the following line    
    doc_vector_length()