import json
import glob
import obonet
import re

def get_local_ontology_terms(subtrees=["brain", "persons"]):
    if subtrees[0] == "ontobiotope":
        return get_ontobiotope_terms()

    data = load_local_subtrees(subtrees)
    terms = {}
    for item in data:
        d = item["d"]["value"]
        c = item["c"]["value"]
        t = item["t"]["value"]
        d_label = item["dL"]["value"].lower().replace(',', '')
        c_label = item["cL"]["value"].lower().replace(',', '')
        t_label = item["tL"]["value"].lower().replace(',', '')

        if d_label not in terms:
            terms[d_label] = {"uri": d, "id": d.split("mesh/")[1], "existInModel": 0}
        if c_label not in terms:
            terms[c_label] = {"uri": c, "id": c.split("mesh/")[1], "existInModel": 0}
        if t_label not in terms:
            terms[t_label] = {"uri": t, "id": t.split("mesh/")[1],  "existInModel": 0}

    return terms




def load_local_subtrees(subtrees=[], path='mesh_subtrees'):
    if len(subtrees) == 0:
        raise Exception("no subtrees found..")
    local_data = []
    files = []

    for subtree in subtrees:
        files.extend(glob.glob(path+'/'+subtree+'*'))

    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            local_data.extend(data["results"]["bindings"])

    return local_data



def get_ontobiotope_terms():
    terms = {}
    graph = obonet.read_obo("OntoBiotope_BioNLP-OST-2019.obo")
    for id_, data in graph.nodes(data=True):
        try:
            if not id_ or not data["name"]:
                continue
            terms[data["name"]] = {"uri": id_, "id": id_.split("OBT:")[1], "existInModel": 0}
            if "synonym" in data:
                for synonym in data["synonym"]:
                    synonym_name = re.findall(r'"([^"]*)"', synonym)[0]
                    terms[synonym_name] = {"uri": id_, "id": id_.split("OBT:")[1], "existInModel": 0}
        except:
            print("Problem!")
    return terms
