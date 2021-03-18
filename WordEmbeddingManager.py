import numpy as np
import WordEmbeddingHelper


class WordEmbeddingManager:

    def __init__(self, source_base_model="vector_model", source_term_model="term_model", is_fasttext=False):
        self.model_dir = 'my_models'
        self.source_base_model = source_base_model
        self.source_term_model = source_term_model
        self.is_fasttext = is_fasttext
        self.vector_model = WordEmbeddingHelper.load_model(self.model_dir + "/" + self.source_base_model)
        self.term_model = WordEmbeddingHelper.load_model(self.model_dir + "/" + self.source_term_model)

    # Returns formatted list of "get_similar_words"
    def get_similar_terms(self, word, topn=5):

        similar_terms = []
        word_vector = self.get_vector_of_word(word)
        if len(word_vector) == 0:
            return []

        # term_model = WordEmbeddingHelper.load_model("my_models/" + self.source_term_model)
        unformatted_similars = self.term_model.wv.most_similar(positive=[word_vector], topn=topn)

        for sim in unformatted_similars:
            name = sim[0].split(":")[0]
            ontology_id = sim[0].split(":")[1]
            similar_terms.append({"name": name, "id": ontology_id, "score": sim[1]})
        return similar_terms


    def get_vector_of_word(self, query):
        # vector_model = WordEmbeddingHelper.load_model("my_models/" + source_base_model)
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

