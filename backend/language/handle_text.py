from backend.language.handle_emoji import convert_string
from pprint import pprint	

GREETINGS = ('salut', 'bonjour', 'coucou', 'yo', 'hello', 'hi', 'hey', 'ola')
CINEMA = ('ciné', 'cine', 'cinéma', 'cinema', 'film')
EXHIBITION = ('expo', 'exposition', 'musée', 'musee', 'gallerie', 'art', 'artiste')
EXIT = ('stop', 'merci')
THANKS = ('cimer', 'cool', 'okay', 'k', 'ok')

def process_text(msg, tagger):
    """ Input: str or list / Output: list of named tuples containing the POS tag and lemma of each word """
    tags = tagger.tag_text(convert_string(msg)[0])
    tags2 = [word.split("\t") for word in tags]

    return tags2

def analyse_text(word_list):
    """ Records all keywords that triggers an action. So far: greeting / cinema / exhibition / exit """

    keywords = [0,0,0,0,0]
    for elt in word_list:
        if elt[2] in GREETINGS:
            keywords[0] = 1
        elif elt[2] in CINEMA:
            keywords[1] = 1
        elif elt[2] in EXHIBITION:
            keywords[2] = 1
        elif elt[2] in EXIT:
            keywords[3] = 1
        elif elt[2] in THANKS:
            keywords[4] = 1

    return keywords

def get_meaning(msg, tagger):
    """ combines process and analyse fct. outputs presence vector x=[0,0,0,0] with 
            x[0]: greetings / x[1]: cinema / x[2]: exhibition / x[3]: exit """
    
    p = process_text(msg, tagger)

    return analyse_text(p)


if __name__ == "__main__":

    import treetaggerwrapper as ttw 
    tagger = ttw.TreeTagger(TAGLANG='fr')
    
    s = "salut salt ;) j'aime les expos d'art contemporain et le cinéma ⛄ 🤞 ❤️ ...".lower()

    a = get_meaning(s, tagger)
    print(a)