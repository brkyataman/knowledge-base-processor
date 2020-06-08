import WordEmbeddingHelper
from WordEmbeddingBuilder import WordEmbeddingBuilder


#stage 1
def preparing(is_data_processed_before=True):
    we_builder = WordEmbeddingBuilder()

    # step 1 Build WE Model
    if is_data_processed_before is False:
        WordEmbeddingHelper.process_training_files()

    processed_data = we_builder.load_processed_data()
    we_builder.build_model(processed_data)
    # step 1 finished

    # step 2 Get OntologyTerms as List

    # step 2 finished

    # step 3 Build new vectors on WE

    # step 3 finished
