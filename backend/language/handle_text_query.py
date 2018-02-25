import json
import pickle
from nltk.probability import FreqDist
import regex as re
from math import log10, sqrt
from pprint import pprint

stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read().split("\n")

with open('backend/exhibition/index_word.json', 'r') as f:
    INDEX_DATA = json.load(f)
    
with open('backend/exhibition/index_doc.json', 'r') as f:
    DOC_LENGTH = json.load(f)

with open('backend/exhibition/data_exhibition.json', 'r') as f:
    COLLECTION = json.load(f)
COLLECTION_IDS = range(1, len(DOC_LENGTH)+1)

def tf_text(text_title_summary_reviews, docID, tagger):
    """ Returns a list of filtered terms: (term, (docID, tf/sqrt(len(keywords)))) """

    tags = tagger.tag_text(re.sub(r"[^\w+ \' \.]", " ", text_title_summary_reviews))
    tags2 = [word.split("\t") for word in tags]

    keywords =[]
    fdist = FreqDist()

    for elt in tags2:
        try:
            if not elt[2].lower() in stopwords:
                keywords.append(elt[2].lower())
        except:
            pass

    fdist = FreqDist(keywords)
    result = [(x[0],( docID, (1+log10(x[1])) / sqrt(len(keywords)) )) for x in fdist.items()]

    return result



def get_postings(word):
    """ Returns a tuple (postings (with tf-idf), postings) if word in index """
    try: 
        doc_tfidf = [ list(x[2]) for x in INDEX_DATA if x[0] == word ][0]
        postings = [ docID[0] for docID in doc_tfidf ]
    except:
        doc_tfidf = [[0, 0]]
        postings = []
        #print("No exact match for word '{}'.".format(word))
        pass
    
    return doc_tfidf, postings


def vect_search(query, tagger, rappel=20):
    
    # Calculates (1+log10(tf)) for each word in the query
    q = tf_text(query, 0, tagger)
    n_q = 0
    sim = {}
    for i in COLLECTION_IDS:
        sim[i] =  0

    for i in range(len(q)):
        postings = get_postings(q[i][0])[0]  
        try:
            w_q = q[i][1][1] / sqrt(len(q))
        except ZeroDivisionError:
            w_q = 0
        #print("mot: {} - in {} docs - poids: {}".format(q[i], len(postings), w_q))
        n_q += w_q ** 2

        if postings != [[0, 0]]:
            for doc in postings:
                w_doc = doc[1]      # calculation (tf-idf) already done during indexation
                sim[doc[0]] += w_doc * w_q

    for j, value in sim.items():
        n_d = DOC_LENGTH[str(j)]
        if value != 0:
            value = value / ( sqrt( n_q * n_d ) ) 

    temp = []
    dictList = []

    for key, value in sim.items():
        temp = (key,value)
        dictList.append(temp)
    s = sorted(dictList, key=lambda x:x[1], reverse=True)[:rappel]

    # RESULT just to check results
    # result = []
    # for elt in s :
    #     result.append((COLLECTION[elt[0]-1]["title"], "weight: {}".format(round(elt[1], 2))))
    
    return [str(x[0]) for x in s]   #, result

if __name__ == "__main__":
    print(get_postings("Marions"))