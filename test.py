import treetaggerwrapper as ttw 
tagger = ttw.TreeTagger(TAGLANG='fr')

s = "salut salt ;) j'aime les expos d'art contemporain et le cinéma ⛄ 🤞 ❤️ ...".lower()

tags = tagger.tag_text(s)
print(tags)
tags2 = [word.split("\t") for word in tags]
print(tags2)