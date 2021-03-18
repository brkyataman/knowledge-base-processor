import os
import obonet
from WordEmbeddingManager import WordEmbeddingManager
import json
import networkx as nx
from operator import attrgetter
import WordEmbeddingHelper

ontobiotope_graph = obonet.read_obo("OntoBiotope_BioNLP-OST-2019.obo")
undirected_ob_graph = ontobiotope_graph.to_undirected()
results_dir = "results_fasttext_related_2"
is_fasttext = False
wordEmbeddingManager = WordEmbeddingManager(source_base_model="microorganisms_model", source_term_model="ontobiotope_term_model_2",is_fasttext=is_fasttext)

ft_wordEmbeddingManager = WordEmbeddingManager(source_base_model="microorganisms_model_fasttext", source_term_model="ontobiotope_term_model_fasttext_2",is_fasttext=True)


def evaluate_files(dir_path):
    files = os.listdir(dir_path)
    targets = []
    for file in files:
        if file.endswith(".a1"):
            targets.append(file.split(".a1")[0])

    for target in targets:
        try:
            evaluate(dir_path, target)
        except:
            print(f"error on file {target}")


def evaluate(dir_path, file_name):
    a1, a2 = get_a1_a2_data(dir_path + "/" + file_name)
    stats = {"right": 0, "wrong": 0, "related":0}
    final = []
    final_json =[]
    bb_results=[]
    i=1
    for link in a2:
        if link["type"] != "OntoBiotope":
            continue
        entity = a1[link["annotation"]]
        similars = wordEmbeddingManager.get_similar_terms(word=entity["entity"], topn=5)
        if len(similars) == 0:
            similars.append({"name": "", "id": "", "score": ""})

        guess_result = "false"
        if link["referent"] == "OBT:" + similars[0]["id"]:
            guess_result="true"
            stats["right"] += 1
        else:
            related = False
            try:
                related = undirected_ob_graph.has_edge(link["referent"], "OBT:" + similars[0]["id"])
            except:
                pass
            if related is True:
                stats["related"] += 1
                guess_result = "related"
            else:
                stats["wrong"] += 1

        real_id = ""
        real_name = ""
        try:
            real_id = link['referent']
            real_term = ontobiotope_graph.nodes[real_id]
            real_name = real_term["name"]
        except:
            pass
        str = f"Result:{guess_result}\tEntity:{entity['entity']}\tEntityType:{entity['type']}\tGuessedTerm:{similars[0]['name']}:OBT:{similars[0]['id']}\tOntobiotopeTerm:{real_name}:{real_id}\tScore:{similars[0]['score']}\n"
        str_json = {"entity": entity['entity'], "type": entity['type'], "guess":{"name": similars[0]['name'], "id": similars[0]['id']}, "real": {"name": real_name, "id": real_id}, "sim_score":similars[0]['score'], "result": guess_result}
        bb_str = f"N{i}	OntoBiotope Annotation:{entity['annotation_id']} Referent:OBT:{similars[0]['id']}";
        i+=1
        bb_results.append(bb_str)
        final.append(str)
        final_json.append(str_json)
    stats["total"] = stats['right'] + stats['wrong'] + stats['related']
    if stats["total"] == 0:
        right_percentage = "0.00"
    else:
        right_percentage = "%.2f" % (stats['right'] / stats["total"])
    stats["right_percentage"] = right_percentage
    with open(dir_path + "/"+results_dir+"/" + file_name + ".a3", mode="w") as a3_file:
        a3_file.write(f"Total:{stats['total']}\tRight:{stats['right']}\tRelated:{stats['related']}\tWrong:{stats['right']}\tPerc:{stats['right_percentage']}\n")
        a3_file.writelines(final)
    with open(dir_path + "/"+results_dir+"/a2/" + file_name + ".a2", mode="w") as f:
        for bb_res in bb_results:
            f.write("%s\n"%bb_res)
    # with open(dir_path + "/"+results_dir+"/" + file_name + ".a3.json", mode="w") as a3_file:
    #     a3_file.write(json.dumps({"result": stats, "items": final_json}))


def get_a1_a2_data(file_name):
    a1_data = {}
    a2_data = []
    with open(file_name + ".a1", mode="r") as a1_file:
        for line in a1_file:
            if line == "":
                continue
            line_data = line.replace("\n", "").split("\t")
            a1_data[line_data[0]] = {"entity": line_data[2], "type": line_data[1].split(" ")[0], "annotation_id": line_data[0]}

    a2_data = get_a2_data(file_name)

    return a1_data, a2_data

def get_a2_data(file_name):
    a2_data = []
    with open(file_name + ".a2", mode="r") as a2_file:
        for line in a2_file:
            if line == "":
                continue
            line_data = line.replace("\t", " ").replace("\n", "").split(" ")
            a2_data.append({"id": line_data[0],"annotation": line_data[2].split("Annotation:")[1], "referent": line_data[3].split("Referent:")[1], "type": line_data[1]})

    return a2_data

def get_total():
    dir_path = "bionlp_ontobiotope_2019_training/" + results_dir
    files = os.listdir(dir_path)
    targets = []
    for file in files:
        if file.endswith(".a3.json"):
            targets.append(file)
    total_stats = {"right": 0, "wrong": 0, "related": 0}
    dict = {}
    file_list =[]
    for target in targets:
        with open(dir_path + "/" + target) as f:
            data = json.load(f)
            file_stat = data["result"]
        dict[target] = file_stat
        file_stat["file"] = target
        file_list.append(file_stat)
        total_stats["right"] += file_stat["right"]
        total_stats["wrong"] += file_stat["wrong"]
        total_stats["related"] += file_stat["related"]
    sorted_list = sorted(file_list, key=lambda i: i["right_percentage"],reverse=True)
    total_stats["total"] = total_stats["right"] + total_stats["wrong"] + total_stats["related"]
    total_stats["percentage"] = "%.2f" % (total_stats["right"] / total_stats["total"])

    with open(dir_path + "/" + "_total_results.txt", mode="w") as f:
        f.write(f"perc:{total_stats['percentage']}\ttotal:{total_stats['total']}\tright:{total_stats['right']}\trelated:{total_stats['related']}\twrong:{total_stats['wrong']}\n")
        for item in sorted_list:
            f.write("%s\n" % item)
    print(total_stats)


def get_detailed_stats():
    dir_path = "bionlp_ontobiotope_2019_training/" + results_dir
    files = os.listdir(dir_path)
    targets = []
    for file in files:
        if file.endswith(".a3.json"):
            targets.append(file)
    type_dict = {}
    for target in targets:
        with open(dir_path + "/" + target) as f:
            data = json.load(f)
            items = data["items"]
        for item in items:
            if item["type"] not in type_dict:
                type_dict[item["type"]]={"right": 0, "related": 0, "wrong": 0}
            if item["result"] == "true":
                type_dict[item["type"]]["right"] += 1
            elif item["result"] == "false":
                type_dict[item["type"]]["wrong"] += 1
            elif item["result"] == "related":
                type_dict[item["type"]]["related"] += 1

    with open(dir_path + "/" + "_type_detailed_stats.txt", mode="w") as f:
        f.write(json.dumps(type_dict))

# evaluate_files("bionlp_ontobiotope_2019_training")
# get_total()
# # get_detailed_stats()


def result_viewer(file_id, normalization_id):
    ref_a1, ref_a2 = get_a1_a2_data("bionlp_ontobiotope_2019_training/"+file_id)
    # w2v_a2 = get_a2_data("bionlp_ontobiotope_2019_training/results_w2v_related/w2v-a2/"+file_id)
    w2v_a2 = get_a2_data("bionlp_ontobiotope_2019_training/results_w2v_related_2/a2/"+file_id)
    # ft_a2 = get_a2_data("bionlp_ontobiotope_2019_training/results_fasttext_related/fasttext-a2/" + file_id)
    ft_a2 = get_a2_data("bionlp_ontobiotope_2019_training/results_fasttext_related_2/a2/" + file_id)

    ref ={}
    ft_res = {}
    w2v_res = {}
    for i in ref_a2:
        if i["annotation"] == normalization_id:
            ref = i
            break
    for i in w2v_a2:
        if i["annotation"] == normalization_id:
            w2v_res = i
            break
    for i in ft_a2:
        if i["annotation"] == normalization_id:
            ft_res = i
            break

    try:
        ref_name = ontobiotope_graph.nodes[ref["referent"]]["name"]
    except:
        ref_name = "-"
    try:
        w2v_name = ontobiotope_graph.nodes[w2v_res["referent"]]["name"]
    except:
        w2v_name = "-"
    try:
        ft_name = ontobiotope_graph.nodes[ft_res["referent"]]["name"]
    except:
        ft_name = "-"

    entity = ref_a1[normalization_id]["entity"]
    type = ref_a1[normalization_id]["type"]

    return f"{normalization_id},{type},{entity},{ref_name},{w2v_name},{ft_name}"


# arr = ["T42","T39","T3"]
# for t in arr:
#     result_viewer("BB-norm-15358511", t)

# arr = ["T27","T25","T15"]
# for t in arr:
#     result_viewer("BB-norm-8607503", t)

# arr = ["T3", "T6", "T19"]
# for t in arr:
#     result_viewer("BB-norm-20148898", t)

# arr = ["T9"]
# for t in arr:
#     result_viewer("BB-norm-9643457", t)

# arr = ["T17","T33", "T22", "T8"]
# for t in arr:
#     result_viewer("BB-norm-10492485", t)

# arr = ["T17", "T14", "T7"]
# for t in arr:
#     result_viewer("BB-norm-10658649", t)

#
# WordEmbeddingHelper.is_word_in_model("meticillin")
# WordEmbeddingHelper.is_word_in_model("desiccation")
# wordEmbeddingManager.get_similar_words_by_user_input()

# T3	Habitat	professional phagocytes			Ref:phagocyte	fastText:phagocyte	w2v:medical staff
# T6	Phenotype	Gram-negative			Ref:gram-negative	fastText:gram-negative	w2v:coagulase negative
# T19	Habitat	professional phagocytes			Ref:phagocyte	fastText:phagocyte	w2v:medical staff

#T9	Phenotype	Gram-negative			Ref:gram-negative	fastText:gram-negative	w2v:coagulase negative


def result_compare():
    with open("api_results/" + "w2v_results.json") as f:
        w2v_res = json.load(f)

    with open("api_results/" + "ft_results.json") as f:
        ft_res = json.load(f)

    print(f"doc_id,annotation_id,w2v_sim,ft_sim,annotation_id,type,entity,ref_name,w2v_name,ft_name")

    for ft_doc in ft_res["evaluation"]["detail"]:
        doc_id =  ft_doc["document"]
        w2v_doc = get_w2v_doc(w2v_res, doc_id)

        for ft_pair in ft_doc["evaluations"][0]["pairs"]:
            annotation_id = ft_pair["reference"]["id"]
            w2v_pair = get_w2v_pair(w2v_doc, annotation_id)

            w2v_sim = w2v_pair["similarity"]
            ft_sim = ft_pair["similarity"]

            if ft_sim == w2v_sim:
                try:
                    detail = result_viewer(doc_id,annotation_id )
                    w2v_sim = "%.2f" % w2v_sim
                    ft_sim = "%.2f" % ft_sim
                    print(f"{doc_id},{annotation_id},{w2v_sim},{ft_sim},{detail}")
                except:
                    print("error")

def get_w2v_doc(res, doc_id):
    for x in res["evaluation"]["detail"]:
        if x["document"] == doc_id:
            return x

def get_w2v_pair(doc, annotation_id):
    for x in doc["evaluations"][0]["pairs"]:
        if x["reference"]["id"] == annotation_id:
            return x

result_compare()


def my_check():
    user_input = ""
    while user_input != "x":
        user_input = input("Give ur input: ")
        if user_input == "w":
            user_input = input("W2V  SIMILARS: ")
            terms = wordEmbeddingManager.get_similar_terms(user_input, topn=5)
            print(terms)
        elif user_input == "f":
            user_input = input("FT SIMILARS: ")
            terms = ft_wordEmbeddingManager.get_similar_terms(user_input, topn=5)
            print(terms)
        else:
            WordEmbeddingHelper.is_word_in_model(user_input)
