import treetaggerwrapper as ttw 
from backend.language.handle_emoji import convert_string
from pprint import pprint	

tagger = ttw.TreeTagger(TAGLANG='fr')

GREETINGS = ('salut', 'bonjour', 'coucou', 'yo', 'hello', 'hi', 'hey', 'ola')
CINEMA = ('ciné', 'cine', 'cinéma', 'cinema', 'film')
EXHIBITION = ('expo', 'exposition', 'musée', 'musee', 'gallerie', '')
EXIT = ('stop', 'merci')

def process_text(msg):
    """ Input: str or list / Output: list of named tuples containing the POS tag and lemma of each word """
    tags = tagger.tag_text(convert_string(msg)[0])
    tags2 = ttw.make_tags(tags)

    return tags2

def analyse_text(word_list):
    """ Records all keywords that triggers an action. So far: greeting / cinema / exhibition / exit """

    keywords = [0,0,0,0]
    for elt in word_list:
        if elt.lemma in GREETINGS:
            keywords[0] = 1
        elif elt.lemma in CINEMA:
            keywords[1] = 1
        elif elt.lemma in EXHIBITION:
            keywords[2] = 1
        elif elt.lemma in EXIT:
            keywords[3] = 1

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