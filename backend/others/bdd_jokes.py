import random

#Juste une liste de dad jokes en anglais

jokes = [
    'To the man in the wheelchair that stole my camouflage jacket', \
    'The rotation of earth really makes my day', \
    '5/4 of people admit that they’re bad with fractions', \
    'Whenever the cashier at the grocery store asks my dad if he would like the milk in a bag he replies, "No, just leave it in the carton!"', \
    'A furniture store keeps calling me.All I wanted was one night stand', \
    'I thought about going on an all-almond diet.But thats just nuts', \
    "I'll call you later.Don't call me later, call me Dad", \
    'I’ve never gone to a gun range before.I decided to give it a shot!', \
    'I don’t play soccer because I enjoy the sport.I’m just doing it for kicks', \
    'I used to work in a shoe recycling shop.It was sole destroying', \
    "I just watched a program about beavers.It was the best dam program I've ever seen", \
    "I would avoid the sushi if I was you.It’s a little fishy", \
    "I wouldn't buy anything with velcro.It's a total rip-off", \
    'Two goldfish are in a tank.One says to the other, "do you know how to drive this thing?"', \
    'This graveyard looks overcrowded.People must be dying to get in there', \
    'People don’t like having to bend over to get their drinks.We really need to raise the bar', \
    "The shovel was a ground-breaking invention.You can hide but you can't run", \
    'Did you hear about the restaurant on the moon? Great food, no atmosphere', \
    'What do you call a fake noodle? An Impasta', \
    'How many apples grow on a tree? All of them', \
    "Want to hear a joke about paper? Nevermind it's tearable", \
    'Why did the coffee file a police report? It got mugged', \
    "How does a penguin build it's house? Igloos it together", \
    'Dad, did you get a haircut? No I got them all cut', \
    'What do you call a Mexican who has lost his car? Carlos', \
    "Dad, can you put my shoes on? No, I don't think they'll fit me", \
    'Why did the scarecrow win an award? Because he was outstanding in his field', \
    "Why don't skeletons ever go trick or treating? Because they have no body to go with", \
    "What do you call an elephant that doesn't matter? An irrelephant", \
    "Want to hear a joke about construction? I'm still working on it", \
    "What do you call cheese that isn't yours? Nacho Cheese", \
    "Why couldn't the bicycle stand up by itself? It was two tired", \
    'What did the grape do when he got stepped on? He let out a little wine', \
    "Dad, can you put the cat out? I didn't know it was on fire", \
    'What do you call a man with a rubber toe? Roberto', \
    'What do you call a fat psychic? A four-chin teller', \
    "What's brown and sticky? A stick", \
    "Why do you never see elephants hiding in trees? Because they're so good at it", \
    "Did you hear about the kidnapping at school? It's fine, he woke up", \
    'Did I tell you the time I fell in love during a backflip? I was heels over head'
]

def random_joke():
    return jokes[random.randrange(0,len(jokes))]


if __name__=="__main__":
    print(random_joke())