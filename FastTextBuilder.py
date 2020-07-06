import fasttext
from gensim.models.fasttext import FastText
from gensim.test.utils import datapath
import WordEmbeddingHelper
import time
import numpy as np
import MeshHelper

class FastTextBuilder:

    def __init__(self):
        # Set file names for train and test data
        self.model_path = 'my_models/ft_gensim_model'
        self.term_model = self.load_model(path="my_models/ft_term_model")
        self.vector_model = self.load_model(path="my_models/ft_gensim_model")

    def build_model(self):
        sentences = WordEmbeddingHelper.load_processed_data("processed/preprocessed_data.txt")
        model_gensim = FastText(size=100, sg=1, min_count=3)

        print("starting to training..")
        start_time = time.time()
        model_gensim.build_vocab(sentences=sentences)
        model_gensim.train(sentences=sentences, epochs=model_gensim.epochs,
                           total_examples=model_gensim.corpus_count, total_words=model_gensim.corpus_total_words)
        training_time = (time.time() - start_time)
        print("training finished in %s seconds" % training_time)
        print(model_gensim)
        # saving a model trained via Gensim's fastText implementation
        model_gensim.save(self.model_path)
        print("ft model saved")


    def load_model(self, path="my_models/ft_gensim_model"):
        return FastText.load(path)


    def create_ontology_term_model(self, ontology_terms, base_model_name, new_model_name="ft_term_model"):
        base_model = self.load_model()
        ontology_model = FastText(size=100)

        normalised_terms = {}
        inserted_item_num = 0

        unknown_term = 0
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
            else:
                unknown_term += 1

        ontology_model.save("my_models/"+new_model_name)

        print(f"{inserted_item_num} items added to model / {unknown_term} unknown terms couldn't inserted")
        return normalised_terms


    # Returns formatted list of "get_similar_words"
    def get_similar_terms(self, word, source_model="term_model", topn=5):
        similar_terms = []
        word_vector = self.get_vector_of_word(word)
        if len(word_vector) == 0:
            return []

        # term_model = self.load_model(path="my_models/ft_term_model")
        unformatted_similars = self.term_model.wv.most_similar(positive=[word_vector], topn=topn)

        for sim in unformatted_similars:
            name = sim[0].split(":")[0]
            ontology_id = sim[0].split(":")[1]
            similar_terms.append({"name": name, "id": ontology_id, "score": sim[1]})
        return similar_terms


    def get_vector_of_word(self, query):
        # vector_model = self.load_model(path="my_models/ft_gensim_model")
        word_vector = [0] * self.vector_model.vector_size

        words = WordEmbeddingHelper.preprocess(query)
        if len(words) == 0:
            word_vector = []

        try:
            for word in words:
                if word not in self.vector_model.wv:
                    word_vector = []
                    break;
                word_vector = np.add(word_vector, self.vector_model.wv.get_vector(word))
            word_vector = np.divide(word_vector, len(words))
        except Exception:
            print(f"An error occured. Probably word {query} is not in model")

        return word_vector

    def get_similar_words_by_user_input(self):
        user_input = ""
        while user_input != "x":
            user_input = input("Give ur input: ")
            terms = self.get_similar_terms(user_input, topn=5)
            print(terms)

# ft_model = load_model()
# subtrees = ['mammals','brain', 'persons']
# local_ont_terms = MeshHelper.get_local_ontology_terms(subtrees)
# create_ontology_term_model(local_ont_terms,"")
# print(ft_model)