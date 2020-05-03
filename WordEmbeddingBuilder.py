import os
import gensim
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot
import dill
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk
import string
import time
import WordEmbeddingHelper

model_dir = 'my_models'
model_path = model_dir + '/model_skipgram'
nltk.download('stopwords')
nltk.download('punkt')


def train_model(data):
    print("training model..")
    start_time = time.time()
    model = Word2Vec(data, window=30, min_count=1, workers=4, sg=1)
    training_time = (time.time() - start_time)
    print("training finished in %s seconds" % training_time)
    return model


def visualize_embedding(model):
    # fit a 2d PCA model to the vectors
    X = model[model.wv.vocab]
    pca = PCA(n_components=2)
    result = pca.fit_transform(X)

    # create a scatter plot of the projection
    pyplot.scatter(result[:, 0], result[:, 1])
    words = list(model.wv.vocab)
    for i, word in enumerate(words):
        pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
    pyplot.show()


def build_model(data):
    print("building word embedding")
    model = train_model(data)
    save_model(model)
    print("build finished")


def visualize(model):
    visualize_embedding(model)


def save_model(model):
    print("trying to save model")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    with open(model_path, 'wb') as f:
        dill.dump(model, f)
    print("model saved locally")


def load_model():
    model = gensim.models.Word2Vec.load(model_path)
    return model


def get_file_names():
    print('getting file names')
    file_names = []
    for file in os.listdir('files'):
        if file.endswith(".txt"):
            file_names.append(file)
    return file_names


def preprocess_files(file_names):
    print('loading and preprocessing files')
    processed_files = []
    for file_name in file_names:
        file = open('files/' + file_name, 'r', encoding="utf8")
        body = file.read()
        file.close()
        processed_body = preprocess(body)
        processed_files.extend(processed_body)
    return processed_files


def preprocess_and_save():
    print('loading files..')
    file_names = get_file_names()

    start_time = time.time()
    processed_sentences = preprocess_files(file_names)
    preprocess_time = (time.time() - start_time)

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
        f.write('Preprocess completed in %s seconds\n' % preprocess_time)
        f.write(f'{len(file_names)} files read\n')
        f.write(f'{len(processed_sentences)} sentences processed\n')
    print('files preprocessed and saved successfully')


def preprocess(text):
    preprocessed = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        words = WordEmbeddingHelper.preprocess(sentence)
        preprocessed.append(words)

    return preprocessed


def load_processed_data():
    data = []
    print('loading data..')
    with open('processed/preprocessed_data.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            data.append(line.strip().split(','))
    print(f'{len(data)} sentences loaded')
    return data



print('stopwords: \n' + ', '.join(stopwords.words('english')))
#preprocess_and_save()

data = load_processed_data()
# TODO: suan cbow'da train oluyor
#build_model(data)

# find_similars()

# visualize(my_model)
