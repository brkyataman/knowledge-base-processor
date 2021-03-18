from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import string
from time import time
import os
import gensim
import json
from gensim.models.fasttext import FastText

table = str.maketrans(string.punctuation, ' ' * 32)
stop_words = set(stopwords.words('english'))


def is_word_in_model(word):
    model = load_model("my_models/microorganisms_model")
    if word in model.wv:
        print(f"{word} is in model")
        return True
    else:
        print(f"{word} is NOT in model")
        return False

def load_model(target, is_fasttext=False):
    if is_fasttext is True:
        model = FastText.load(target)
    else:
        model = gensim.models.Word2Vec.load(target)
    return model


def preprocess(sentence):
    # replace punctuations to space
    query = sentence.translate(table)

    tokens = word_tokenize(query)
    tokens = [w.lower() for w in tokens]

    # filter out stop words
    words = [w for w in tokens if w not in stop_words]

    return words


# Preprocesses every file under "files" dir and write results to "processed" dir
# Prepares data for training
def process_training_files(files_dir):
    print('loading files..')
    file_names = get_file_names(files_dir)

    start_time = time()
    processed_sentences = process_files(files_dir, file_names)
    process_time = (time() - start_time)

    print('saving preprocessed data')
    with open('processed/preprocessed_data.txt', 'w', encoding='utf-8') as f:
        for file in processed_sentences:
            try:
                f.write("%s\n" % ','.join(file))
            except:
                try:
                    print(f'exception occured for sentence: {file}')
                except:
                    print('exception occured after exception')

    print('saving report')
    with open('processed/preprocess_report.txt', 'w') as f:
        f.write('Preprocess completed in %s seconds\n' % process_time)
        f.write(f'{len(file_names)} files read\n')
        f.write(f'{len(processed_sentences)} sentences processed\n')
    print('files preprocessed and saved successfully')


def load_processed_data(target_file='processed/preprocessed_data.txt'):
    data = []
    print('loading data..')
    with open(target_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            data.append(line.strip().split(','))
    print(f'{len(data)} sentences loaded')
    return data


def get_file_names(dir):
    print('getting file names')
    file_names = []
    for file in os.listdir(dir):
        if file.endswith(".txt"):
            file_names.append(file)
    return file_names


def process_files(files_dir, file_names):
    print('loading and preprocessing files')
    processed_files = []
    processed_num = 0
    erronous_num = 0
    for file_name in file_names:
        try:
            with open(files_dir + "/" + file_name, 'r', encoding="utf8") as json_file:
                data = json.load(json_file)
                processed_body = process_file(data["abstract"])
                processed_files.extend(processed_body)
                processed_num += 1
        except:
            print(f"Error for file {files_dir}/{file_name}")
            erronous_num += 1
        if processed_num + erronous_num % 1000 == 0:
            print(f"Processed {processed_num + erronous_num} files so far.(Erronous: {erronous_num})")

    return processed_files


def process_file(text):
    preprocessed = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        words = preprocess(sentence)
        preprocessed.append(words)
    return preprocessed


#
# deneme = load_model("my_models/microorganisms_model")
#
# deneme2=deneme