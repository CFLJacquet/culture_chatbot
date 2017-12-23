import unicodedata as ud
import json
import pickle

#Note: Needed to put part of the emoji list in the main file because it couldn't be converted into unicode description
#Note2: "❤️" == "\u2764\uFE0F" -> coded on 2 unicode codepoints

data1 = [{"img": "✌", "name": "victory hand", "negative": "0.113", "neutral": "0.310", "positive": "0.576", "sentiment": "0.463"},
{"img": "✨", "name": "sparkles", "negative": "0.052", "neutral": "0.545", "positive": "0.403", "sentiment": "0.351"},
{"img": "☕", "name": "hot beverage", "negative": "0.140", "neutral": "0.475", "positive": "0.384", "sentiment": "0.244"},
{"img": "✋", "name": "raised hand", "negative": "0.328", "neutral": "0.218", "positive": "0.454", "sentiment": "0.126"},
{"img": "⚽", "name": "soccer ball", "negative": "0.053", "neutral": "0.278", "positive": "0.669", "sentiment": "0.616"},
{"img": "✊", "name": "raised fist", "negative": "0.139", "neutral": "0.293", "positive": "0.568", "sentiment": "0.429"},
{"img": "⚡", "name": "high voltage sign", "negative": "0.044", "neutral": "0.735", "positive": "0.221", "sentiment": "0.177"},
{"img": "❗", "name": "heavy exclamation mark symbol", "negative": "0.159", "neutral": "0.582", "positive": "0.259", "sentiment": "0.100"},
{"img": "☝", "name": "white up pointing index", "negative": "0.144", "neutral": "0.402", "positive": "0.454", "sentiment": "0.309"},
{"img": "⛄", "name": "snowman without snow", "negative": "0.077", "neutral": "0.325", "positive": "0.598", "sentiment": "0.521"},
{"img": "⭐", "name": "white medium star", "negative": "0.037", "neutral": "0.346", "positive": "0.617", "sentiment": "0.580"},
{"img": "☔", "name": "umbrella with rain drops", "negative": "0.193", "neutral": "0.325", "positive": "0.482", "sentiment": "0.289"},
{"img": "⛔", "name": "no entry", "negative": "0.088", "neutral": "0.338", "positive": "0.574", "sentiment": "0.485"},
{"img": "❌", "name": "cross mark", "negative": "0.254", "neutral": "0.220", "positive": "0.525", "sentiment": "0.271"},
{"img": "✅", "name": "white heavy check mark", "negative": "0.074", "neutral": "0.444", "positive": "0.481", "sentiment": "0.407"},
{"img": "❓", "name": "black question mark ornament", "negative": "0.182", "neutral": "0.568", "positive": "0.250", "sentiment": "0.068"},
{"img": "⚪", "name": "medium white circle", "negative": "0.025", "neutral": "0.500", "positive": "0.475", "sentiment": "0.450"},
{"img": "⛅", "name": "sun behind cloud", "negative": "0.125", "neutral": "0.300", "positive": "0.575", "sentiment": "0.450"},
{"img": "⚓", "name": "anchor", "negative": "0.086", "neutral": "0.257", "positive": "0.657", "sentiment": "0.571"},
{"img": "➕", "name": "heavy plus sign", "negative": "0.147", "neutral": "0.176", "positive": "0.676", "sentiment": "0.529"},
{"img": "⛽", "name": "fuel pump", "negative": "0.061", "neutral": "0.727", "positive": "0.212", "sentiment": "0.152"},
{"img": "⚾", "name": "baseball", "negative": "0.370", "neutral": "0.296", "positive": "0.333", "sentiment": "-0.037"},
{"img": "⌚", "name": "watch", "negative": "0.150", "neutral": "0.500", "positive": "0.350", "sentiment": "0.200"},
{"img": "⛲", "name": "fountain", "negative": "0.111", "neutral": "0.722", "positive": "0.167", "sentiment": "0.056"},
{"img": "⚫", "name": "medium black circle", "negative": "0.235", "neutral": "0.294", "positive": "0.471", "sentiment": "0.235"},
{"img": "⏰", "name": "alarm clock", "negative": "0.188", "neutral": "0.188", "positive": "0.625", "sentiment": "0.438"},
{"img": "⛪", "name": "church", "negative": "0.188", "neutral": "0.500", "positive": "0.313", "sentiment": "0.125"},
{"img": "⛺", "name": "tent", "negative": "0.154", "neutral": "0.231", "positive": "0.615", "sentiment": "0.462"},
{"img": "❔", "name": "white question mark ornament", "negative": "0.333", "neutral": "0.333", "positive": "0.333", "sentiment": "0.000"},
{"img": "➰", "name": "curly loop", "negative": "0.455", "neutral": "0.182", "positive": "0.364", "sentiment": "-0.091"},
{"img": "⛳", "name": "flag in hole", "negative": "0.091", "neutral": "0.182", "positive": "0.727", "sentiment": "0.636"},
{"img": "⏳", "name": "hourglass with flowing sand", "negative": "0.400", "neutral": "0.200", "positive": "0.400", "sentiment": "0.000"},
{"img": "♎", "name": "libra", "negative": "0.300", "neutral": "0.500", "positive": "0.200", "sentiment": "-0.100"},
{"img": "⛵", "name": "sailboat", "negative": "0.100", "neutral": "0.300", "positive": "0.600", "sentiment": "0.500"},
{"img": "⌛", "name": "hourglass", "negative": "0.300", "neutral": "0.300", "positive": "0.400", "sentiment": "0.100"},
{"img": "❕", "name": "white exclamation mark ornament", "negative": "0.200", "neutral": "0.400", "positive": "0.400", "sentiment": "0.200"},
{"img": "♌", "name": "leo", "negative": "0.111", "neutral": "0.222", "positive": "0.667", "sentiment": "0.556"},
{"img": "⏩", "name": "black right-pointing double triangle", "negative": "0.111", "neutral": "0.667", "positive": "0.222", "sentiment": "0.111"}
]

#Gets all the other converted emojis and appends the "data" list
with open("backend/language/emoji_sentiment", 'rb') as f:
    d = pickle.Unpickler(f)
    data2 = d.load()
data = data2 + data1


def convert_special(c):
    """ converts emoji into emoji description if it exists """

    if c > '\uffff':
        try:
            c = '_.{}._'.format(ud.name(c).lower().replace(' ', '_'))
        except:
            c = '_.�._'
    elif c in [":)", ":-)"]:
        c = '_.☺._'
    elif c in ["=)"]:
        c = "_.smiling_face_with_smiling_eyes._"
    elif c in [":(", ":-(", "=("]:
        c = "_.disappointed_face._"
    elif c in [":/", ":-/", "=/"]:
        c = "_.confused_face._"
    elif c in [">:(", ">:-(", ">:o", ">:-o"]:
        c = "_.persevering_face._"
    elif c in [":'(", ":'-("]:
        c = "_.crying_face._"
    elif c in [":p", ":-p", "=p"]:
        c = "_.face_with_stuck-out_tongue._"
    elif c in [";p", ";-p"]:
        c = "_.face_with_stuck-out_tongue_and_winking_eye._"
    elif c in ["3:)", "3:-)"]:
        c = "_.smiling_face_with_horns._"
    elif c in [":d", ":-d", "=d"]:
        c = "_.grinning_face._"
    elif c in ["o:)", "o:-)"]:
        c = "_.smiling_face_with_halo._"
    elif c in [":o", ":-o"]:
        c = "_.astonished_face._"
    elif c in [":*",":-*"]:
        c = "_.kissing_face._"
    elif c in [";)", ";-)"]:
        c = "_.winking_face._"
    elif c in ["<3", "\u2764\uFE0F"]:
        c = "_.❤._"
    elif c in ["8)", "8-)"]:
        c = "_.smiling_face_with_sunglasses._"
    elif c in ["-_-"]:
        c = "_.expressionless_face._"
    elif c in [":|", ":-|"]:
        c = "_.neutral_face._"
    elif c in ["(y)"]:
        c = "_.thumbs_up_sign._"
    elif c in ["(n)"]:
        c = "_.thumbs_down_sign._"
    return c

def convert_string(s):
    """ converts string into a tuple (string without emoji, list of emojis) """

    text = []
    smileys = []
    cv = [convert_special(c) for c in s.split(" ")]
    for elt in cv:
        if elt[:2] == "_.":
            smileys.append(elt)
        else:
            text.append(elt)
    
    return text, smileys


def emoji_sentiment(s):
    """ for each emoji of the sentence, gets its sentiment score in [-1; 1] """
    
    emoji = convert_string(s)[1]
    results = []
    for elt in emoji:
        for item in data:
            if item['img'] == elt:
                sentiment = item['sentiment']
                results.append((elt, sentiment))
                break
        else:
            sentiment = "0"
    
    return results

if __name__ == '__main__':
    x = "salut >:( je suis trop chaud ⛄ 🤞 ❤️".lower()
    print(convert_string(x))
    print(emoji_sentiment(x))
    
    


