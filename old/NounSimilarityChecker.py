from WordEmbeddingManager import WordEmbeddingManager
import pymysql
import time
import OntologyEmbeddingMapper
from os import listdir


def get_noun_phrases():
    print("x")


def get_db_connection():
    return pymysql.connect(host='localhost',
        user='root',
        password='pass',
        db='testdb',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)


def get_noun_phrases_from_db():
    with get_db_connection() as con:
        query = "select phrase_id, description, first_sim, second_sim, third_sim " \
                "from phrases p "
        con.execute(query)
        rows = con.fetchall()
    return rows


def save_noun_phrases_similars(phrase_id, similars):
    with get_db_connection() as con:
        query = "UPDATE phrases SET " \
                "first_sim = %s " \
                ",first_sim_point = %s " \
                "where phrase_id = %s "
        args = (similars["similar"], str(similars["similarity"]), phrase_id)
        con.execute(query, args)


def execute():
    phrases = get_noun_phrases_from_db()
    manager = WordEmbeddingManager()

    total_phrase_num = 0
    erronous_phrase_num = 0

    start_time = time.time()
    for phrase in phrases:
        similars = manager.get_similar_words(phrase["description"])
        total_phrase_num += 1
        if similars['similarity'] == 0:
            erronous_phrase_num += 1
        phrase["similars"] = similars
        save_noun_phrases_similars(phrase["phrase_id"], similars)
        if total_phrase_num % 100 == 0:
            execution_time = (time.time() - start_time)
            print(f"{total_phrase_num} passed in %s seconds" % execution_time)
            start_time = time.time()


def find_how_many_similarities_are_in_ontology():
    terms = OntologyEmbeddingMapper.get_terms()
    phrases = get_noun_phrases_from_db()
    unknown_num = 0
    wrong_num = 0
    correct_num = 0
    unknowns = []
    wrongs = []
    corrects = []
    for phrase in phrases:
        if phrase["first_sim"] == "":
            unknown_num += 1
            unknowns.append(phrase)
        elif phrase["first_sim"] in terms:
            correct_num += 1
            corrects.append(phrase)
        elif phrase["second_sim"] in terms:
            correct_num += 1
            corrects.append(phrase)
        elif phrase["third_sim"] in terms:
            correct_num += 1
            corrects.append(phrase)
        else:
            wrong_num += 1
            wrongs.append(phrase)
    print(f"Correct: {correct_num} - Wrong: {wrong_num} - Unknown: {unknown_num}")

def execute_2():
    manager = WordEmbeddingManager()
    manager.get_similar_words_by_user_input()


def find_in_files(query):
    found_files = []
    files_scanned = 0
    for filename in listdir("files"):
        with open('files/' + filename) as file:
            try:
                files_scanned += 1
                text = file.read().lower()
                if query in text:
                    found_files.append(filename)
                if len(found_files) == 5:
                    break
            except:
                continue
    print(f"{files_scanned} files scanned")
    return found_files

execute_2()
#files = find_in_files("uncinate")
#print(files)