from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

table = str.maketrans(string.punctuation, ' ' * 32)
stop_words = set(stopwords.words('english'))


def preprocess(sentence):
    # replace punctuations to space
    query = sentence.translate(table)

    tokens = word_tokenize(query)
    tokens = [w.lower() for w in tokens]

    # filter out stop words
    words = [w for w in tokens if w not in stop_words]

    return words
