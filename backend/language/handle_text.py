from backend.language.handle_emoji import convert_string
from pprint import pprint	
import json
import nltk

GREETINGS = ('salut', 'bonjour', 'coucou', 'yo', 'hello', 'hi', 'hey', 'ola')
CINEMA = ('ciné', 'cine', 'cinéma', 'cinema', 'film')
EXHIBITION = ('expo', 'exposition', 'musée', 'musee', 'gallerie', 'art', 'artiste')
EXIT = ('stop', 'merci')
THANKS = ('cimer', 'cool', 'okay', 'k', 'ok')
HELP = ('help', 'aide')
MENU = ('menu')

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

def analyse_text(word_list):
    """ Records all keywords that triggers an action. So far: greeting / cinema / exhibition / exit / help """

    keywords = [0,0,0,0,0,0,0]
    for elt in word_list:
        if elt[1] in GREETINGS:
            keywords[0] = 1
        elif elt[1] in CINEMA:
            keywords[1] = 1
        elif elt[1] in EXHIBITION:
            keywords[2] = 1
        elif elt[1] in EXIT:
            keywords[3] = 1
        elif elt[1] in THANKS:
            keywords[4] = 1
        elif elt[1] in HELP and len(word_list) == 1:
            keywords[5] = 1
        elif elt[1] in MENU and len(word_list) == 1:
            keywords[6] = 1

    return keywords

def get_meaning(msg):
    """ combines process and analyse fct. outputs presence vector x=[0,0,0,0] with 
            x[0]: greetings / x[1]: cinema / x[2]: exhibition / x[3]: exit """
    
    p = process_text(msg)

    return analyse_text(p)


if __name__ == "__main__":
    
    s = "salut salt ;) j'aime les expos d'art contemporain et le cinéma ⛄ 🤞 ❤️ ...".lower()

    a = get_meaning(s)
    print(a)