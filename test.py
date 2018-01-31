from server import get_genre_exhib
from backend.cinema.handle_cinema import get_details_cinema, stock_last_movies
import sys
from pprint import pprint


print(sys.stdout.encoding)
pprint(stock_last_movies())