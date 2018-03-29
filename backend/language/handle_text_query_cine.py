import json
import pickle
from nltk.probability import FreqDist
import nltk
from math import log10, sqrt
from pprint import pprint

stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read().split("\n")

with open('backend/cinema/index_word_cine.json', 'r') as f:
    INDEX_DATA = json.load(f)

with open('backend/cinema/index_doc_cine.json', 'r') as f:
    DOC_LENGTH = json.load(f)

with open('backend/cinema/cinema_full.json', 'r') as f:
    COLLECTION = json.load(f)
# In index_doc, we only have current exhibition, so IDs can be high
COLLECTION_IDS = [x for x in DOC_LENGTH.keys()]

LEMMA_DIC = {"'": "lemma/first_letter_'.json", '-': 'lemma/first_letter_-.json', 'a': 'lemma/first_letter_a.json', 'b': 'lemma/first_letter_b.json', 'c': 'lemma/first_letter_c.json', 'd': 'lemma/first_letter_d.json', 'e': 'lemma/first_letter_e.json', 'f': 'lemma/first_letter_f.json', 'g': 'lemma/first_letter_g.json', 'h': 'lemma/first_letter_h.json', 'i': 'lemma/first_letter_i.json', 'j': 'lemma/first_letter_j.json', 'k': 'lemma/first_letter_k.json', 'l': 'lemma/first_letter_l.json', 'm': 'lemma/first_letter_m.json', 'n': 'lemma/first_letter_n.json', 'o': 'lemma/first_letter_o.json', 'p': 'lemma/first_letter_p.json', 'q': 'lemma/first_letter_q.json', 'r': 'lemma/first_letter_r.json', 's': 'lemma/first_letter_s.json', 't': 'lemma/first_letter_t.json', 'u': 'lemma/first_letter_u.json', 'v': 'lemma/first_letter_v.json', 'w': 'lemma/first_letter_w.json', 'y': 'lemma/first_letter_y.json', 'z': 'lemma/first_letter_z.json', 'x': 'lemma/first_letter_x.json', '£': 'lemma/first_letter_pound.json', 'é': 'lemma/first_letter_a_down.json', 'à': 'lemma/first_letter_a_circ.json', 'â': 'lemma/first_letter_c_ced.json', 'ç': 'lemma/first_letter_e_down.json', 'è': 'lemma/first_letter_i_circ.json', 'ê':
'lemma/first_letter_i_trema.json', 'î': 'lemma/first_letter_o_circ.json'}

def tf_text(request, docID):
    """ Returns a list of filtered terms: (term, (docID, tf/sqrt(len(keywords)))) """
    
    pattern = r'''(?x)              # set flag to allow verbose regexps
            aujourd'hui             # exception 1
            | prud'hom\w+           # exception 2
            | \w'                   # contractions d', l', j', t', s'
            | \d+(?:,\d+)?%?€?      # currency and percentages, e.g. 12,40€, 82%        
            | (?:[A-Z]\.)+          # abbreviations, e.g. U.S.A.
            | \w+(?:-\w+)*          # words with optional internal hyphens
            #| [][.,;"'?():_`-]     # these are separate tokens; includes ], [
        '''
    
    words = [x.lower() for x in nltk.regexp_tokenize(request, pattern)]

    keywords = []
    fdist = FreqDist()

    for elt in words:

        with open("backend/language/"+LEMMA_DIC[elt[0]]) as json_data:
            d = json.load(json_data)
        try: # on prend le 1e lemma possible meme si ça peut etre faux (ex: abstrait -> abstraire (verbe))
            lemma = [x[0] for x in d if x[0][0] == elt][0][1]
        except:
            with open("backend/language/lemma/missing.txt", "a") as f:
                f.write(elt+"\n")

        if not lemma in stopwords:
            keywords.append(lemma)

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


def vect_search_cine(query):
    """ :param query: full text query\n
    :return: list of doc IDs ranked by highest proximity
    """

    # Calculates (1+log10(tf)) for each word in the query
    q = tf_text(query, 0)
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
    s = sorted(dictList, key=lambda x:x[1], reverse=True)

    # RESULT just to check results
    # result = []
    # for elt in s :
    #     result.append((COLLECTION[elt[0]-1]["title"], "weight: {}".format(round(elt[1], 2))))
    
    return [x[0] for x in s]   #, result

if __name__ == "__main__":
    print(vect_search_cine("un film d'action avec Spielberg"))