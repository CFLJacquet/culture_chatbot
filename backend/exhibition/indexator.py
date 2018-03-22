import re
import json
from math import log10, sqrt
from nltk.probability import FreqDist
import nltk
import regex as re
import unidecode

from datetime import datetime as dt

from backend.exhibition.expo_scraper.handle_exhibition_data import run_spiders, append_to_full, merge_results

stopwords = open("backend/language/stopwords.txt", 'r', encoding='utf-8').read().split("\n")
LEMMA_DIC = {"'": "lemma/first_letter_'.json", '-': 'lemma/first_letter_-.json', 'a': 'lemma/first_letter_a.json',
             'b': 'lemma/first_letter_b.json', 'c': 'lemma/first_letter_c.json', 'd': 'lemma/first_letter_d.json',
             'e': 'lemma/first_letter_e.json', 'f': 'lemma/first_letter_f.json', 'g': 'lemma/first_letter_g.json',
             'h': 'lemma/first_letter_h.json', 'i': 'lemma/first_letter_i.json', 'j': 'lemma/first_letter_j.json',
             'k': 'lemma/first_letter_k.json', 'l': 'lemma/first_letter_l.json', 'm': 'lemma/first_letter_m.json',
             'n': 'lemma/first_letter_n.json', 'o': 'lemma/first_letter_o.json', 'p': 'lemma/first_letter_p.json',
             'q': 'lemma/first_letter_q.json', 'r': 'lemma/first_letter_r.json', 's': 'lemma/first_letter_s.json',
             't': 'lemma/first_letter_t.json', 'u': 'lemma/first_letter_u.json', 'v': 'lemma/first_letter_v.json',
             'w': 'lemma/first_letter_w.json', 'y': 'lemma/first_letter_y.json', 'z': 'lemma/first_letter_z.json',
             'x': 'lemma/first_letter_x.json', '£': 'lemma/first_letter_pound.json',
             'é': 'lemma/first_letter_a_down.json', 'à': 'lemma/first_letter_a_circ.json',
             'â': 'lemma/first_letter_c_ced.json', 'ç': 'lemma/first_letter_e_down.json',
             'è': 'lemma/first_letter_i_circ.json', 'ê':
                 'lemma/first_letter_i_trema.json', 'î': 'lemma/first_letter_o_circ.json'}

LOADED_LEMMA = {}
for elt in LEMMA_DIC:
    with open("backend/language/" + LEMMA_DIC[elt]) as json_data:
        LOADED_LEMMA[elt] = json.load(json_data)

with open('backend/exhibition/data_exhibition.json', 'r') as f:
    DB = [elt for elt in json.load(f) if dt.strptime(elt['d_end'], "%Y-%m-%d") >= dt.today()]


def create_collection():
    """ only considers current exhibition """

    collection = []
    temp = 0
    for elt in DB:
        text = elt['title'].lower() + ". " + elt['summary'] + ". " + elt['reviews'] + ". " + str(
            elt['genre']).lower() + ". " + str(elt['tags']).lower() + ". " + elt['location']
        terms = tf_text(text, elt['ID'])
        collection += terms
        temp += 1
        if temp % 10 == 0: print('doc {}/{}'.format(temp, len(DB)))

    s_list = sorted(collection)

    return s_list


def tf_text(text_title_summary_reviews, docID):
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

    words = nltk.regexp_tokenize(text_title_summary_reviews.lower(), pattern)

    keywords = []
    fdist = FreqDist()

    for elt in words:
        if elt[0] in LOADED_LEMMA:
            try:  # on prend le 1e lemma possible meme si ça peut etre faux (ex: abstrait -> abstraire (verbe))
                lemma = [x[0] for x in LOADED_LEMMA[elt[0]] if x[0][0] == elt][0][1]
            except:
                with open("backend/language/lemma/missing.txt", "a") as f:
                    f.write(unidecode.unidecode(elt) + "\n")
                lemma = elt

            if not lemma in stopwords:
                keywords.append(lemma)

    fdist = FreqDist(keywords)
    result = [(x[0], (docID, (1 + log10(x[1])) / sqrt(len(keywords)))) for x in fdist.items()]

    return result


def aggregate(full_collection_terms):
    """ Creates the reverse index: list of (term, collection_freq, [posting_list: (docID, tf-idf)]) """

    term = [(x[0], 1, [x[1]]) for x in full_collection_terms]

    d = [term[0]]
    for i in range(1, len(term)):
        if term[i][0] != term[i - 1][0]:
            d.append(term[i])
        else:
            d[len(d) - 1] = (d[len(d) - 1][0], d[len(d) - 1][1] + 1, d[len(d) - 1][2] + term[i][2])

    result = []
    for elt in d:
        term = [elt[0], elt[1], []]
        for posting in elt[2]:
            r = posting[0], posting[1] * log10(len(DB) / elt[1])
            term[2].append(r)
        result.append(term)
    print("Fin agrégation")
    return result


def doc_vector_length():
    """ Create json file with exhibition vectors length = sum( (tf-idf)² ) """

    with open('backend/exhibition/index_word.json', 'r') as f:
        index = json.load(f)

    doc_index = {}
    for elt in DB:
        doc_index[elt["ID"]] = 0

    for word in index:
        postings = word[2]
        for doc in postings:
            doc_index[doc[0]] += doc[1] ** 2

    with open('backend/exhibition/index_doc.json', 'w') as outfile:
        json.dump(doc_index, outfile)
    print('Fin doc index creation')


if __name__ == "__main__":
    # ---to run all the spiders, uncomment the following line
    # run_spiders()

    # ---to get merged result of scraped data, uncomment the following line
    # append_to_full(merge_results("backend/exhibition/expo_scraper/extracted_data/all_expo.jsonl"))


    # ---to create the reverse index for words, uncomment the following line
    c = create_collection()
    a = aggregate(c)
    with open('backend/exhibition/index_word.json', 'w') as outfile:
        json.dump(a, outfile)
    print("the index contains {} words".format(len(a)))

    # ---to create the document (exhibition) length index , uncomment the following line
    doc_vector_length()