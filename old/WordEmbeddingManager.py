import gensim
from gensim.models import Word2Vec
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np
import string
import WordEmbeddingHelper
import OntologyEmbeddingMapper


class WordEmbeddingManager:

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.model_dir = 'my_models'
        self.model_path = self.model_dir + '/model_skipgram'
        self.ontology_terms_in_model = []
        self.mesh_terms = self.get_added_ontology_terms()
        ontology_terms = set(OntologyEmbeddingMapper.get_terms().keys())
        model = self.load_model()
        for term in ontology_terms:
            if term in model.wv.vocab:
                self.ontology_terms_in_model.append(term)

    ## Returns formatted list of "get_similar_words"
    def get_similars(self, query, topn=10):
        formatted_similars = []
        similars = self.get_similar_words(query, topn)

        formatted_similars = []
        for sim in similars["similar"]:
            if len(formatted_similars) == 5:
                break

            mesh_id = self.get_term_mesh_id(sim[0])
            if mesh_id == "":
                continue
            formatted_similars.append({"name": sim[0], "score": sim[1], "id": mesh_id})

        return formatted_similars

    ### This method is frequently used by others.. Refactor it.
    def get_similar_words(self, query, topn=5):
        model = self.load_model()
        similars = []
        try:
            if query in model.wv:
                similars = model.most_similar_cosmul(query, topn=topn)
                #similars = model.wv.most_similar_to_given(query, entities_list=self.ontology_terms_in_model)
            else:
                words = WordEmbeddingHelper.preprocess(query)
                if len(words) == 0:
                    raise Exception()
                avg_vector = [0] * 100
                for word in words:
                    if word not in model.wv:
                        raise Exception()
                    avg_vector = np.add(avg_vector, model.wv.get_vector(word))
                avg_vector = np.divide(avg_vector, len(words))
                model.wv.add(query, avg_vector)
                similars = model.most_similar_cosmul(query, topn=topn)
                #similars = model.wv.most_similar_to_given(query, entities_list=self.ontology_terms_in_model)
        except Exception:
            print(f"An error occured. Probably word {query} is not in model")

        sim = 0
        try:
            sim = model.similarity(query, similars)
        except:
            sim = 0
        return {'similar': similars, 'similarity': sim}


    def get_term_mesh_id(self, name):
        id = ""
        try:
            term = self.mesh_terms[name]
            uri = term["uri"]
            id = uri.split("mesh/")[1]
        except:
            id = ""
        return id

    def get_added_ontology_terms(self):
        s = open('my_terms_with_vectors.txt', 'r').read()
        terms = eval(s)
        return terms

    def get_similar_words_by_user_input(self):
        user_input = ""
        while user_input != "x":
            user_input = input("Give ur input: ")
            self.get_similar_words(user_input, topn=5)

    def __preprocess_query(self, query):
        # replace punctuations to space
        query = query.translate(str.maketrans(string.punctuation, ' '*32))

        tokens = word_tokenize(query)
        tokens = [w.lower() for w in tokens]

        # filter out stop words
        stop_words = set(stopwords.words('english'))
        words = [w for w in tokens if w not in stop_words]

        return words

    def __filter_stopwords(self, query):
        words = [w for w in query if w not in self.stop_words]
        return words

    def load_model(self):
        model = gensim.models.Word2Vec.load(self.model_path)
        return model

    def restrict_w2v(self, w2v, restricted_word_set):
        new_vectors = []
        new_vocab = {}
        new_index2entity = []
        new_vectors_norm = []

        for i in range(len(w2v.vocab)):
            word = w2v.index2entity[i]
            vec = w2v.vectors[i]
            vocab = w2v.vocab[word]
            vec_norm = w2v.vectors_norm[i]
            if word in restricted_word_set:
                vocab.index = len(new_index2entity)
                new_index2entity.append(word)
                new_vocab[word] = vocab
                new_vectors.append(vec)
                new_vectors_norm.append(vec_norm)

        w2v.vocab = new_vocab
        w2v.vectors = new_vectors
        w2v.index2entity = new_index2entity
        w2v.index2word = new_index2entity
        w2v.vectors_norm = new_vectors_norm
        return w2v


