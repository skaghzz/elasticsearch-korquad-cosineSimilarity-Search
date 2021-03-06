# -*- coding: utf-8 -*-

import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import tensorflow_hub as hub
import tensorflow_text
import kss, numpy


##### INDEXING #####

def index_data():
    print("Creating the 'posts' index.")
    client.indices.delete(index=INDEX_NAME, ignore=[404])

    with open(INDEX_FILE) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=INDEX_NAME, body=source)

    count = 0

    with open(DATA_FILE) as data_file:
        for line in data_file:
            line = line.strip()

            json_data = json.loads(line)

            docs = []
            for j in json_data:
                count += 1

                docs.append(j)
                if count % BATCH_SIZE == 0:
                    index_batch(docs)
                    docs = []
                    print("Indexed {} documents.".format(count))

            if docs:
                index_batch(docs)
                print("Indexed {} documents.".format(count))

    client.indices.refresh(index=INDEX_NAME)
    print("Done indexing.")


def paragraph_index(paragraph):
    # 문장단위 분리
    avg_paragraph_vec = numpy.zeros((1, 512))
    sent_count = 0
    for sent in kss.split_sentences(paragraph):
        # 문장을 embed 하기
        # vector들을 평균으로 더해주기
        avg_paragraph_vec += embed_text([sent])
        sent_count += 1
    avg_paragraph_vec /= sent_count
    return avg_paragraph_vec.ravel(order='C')


def index_batch(docs):
    titles = [doc["title"] for doc in docs]
    title_vectors = embed_text(titles)
    paragraph_vectors = [paragraph_index(doc["paragraph"]) for doc in docs]
    requests = []
    for i, doc in enumerate(docs):
        request = doc
        request["_op_type"] = "index"
        request["_index"] = INDEX_NAME
        request["title_vector"] = title_vectors[i]
        request["paragraph_vector"] = paragraph_vectors[i]
        requests.append(request)
    bulk(client, requests)


##### EMBEDDING #####

def embed_text(input):
    vectors = model(input)
    return [vector.numpy().tolist() for vector in vectors]


##### MAIN SCRIPT #####

if __name__ == '__main__':
    INDEX_NAME = "korquad"
    INDEX_FILE = "./index.json"

    DATA_FILE = "./KorQuAD_v1.0_train_convert.json"
    BATCH_SIZE = 100

    SEARCH_SIZE = 3

    print("Downloading pre-trained embeddings from tensorflow hub...")
    module_url = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
    print("module %s loaded" % module_url)
    model = hub.load(module_url)

    client = Elasticsearch()

    index_data()

    print("Done.")
