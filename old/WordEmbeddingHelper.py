from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import string
from time import time
import os
import gensim

table = str.maketrans(string.punctuation, ' ' * 32)
stop_words = set(stopwords.words('english'))


def load_model(target):
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
def process_training_files():
    print('loading files..')
    file_names = get_file_names()

    start_time = time()
    processed_sentences = process_files(file_names)
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


def get_file_names():
    print('getting file names')
    file_names = []
    for file in os.listdir('files'):
        if file.endswith(".txt"):
            file_names.append(file)
    return file_names


def process_files(file_names):
    print('loading and preprocessing files')
    processed_files = []
    for file_name in file_names:
        file = open('files/' + file_name, 'r', encoding="utf8")
        body = file.read()
        file.close()
        processed_body = process_file(body)
        processed_files.extend(processed_body)
    return processed_files


def process_file(text):
    preprocessed = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        words = preprocess(sentence)
        preprocessed.append(words)
    return preprocessed
