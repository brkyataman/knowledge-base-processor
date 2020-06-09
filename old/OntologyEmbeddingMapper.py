import json
import time
import gensim
import numpy as np
import os
import dill
import WordEmbeddingHelper

model_dir = 'my_models'
model_path = model_dir + '/model_skipgram'


def load_model():
    model = gensim.models.Word2Vec.load(model_path)
    return model

def save_model(model, suffix = ""):
    print("trying to save model")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    with open(model_path + suffix, 'wb') as f:
        dill.dump(model, f)
    print("model saved locally")


def open_file():
    #with open('limbic-system-subtree') as json_file:
    #    data = json.load(json_file)
    #return data["results"]["bindings"]
    with open('brain-subtree-0') as json_file:
        data0 = json.load(json_file)
    with open('brain-subtree-1') as json_file:
        data1 = json.load(json_file)
    with open('brain-subtree-2') as json_file:
        data2 = json.load(json_file)
    with open('brain-subtree-3') as json_file:
        data3 = json.load(json_file)

    my_data = []
    my_data.extend(data0["results"]["bindings"])
    my_data.extend(data1["results"]["bindings"])
    my_data.extend(data2["results"]["bindings"])
    my_data.extend(data3["results"]["bindings"])

    return my_data

def get_terms():
    data = open_file()
    terms = {}
    for item in data:
        d = item["d"]["value"]
        c = item["c"]["value"]
        t = item["t"]["value"]
        dName = item["dName"]["value"].lower().replace(',', '')
        cName = item["cName"]["value"].lower().replace(',', '')
        tName = item["tName"]["value"].lower().replace(',', '')

        if dName not in terms:
            terms[dName] = {"uri": d, "existInModel": 0}
        if cName not in terms:
            terms[cName] = {"uri": c, "existInModel": 0}
        if tName not in terms:
            terms[tName] = {"uri": t, "existInModel": 0}

    return terms


def get_vocab():
    terms = get_terms()
    vocab = {}
    for term in terms:
        words = WordEmbeddingHelper.preprocess(term)
        for word in words:
            if word not in vocab:
                vocab[word] = 1
    return vocab

def compare():
    limbic_vocab = get_vocab()
    model = load_model()
    word_vectors = model.wv
    existsInModelNum = 0
    for word in limbic_vocab:
        if word in word_vectors:
            limbic_vocab[word]["existInModel"] = 1
            existsInModelNum += 1
    notExistsInModelNum = len(limbic_vocab) - existsInModelNum
    return limbic_vocab



def create_new_vectors():
    my_terms = get_terms()
    model = load_model()
    word_vectors = model.wv
    normalised_terms = {}
    addedItem = 0
    for term in my_terms:
        vectors_of_term = []
        words = term.replace(',','').split(' ')
        wordNotExistInModel = False
        for word in words:
            if word not in word_vectors:
                wordNotExistInModel = True
                break
            vectors_of_term.append(word_vectors.get_vector(word))

        if wordNotExistInModel is False:
            avg_vector = [0] * len(vectors_of_term[0])
            for vector in vectors_of_term:
                avg_vector = np.add(avg_vector, vector)
            avg_vector = np.divide(avg_vector, len(vectors_of_term))
            # my_terms[term]["avg_vector"] = avg_vector
            normalised_terms[term] = {"uri": my_terms[term]["uri"], "addedToModel": 1}
            model.wv.add(term, avg_vector)
            addedItem += 1

    save_model(model)

    print(f"{addedItem} item added to model")
    return normalised_terms


def save_model_of_ontology():
    vocab = get_vocab()
    vocab = set(vocab)
    model = load_model()
    # TODO: sadece ontology'deki vocabulary'den en az bir kelime içeren word'ler w2v model de kalmalı


#tterms = create_new_vectors()
#with open('my_terms_with_vectors.txt', 'w') as file:
#   file.write(json.dumps(tterms))
#print("done")

#terms = get_terms()
#terms