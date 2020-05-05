from SPARQLWrapper import SPARQLWrapper, JSON
import pymysql

def get_db_connection():
    return pymysql.connect(host='localhost',
        user='root',
        password='pass',
        db='testdb',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)


def insert_to_sparql(query):
    sparql = SPARQLWrapper("http://localhost:3030/neuroboun/update")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    #sparql.setMethod('POST')
    results = sparql.query().convert()
    return results


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
    return text.lower().replace(".","").replace(" ", "_")


def feed_ontology_terms():
    terms = get_ontologyterms()
    insert_ontologyterms(terms)


def feed_db_with_article_data(article_id):
    phrases = get_phrases(article_id)
    insert_nounphrase(phrases)
    insert_phrase_article_relation(article_id)
    insert_phrase_term_relation(phrases)


#22173014
#feed_ontology_terms()
#feed_db_with_article_data(22173014)