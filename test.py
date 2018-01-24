from server import get_details, get_genre_movie, get_topmovies_genre
import sys
from pprint import pprint


print(sys.stdout.encoding)
pprint(get_topmovies_genre("Comédie"))