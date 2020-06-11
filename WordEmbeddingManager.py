import numpy as np
import WordEmbeddingHelper


class WordEmbeddingManager:

    def __init__(self):
        self.model_dir = 'my_models'

    # Returns formatted list of "get_similar_words"
    def get_similar_terms(self, word, source_model="term_model",topn=5):
        similar_terms = []
        word_vector = self.get_vector_of_word(word)
        if len(word_vector) == 0:
            return []

        term_model = WordEmbeddingHelper.load_model("my_models/" + source_model)
        unformatted_similars = term_model.wv.most_similar(positive=[word_vector], topn=topn)

        for sim in unformatted_similars:
            name = sim[0].split(":")[0]
            ontology_id = sim[0].split(":")[1]
            similar_terms.append({"name": name, "id": ontology_id, "score": sim[1]})
        return similar_terms


    def get_vector_of_word(self, query):
        vector_model = WordEmbeddingHelper.load_model("my_models/vector_model")
        word_vector = [0] * vector_model.vector_size

        words = WordEmbeddingHelper.preprocess(query)
        if len(words) == 0:
            word_vector = []

        try:
            for word in words:
                if word not in vector_model.wv:
                    word_vector = []
                    break;
                word_vector = np.add(word_vector, vector_model.wv.get_vector(word))
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

