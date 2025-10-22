import dat1

# GloVe model from https://www.deepset.ai/german-word-embeddings
model = dat1.Model("model/vectors.txt", "model/vocab.txt")

print("Vector for 'Katze':", model.vectors.get("katze"))
print("Vector for 'Hund':", model.vectors.get("hund"))

# Compound words are translated into words found in the model
# print(model.validate("cul de sac")) # cul-de-sac

# Compute the cosine distance between 2 words (0 to 2)
print(model.distance("katze", "hund"))
print(model.distance("katze", "daumen"))

# Compute the DAT score between 2 words (average cosine distance * 100)
print(model.dat(["katze", "hund"], 2))
print(model.dat(["katze", "daumen"], 2))

# Word examples (Figure 1 in paper)
low = ["arme", "augen", "fuss", "hand", "kopf", "bein", "bauch"]
average = ["tasche", "biene", "burger", "fest", "büro", "schuhe", "baum"]
high = ["pferd", "pullover", "maschine", "stechen", "tickets", "tomate", "geige"]

# Compute the DAT score (transformed average cosine distance of first 7 valid words)
print(model.dat(low))
print(model.dat(average))
print(model.dat(high))
