#Not enough exhibs on danse(2), musique(3)

import pandas as pd
import numpy as np
import treetaggerwrapper as ttw 

tagger = ttw.TreeTagger(TAGLANG='fr')

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier

from sklearn.externals import joblib

from sklearn.model_selection import GridSearchCV, cross_val_score

def lemmatize(doc):
    tags = tagger.tag_text(doc)
    with_lemma = [x for x in tags if len(x.split('\t'))>2 ]
    return " ".join([x.split('\t')[2] for x in with_lemma])

data = pd.read_json("backend/exhibition/data_exhibition.json")
input_d = data['title']+" "+ data['reviews']+" "+ data['summary']+" "+ data['location']+" "+ data['tags'].apply(lambda x: str(x)*4)

# if problem with data type, use --> .apply(lambda x: str(x))
input_d = input_d.apply(func = lemmatize)
output_d = data[['Architecture', 'Sculpture', 'Peinture', 'Musique',
       'Littérature', 'Danse', 'Cinéma', 'Photographie', 'Mode',
       'Beaux-Arts', 'Art contemporain', 'Histoire / Civilisations',
       'Famille']]

stopwords = open("backend/exhibition/expo_scraper/expo_classifiers/title_stopwords.txt", 'r', encoding='utf-8').read().split("\n")

clf = Pipeline([('vect', CountVectorizer(stop_words=stopwords)), 
                         ('tfidf', TfidfTransformer()), 
                         ('clf', SGDClassifier(loss='modified_huber', 
                                               penalty='l1',
                                               alpha=1e-3, 
                                               random_state=42, 
                                               max_iter=1000))])

for elt in output_d.columns.values:
    clf.fit(input_d, output_d[elt])
    name = elt.replace(' / ', '_').replace(' ', '_')
    joblib.dump(clf, 'backend/exhibition/expo_scraper/expo_classifiers/classifier_{}.pkl'.format(name))
    #s = cross_val_score(clf, input_d, output_d[elt], cv =5)
    #print("prediction {} : {}".format(elt, str(np.mean(s))))
