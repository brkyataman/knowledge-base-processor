from SPARQLWrapper import SPARQLWrapper, JSON
import pymysql


class SparqlManager:

    def __init__(self):
        self.base_address = "http://localhost:3030"
        self.db = "neuroboun_clean"

    # Returns intersected related articles of given Ontology Term list
    def get_related_articles_of_list(self, term_id_list, min_sim_score):
        result = {}
        intersected_articles = []
        i = 0
        for term_id in term_id_list:
            details, articles = self.get_related_articles(term_id, min_sim_score)
            result[term_id] = details
            if i == 0:
                intersected_articles.extend(articles)
            else:
                intersected_articles = set(intersected_articles).intersection(articles)
            i += 1

        for key in result:
            val = result[key]
            result[key] = [v for v in val if v["article"] in intersected_articles]

        return result, list(intersected_articles)


    def get_related_articles(self, term_id, min_sim_score=0.8):
        q = '''
                        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        				PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
        				PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
        				PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        				PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        				PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        				PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>

        				SELECT DISTINCT ?a ?p ?pL ?ot ?otL ?sim
        				WHERE { 
                            %s
        					?p nboun:isSimilarTo ?ot ;
        					  rdfs:label ?pL ;
        					  nboun:similarityScore ?sim .
        					?a nboun:contains ?p .
        					bind( if((?ot=?d),?dL,if((?ot=?c),?cL,?tL)) as ?otL ) .
        				  FILTER(((?ot=?d) || (?ot=?c) || (?ot=?t)) && (?sim > %s))

        				}
                '''
        mesh_query = ""
        if term_id[0] == 'T':
            mesh_query = '''
                            SERVICE<http://id.nlm.nih.gov/mesh/sparql?inference=true>{
                             ?ct meshv:term mesh:%s ;
                                 rdf:type meshv:Concept .
                             ?dt meshv:concept ?ct ;
                                 rdf:type meshv:Descriptor .
        					 ?d meshv:broaderDescriptor* ?dt ;
        						  rdfs:label ?dL . 
        					 ?d meshv:concept ?c .
        					 ?c rdfs:label ?cL .
        					 ?c meshv:term ?t .
        					  ?t meshv:prefLabel ?tL .
        					}
            '''
        elif term_id[0] == 'M':
            mesh_query = '''
                                        SERVICE<http://id.nlm.nih.gov/mesh/sparql?inference=true>{
                                         ?dc meshv:concept mesh:%s ;
                                             rdf:type meshv:Descriptor .
                    					 ?d meshv:broaderDescriptor* ?dc ;
                    						  rdfs:label ?dL . 
                    					 ?d meshv:concept ?c .
                    					 ?c rdfs:label ?cL .
                    					 ?c meshv:term ?t .
                    					  ?t meshv:prefLabel ?tL .
                    					}
                        '''
        elif term_id[0] == 'D':
            mesh_query = '''
                        SERVICE<http://id.nlm.nih.gov/mesh/sparql?inference=true>{
        					 ?d meshv:broaderDescriptor* mesh:%s ;
        						  rdfs:label ?dL . 
        					 ?d meshv:concept ?c .
        					 ?c rdfs:label ?cL .
        					 ?c meshv:term ?t .
        					  ?t meshv:prefLabel ?tL .
                        }
            '''

        q = q % (mesh_query, min_sim_score)
        q = q % term_id

        response = self.query_fuseki(q)
        formatted_response = []
        unique_articles = []
        for item in response["results"]["bindings"]:
            f = {}
            f["article"] = item["a"]["value"].split("ontology#")[1]
            f["phrase"] = item["p"]["value"].split("ontology#")[1]
            f["phrase_label"] = item["pL"]["value"]
            f["ontology_term"] = item["ot"]["value"].split("mesh/")[1]
            f["ontology_desc"] = item["otL"]["value"]
            f["sim_score"] = item["sim"]["value"]
            formatted_response.append(f)
            if f["article"] not in unique_articles:
                unique_articles.append(f["article"])
        return formatted_response, unique_articles


    def query_fuseki(self, query):
        sparql = SPARQLWrapper(self.base_address + "/" + self.db + "/query")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results