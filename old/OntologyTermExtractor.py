class OntologyTermExtractor:

    def __init__(self):
        self.init = "hi"

    def extract(self, ontology_name, category):
        if ontology_name == "MESH":
            meshExtractor = MESHTermExtractor()
            meshExtractor.Extract(category)

class MESHTermExtractor:
    def __init__(self):
        self.api_endpoint = ""

    def extract(self, category):
        a =1
        # brute force to mesh api until offset comes 0
