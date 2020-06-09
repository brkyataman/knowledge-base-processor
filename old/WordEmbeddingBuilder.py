import os
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot
import dill
import nltk
import time
import numpy as np
import WordEmbeddingHelper


class WordEmbeddingBuilder:

    def __init__(self):
        self.model_dir = 'my_models'
        nltk.download('stopwords')
        nltk.download('punkt')

    def build_model(self, data):
        print("building word embedding")
        model = self.train_model(data)
        self.save_model(model, "model")
        print("build finished")

    def train_model(self, data):
        print("training model..")
        start_time = time.time()
        model = Word2Vec(data, window=30, min_count=1, workers=4, sg=1)
        training_time = (time.time() - start_time)
        print("training finished in %s seconds" % training_time)
        return model

    def save_model(self, model, name):
        print("trying to save model")
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        with open(self.model_dir + '/' + name, 'wb') as f:
            dill.dump(model, f)
        print("model saved locally")

    def visualize_embedding(self, model):
        # fit a 2d PCA model to the vectors
        pca = PCA(n_components=2)
        result = pca.fit_transform(model[model.wv.vocab])

        # create a scatter plot of the projection
        pyplot.scatter(result[:, 0], result[:, 1])
        words = list(model.wv.vocab)
        for i, word in enumerate(words):
            pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
        pyplot.show()

    def create_ontology_we_model(self, ontology_terms, base_model_name):
        base_model = WordEmbeddingHelper.load_model(self.model_dir + "/" + base_model_name)
        ontology_model = Word2Vec()

        normalised_terms = {}
        inserted_item_num = 0
        for term in ontology_terms:
            vectors_of_term = []
            words = term.split(' ')
            has_unknown_word = False
            for word in words:
                if word not in base_model.wv:
                    has_unknown_word = True
                    break
                vectors_of_term.append(base_model.wv.get_vector(word))

            if has_unknown_word is False:
                avg_vector = [0] * len(vectors_of_term[0])
                for vector in vectors_of_term:
                    avg_vector = np.add(avg_vector, vector)
                avg_vector = np.divide(avg_vector, len(vectors_of_term))
                normalised_terms[term] = {"uri": ontology_terms[term]["uri"], "addedToModel": 1}
                ontology_model.wv.add(term + ":" + ontology_terms[term]["id"], avg_vector)
                inserted_item_num += 1

        self.save_model(ontology_model, "ont_model")

        print(f"{inserted_item_num} items added to model")
        return normalised_terms
