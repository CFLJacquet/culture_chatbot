from backend.exhibition.handle_expo import get_genre_exhib, get_exhib

payload = 'Famille-1'

print(payload[:-2] in get_genre_exhib()[0])

print(get_exhib(payload[:-2], int(payload[-1])))