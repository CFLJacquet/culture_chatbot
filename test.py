from backend.exhibition.handle_expo import get_genre_exhib, get_exhib, get_exhib_query, get_detail_exhib
from backend.messenger.msg_fct import user_details, typing_bubble, send_msg, send_button, send_card, send_quick_rep, start_buttons
from backend.cinema.handle_cinema import get_details_cinema, get_topmovies_genre

from backend.language.handle_text import analyse_text
from backend.language.handle_text_query import vect_search
from backend.others.bdd_jokes import random_joke


print(len(get_exhib_query(vect_search("expo sur la mode"), ["mode"], 1)))
# print(vect_search("expo photo")[:10])
# print(vect_search("expo art moderne")[:10])
# print(vect_search("expo art contemporain")[:10])

# print(get_exhib_query([291, 355, 348, 344, 383, 289, 370, 273, 38, 247], ["all"], 1)[:3])
# print(get_exhib_query([192, 400, 206, 391, 429, 274, 180, 276, 258, 124], ["all"], 1)[:3])
# print(get_exhib_query([297, 147, 169, 171, 196, 428, 424, 263, 143, 181], ["all"], 1)[:3])