from backend.messenger.msg_fct import send_msg, send_card, send_quick_rep, start_buttons
from backend.language.handle_emoji import convert_string
from backend.exhibition.handle_expo import get_genre_exhib, get_exhib, get_exhib_query, get_detail_exhib
from backend.cinema.handle_cinema import get_details_cinema
from backend.language.handle_text_query import vect_search

from pprint import pprint
import random	
import json
import nltk
import time

GREETINGS = ('salut', 'bonjour', 'coucou', 'yo', 'hello', 'hi', 'hey', 'ola')
CINEMA = ('ciné', 'cine', 'cinéma', 'cinema', 'film')
EXHIBITION = ('exposition', 'musée', 'musee', 'gallerie', 'art', 'artiste',)
EXHIB_GENRE = ('architecture', 'sculpture', 'peinture', 'musique', 'littérature', 'danse', 'photographie', 'mode', 'beaux-arts', 'contemporain', 'histoire','civilisation', 'famille')
EXIT = ('stop', 'tchao' 'bye')
THANKS = ('merci', 'cimer', 'cool', 'okay', 'k', 'ok')
HELP = ('help', 'aide')
MENU = ('menu')

with open('backend/language/sentences_DB.json') as f:
    SENTENCES = json.load(f)

def process_text(msg):
    """ Input: str or list / Output: list of named tuples containing the POS tag and lemma of each word """
    
    LEMMA_DIC = {"'": "lemma/first_letter_'.json", '-': 'lemma/first_letter_-.json', 'a': 'lemma/first_letter_a.json', 'b': 'lemma/first_letter_b.json', 'c': 'lemma/first_letter_c.json', 'd': 'lemma/first_letter_d.json', 'e': 'lemma/first_letter_e.json', 'f': 'lemma/first_letter_f.json', 'g': 'lemma/first_letter_g.json', 'h': 'lemma/first_letter_h.json', 'i': 'lemma/first_letter_i.json', 'j': 'lemma/first_letter_j.json', 'k': 'lemma/first_letter_k.json', 'l': 'lemma/first_letter_l.json', 'm': 'lemma/first_letter_m.json', 'n': 'lemma/first_letter_n.json', 'o': 'lemma/first_letter_o.json', 'p': 'lemma/first_letter_p.json', 'q': 'lemma/first_letter_q.json', 'r': 'lemma/first_letter_r.json', 's': 'lemma/first_letter_s.json', 't': 'lemma/first_letter_t.json', 'u': 'lemma/first_letter_u.json', 'v': 'lemma/first_letter_v.json', 'w': 'lemma/first_letter_w.json', 'y': 'lemma/first_letter_y.json', 'z': 'lemma/first_letter_z.json', 'x': 'lemma/first_letter_x.json', '£': 'lemma/first_letter_pound.json', 'é': 'lemma/first_letter_a_down.json', 'à': 'lemma/first_letter_a_circ.json', 'â': 'lemma/first_letter_c_ced.json', 'ç': 'lemma/first_letter_e_down.json', 'è': 'lemma/first_letter_i_circ.json', 'ê':
'lemma/first_letter_i_trema.json', 'î': 'lemma/first_letter_o_circ.json'}
    
    pattern = r'''(?x)              # set flag to allow verbose regexps
            aujourd'hui             # exception 1
            | prud'hom\w+           # exception 2
            | \w'                   # contractions d', l', j', t', s'
            | \d+(?:,\d+)?%?€?      # currency and percentages, e.g. 12,40€, 82%        
            | (?:[A-Z]\.)+          # abbreviations, e.g. U.S.A.
            | \w+(?:-\w+)*          # words with optional internal hyphens
            #| [][.,;"'?():_`-]     # these are separate tokens; includes ], [
        '''
    
    words = [x.lower() for x in nltk.regexp_tokenize(msg, pattern)]
    
    keywords = []

    for elt in words:
        with open("backend/language/"+LEMMA_DIC[elt[0]]) as json_data:
            d = json.load(json_data)
        try: # on prend le 1e lemma possible meme si ça peut etre faux (ex: abstrait -> abstraire (verbe))
            tags = [x[0] for x in d if x[0][0] == elt][0]
            keywords.append(tags)
        except:
            with open("backend/language/lemma/missing.txt", "a") as f:
                f.write(elt+"\n")
            keywords.append( (elt, elt, "UKN") )

    return keywords

def analyse_text(msg, sender, user, ACCESS_TOKEN):
    """ Records all keywords that triggers an action. So far: greeting / cinema / exhibition / exit / help """

    word_list = process_text(msg)
    cinema = False
    # system : [greetings, cinema, exhibition, exit, thanks,
    keys = [0,0,0,0,0,0,0]
    
    for elt in word_list:
        if elt[1] in GREETINGS: keys[0] = 1
        elif elt[1] in CINEMA: keys[1] = 1
        elif elt[1] in EXHIBITION or elt[1] in EXHIB_GENRE: keys[2] = 1
        elif elt[1] in EXIT: keys[3] = 1
        elif elt[1] in THANKS: keys[4] = 1
        elif elt[1] in HELP : keys[5] = 1
        elif elt[1] in MENU : keys[6] = 1

    if keys[0] :
        time.sleep(1)
        start_buttons(sender, random.choice(SENTENCES["GREETINGS"]).format(user[1]), ACCESS_TOKEN)

    elif keys[1]:
        # ATTENTION parce qu'on ne pouvait pas importer les fonctions du serveur, c'est la seule 
        # action pas gérée ici mais dans le serveur.
        cinema = True

    elif keys[2]:
        time.sleep(1)

        filter_exhib = [w for w in word_list if w in EXHIB_GENRE] 
        if not filter_exhib: filter_exhib = ["all"]     

        send_msg(sender, random.choice(SENTENCES['EXHIBITIONS']), ACCESS_TOKEN)
        send_card(sender, get_exhib_query(vect_search(msg), filter_exhib, 1), ACCESS_TOKEN)

    elif keys[3]:
        send_msg(sender, random.choice(SENTENCES["EXIT"]), ACCESS_TOKEN)

    elif keys[4]:
        send_msg(sender, random.choice(SENTENCES["THANKS"]), ACCESS_TOKEN)

    elif keys[5]:
        send_msg(sender, "======= HELP =======\n\n\
A tout moment tu peux me demander des choses comme \'Est ce qu'il y a des expos d'art moderne ?\' ou \
\'donne moi le meilleur film comique au ciné\'\n\n\
Si tu préfères être guidé, tape 'menu' et des boutons apparaîtront !", ACCESS_TOKEN) 
    
    elif keys[6]:
        start_buttons(sender, "Qu'est-ce qui t'intéresserait ?", ACCESS_TOKEN)

    elif keys == [0,0,0,0,0,0,0]:
        send_msg(sender, random.choice(SENTENCES["UNKNOWN"]), ACCESS_TOKEN)
        send_msg(sender, "Mais si tu as besoin d'aide, tape 'help'. Sinon pour accéder au menu, tape 'menu' :)", ACCESS_TOKEN)
        with open("misunderstood_sentences.txt", "a") as f:
            f.write(msg + "\n")

    return cinema 



if __name__ == "__main__":
    
    s = "salut salt ;) j'aime les expos d'art contemporain et le cinéma ⛄ 🤞 ❤️ ...".lower()

    a = analyse_text(s, "na", ["na", "na","na"], "na")
    print(a)