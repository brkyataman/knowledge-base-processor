import os
import gensim
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot
import dill
import nltk
import time


class WordEmbeddingBuilder:

    def __init__(self):
        self.model_dir = 'my_models'
        nltk.download('stopwords')
        nltk.download('punkt')

    def build_model(self, data):
        print("building word embedding")
        model = self.train_model(data)
        self.save_model(model)
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

    def load_model(self, name):
        model = gensim.models.Word2Vec.load(self.model_dir + '/'+ name)
        return model


    def load_processed_data(self):
        data = []
        print('loading data..')
        with open('processed/preprocessed_data.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                data.append(line.strip().split(','))
        print(f'{len(data)} sentences loaded')
        return data
