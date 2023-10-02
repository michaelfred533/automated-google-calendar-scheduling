from textblob import TextBlob

t = TextBlob("reponding") 
t = t.correct()
print(t)