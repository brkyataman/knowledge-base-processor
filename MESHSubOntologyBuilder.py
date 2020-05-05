from MeshApiClient import MeshApiClient
from anytree import Node, RenderTree, AnyNode
from anytree.exporter import JsonExporter
import SparqlFeeder
import OntologyEmbeddingMapper


_meshReqCount = 0
_meshApiClient = MeshApiClient()
_basicInsert = """
    INSERT {
       mesh:%s meshv:broaderDescriptor mesh:%s .
       mesh:%s rdfs:label "%s"^^xsd:string .
    }
    WHERE{
      
    };
    
"""
_conceptsAndTermsInsert = """
    INSERT {
    mesh:%s
       mesh:%s meshv:concept mesh:%s .
       mesh:%s rdfs:label "%s"^^xsd:string .
    }
    WHERE{
      
    };
"""

def get_narrower_descriptors(descriptor):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
        PREFIX mesh2020: <http://id.nlm.nih.gov/mesh/2020/>
        PREFIX mesh2019: <http://id.nlm.nih.gov/mesh/2019/>
        PREFIX mesh2018: <http://id.nlm.nih.gov/mesh/2018/>
        
        SELECT DISTINCT ?d ?dName
        FROM <http://id.nlm.nih.gov/mesh>
        WHERE {
           ?d meshv:broaderDescriptor mesh:%s .
           ?d rdfs:label ?dName .
        }
    """
    query = query % descriptor
    result = _meshApiClient.query_sparql(query=query)

    return result


def build_tree_from_main_descriptor(id, name, parent_id):
    narrows = get_narrower_descriptors(id)
    insert_cmd = _basicInsert % (id, parent_id,id,name)

    if len(narrows) == 0:
        return AnyNode(id=id,name=name), insert_cmd

    children = []
    for narrow in narrows:
        narrow_id = narrow["d"]["value"].split("mesh/")[1]
        narrow_name = narrow["dName"]["value"]

        child, child_insert_cmd = build_tree_from_main_descriptor(narrow_id, narrow_name, id)
        insert_cmd += child_insert_cmd
        children.append(child)

    node = AnyNode(id=id,name=name, children=children)

    return node, insert_cmd


def execute():
    root, root_insert_command = build_tree_from_main_descriptor("D001921", "Brain", "D002490")

    for pre, fill, node in RenderTree(root):
        print("%s%s(%s)" % (pre, node.name, node.id))

    exporter = JsonExporter(sort_keys=True)
    json_tree = exporter.export(root)

    with open('brain_subtree_json.txt', 'w') as f:
        f.write(json_tree)

    with open("brain_subtree_insert_cmd.txt", 'w') as f:
        f.write(root_insert_command)


    SparqlFeeder.insert_bulk(root_insert_command)

    print("%s requests sent to MESH Api" % _meshApiClient.req_count)




def build_concepts_and_terms():
    data = OntologyEmbeddingMapper.open_file()

    cmd = ""
    partial_cmd = ""

    i = 0
    for row in data:
        d_id = row["d"]["value"].split("mesh/")[1]
        d_name = row["dName"]["value"]
        c_id = row["c"]["value"].split("mesh/")[1]
        c_name = row["cName"]["value"]
        t_id = row["t"]["value"].split("mesh/")[1]
        t_name = row["tName"]["value"]

        outer = """
           INSERT {
               %s
            }
            WHERE{
            }; 
            
        """
        body = f"""
            mesh:{d_id} rdf:type meshv:Descriptor .
            mesh:{c_id} rdf:type meshv:Concept .
            mesh:{t_id} rdf:type meshv:Term .

            mesh:{d_id} meshv:concept mesh:{c_id} .
            mesh:{c_id} meshv:term mesh:{t_id} .
            
            mesh:{d_id} rdfs:label "{d_name}"^^xsd:string .
            mesh:{c_id} rdfs:label "{c_name}"^^xsd:string .
            mesh:{t_id} rdfs:label "{t_name}"^^xsd:string .
        """
        insert_cmd = outer % body
        partial_cmd += insert_cmd

        i += 1
        if i % 100 == 0:
            SparqlFeeder.insert_bulk(partial_cmd)
            cmd += partial_cmd
            partial_cmd = ""

    SparqlFeeder.insert_bulk(partial_cmd)
    cmd += partial_cmd

    with open("brain_concepts_terms_insert_cmd.txt", 'w') as f:
        f.write(cmd)

    print(f"{i} number of record added")
    #SparqlFeeder.insert_bulk(cmd)

build_concepts_and_terms()


print("end")