import hunspell

h = hunspell.Hunspell('hu_HU')
text = "A Zákány Szerszámház kiváló szerszámokat kínál."
words = text.split()
new_text = " ".join([h.suggest(word)[0] if h.suggest(word) else word for word in words])

print(new_text)
