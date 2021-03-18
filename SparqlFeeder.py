from SPARQLWrapper import SPARQLWrapper, JSON
import pymysql
from WordEmbeddingManager import WordEmbeddingManager
from FastTextBuilder import FastTextBuilder
import time

db = "neuroboun_fasttext"

def get_db_connection():
    return pymysql.connect(host='localhost',
        user='root',
        password='pass',
        db='testdb',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)


def insert_to_sparql(query):
    sparql = SPARQLWrapper("http://localhost:3030/"+ db +"/update")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    #sparql.setMethod('POST')
    results = sparql.query().convert()
    return results


def query_fuseki(query):
    sparql = SPARQLWrapper("http://localhost:3030/"+ db +"/query")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


def get_phrases(article_id):
    with get_db_connection() as con:
        query = """
        SELECT p.description, p.first_sim, p.first_sim_point, a.body
        FROM testdb.articles a
        JOIN testdb.article_phrase_map apm on a.article_id = apm.article_id
        JOIN testdb.phrases p on p.phrase_id = apm.phrase_id
        where a.article_id = %s;
        """
        args=(article_id)
        con.execute(query,args)
        rows = con.fetchall()
    return rows


def get_phrases():
    with get_db_connection() as con:
        query = """
        select phrase_id, description
        from phrases
        """
        con.execute(query)
        rows = con.fetchall()
    return rows


def get_ontologyterms():
    with get_db_connection() as con:
        query = """
        select distinct first_sim
        from phrases
        """
        con.execute(query)
        rows = con.fetchall()
    return rows


def insert_bulk(query):
    prefix = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    """
    query = prefix + query
    insert_to_sparql(query)


def insert_phrase_article_relation(article_id, phrases):
    queryString = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
                       PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                       """
    insert_clause = """
                       INSERT{
                           nboun:%s nboun:contains nboun:%s
                       }
                       WHERE{

                       };
       """
    for phrase in phrases:
        queryString += insert_clause % (article_id, process_for_sparql(phrase))

    insert_to_sparql(queryString)

    print
    "Content-type: text/json\n"
    print
    "{ \"result\": \"ok\" }"


def insert_nounphrase(phrases):
    queryString = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
                    PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                    """
    insert_clause = """
                    INSERT{
                        nboun:%s a nboun:Phrase
                    }
                    WHERE{
                    
                    };
    """
    for phrase in phrases:
        queryString += insert_clause % process_for_sparql(phrase)

    insert_to_sparql(queryString)

    print
    "Content-type: text/json\n"
    print
    "{ \"result\": \"ok\" }"

def insert_phrase_term_relation(phrases):
    queryString = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
                             PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                             """
    insert_clause = """
                             INSERT{
                                 nboun:%s nboun:isSimilarTo nboun:%s;
                                          nboun:similarityPoint %s
                             }
                             WHERE{

                             };
             """
    for phrase in phrases:
        queryString += insert_clause % (process_for_sparql(phrase["description"]), process_for_sparql(phrase["first_sim"]), phrase["first_sim_point"])

    insert_to_sparql(queryString)

    print
    "Content-type: text/json\n"
    print
    "{ \"result\": \"ok\" }"


def insert_ontologyterms(terms):
    queryString = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
                          PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                          """
    insert_clause = """
                          INSERT{
                              nboun:%s a nboun:OntologyTerm
                          }
                          WHERE{

                          };
          """
    for term in terms:
        queryString += insert_clause % process_for_sparql(term)

    insert_to_sparql(queryString)

    print
    "Content-type: text/json\n"
    print
    "{ \"result\": \"ok\" }"


def process_for_sparql(text):
    return text.lower().replace(".","").replace(" ", "_").replace("'","").replace("/","").replace(",","").replace("-","_")


def feed_ontology_terms():
    terms = get_ontologyterms()
    insert_ontologyterms(terms)


def feed_db_with_article_data(article_id):
    phrases = get_phrases(article_id)
    insert_nounphrase(phrases)
    insert_phrase_article_relation(article_id)
    insert_phrase_term_relation(phrases)


def read_added_ontology_terms():
    s = open('my_terms_with_vectors.txt', 'r').read()
    terms = eval(s)
    return terms


def update_mysql(phrase_id, uri):
    with get_db_connection() as con:
        query = "UPDATE phrases SET " \
                "first_sim_uri = %s " \
                "where phrase_id = %s "
        args = (uri, phrase_id)
        con.execute(query, args)


def add_sim_to_fuseki(phrase, mesh_id, sim_score, phrase_id):
    queryString = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
                     PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                     PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
                     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                     INSERT{
                         nboun:%s nboun:isSimilarTo mesh:%s ;
                                  nboun:similarityScore %s ;
                                  rdfs:label "%s"^^xsd:string .
                     }
                     WHERE{

                     };
                 """
    queryString = queryString % ("PH%s"%phrase_id, mesh_id, sim_score, phrase)
    insert_to_sparql(queryString)

def add_article_to_fuseki(article_id):
    queryString = """   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                         PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                         PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
                         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                         INSERT{
                             nboun:%s rdf:type nboun:Article .
                         }
                         WHERE{

                         };
                     """
    queryString = queryString % ("ART%s" % article_id)
    insert_to_sparql(queryString)



def is_phrase_term_rel_exist(phrase_id, term):
    queryString = """       PREFIX owl: <http://www.w3.org/2002/07/owl#>
                         PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                         PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
                         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                            SELECT ?l
                            WHERE {
                              nboun:%s nboun:isSimilarTo mesh:%s;
                                        rdfs:label ?l .
                            }
                         """
    queryString = queryString % (("PH%s" % phrase_id), term)
    result = query_fuseki(queryString)

    if len(result) == 0:
        return False;
    return True;



def insert_similarity(phrases, source_model="term_model", sim_threshold=0):
    # we_manager = WordEmbeddingManager()
    we_manager = FastTextBuilder()

    inserted_items = []
    error_items = []

    for phrase in phrases:
        try:
            id = phrase["phrase_id"]
            word = phrase["description"]
            similars = we_manager.get_similar_terms(word, source_model=source_model, topn=1)
            if len(similars) == 0 or similars[0]["score"] < sim_threshold:
                continue;
            sim = similars[0]
            # if is_phrase_term_rel_exist(id, sim["id"]) == False:
            add_sim_to_fuseki(phrase=word, mesh_id=sim["id"], sim_score=sim["score"], phrase_id=id)
            inserted_items.append({"phrase_id": id, "phrase": word, "mesh_id": sim["id"], "mesh_desc": sim["name"], "sim_score": sim["score"]})
        except Exception:
            error_items.append({"phrase_id": id, "phrase": word})
            print("error on word '%s'" % phrase)

    timestr = time.strftime("%Y%m%d-%H%M")
    filename = 'fuseki_feed%s.txt' % timestr
    with open(filename, 'w') as f:
        for item in inserted_items:
            f.write("%s\n" % item)

    timestr = time.strftime("%Y%m%d-%H%M")
    filename = 'fuseki_feed_error%s.txt' % timestr
    with open(filename, 'w') as f:
        for item in error_items:
            f.write("%s\n" % item)


def get_articles():
    with get_db_connection() as con:
        query = """
        SELECT article_id, body
        FROM testdb.articles a
        """
        con.execute(query)
        rows = con.fetchall()
    return rows

def feed_fuseki_with_articles():
    articles = get_articles()
    for article in articles:
        add_article_to_fuseki(article["article_id"])


def get_article_phrase_pairs():
        with get_db_connection() as con:
            query = """
            SELECT article_id, phrase_id
            FROM testdb.article_phrase_map ;
            """
            con.execute(query)
            rows = con.fetchall()
        return rows

def add_article_pair_rel_to_fuseki(article_id, phrase_id):
    queryString = """   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                         PREFIX nboun: <http://www.semanticweb.org/berkay.ataman/ontologies/2020/3/neuroboun_ontology#>
                         PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
                         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                         INSERT{
                             nboun:%s nboun:contains nboun:%s .
                             nboun:%s rdf:type nboun:Phrase .
                         }
                         WHERE{

                         };
                     """
    queryString = queryString % ("ART%s" % article_id, "PH%s" % phrase_id, "PH%s" % phrase_id)
    insert_to_sparql(queryString)


def feed_fuseki_with_article_phrase_rel():
    pairs = get_article_phrase_pairs()
    for pair in pairs:
        add_article_pair_rel_to_fuseki(pair["article_id"], pair["phrase_id"])


# feed_fuseki_with_articles()
# feed_fuseki_with_article_phrase_rel()


# phrases = get_phrases()
# insert_similarity(phrases)

#22173014
#feed_ontology_terms()
#feed_db_with_article_data(22173014)