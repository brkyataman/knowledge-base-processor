import WordEmbeddingHelper
import MeshHelper
from WordEmbeddingBuilder import WordEmbeddingBuilder

subtrees = ['brain', 'persons']


#stage 1
def preparing(process_data=False, build_we_model=False, build_new_ontology_we_model=True):
    we_builder = WordEmbeddingBuilder()

    # step 1 Build WE Model
    print("starting to step 1 - building we model...")
    if process_data is True:
        WordEmbeddingHelper.process_training_files()

    if build_we_model is True:
        processed_data = WordEmbeddingHelper.load_processed_data()
        we_builder.build_model(processed_data)
    # step 1 finished

    # step 2 Get OntologyTerms as List
    local_ont_terms = MeshHelper.get_local_ontology_terms(subtrees)
    # step 2 finished

    # step 3 Build new vectors on WE
    if build_new_ontology_we_model is True:
        we_builder.create_ontology_term_model(ontology_terms=local_ont_terms, base_model_name="model")
    else:
        print("Extending ontology WE model is not implemented yet..")
    # step 3 finished

preparing()