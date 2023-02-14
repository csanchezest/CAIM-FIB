from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.client import CatClient
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
import numpy as np
import uuid
import csv
import sys


K = 5
alpha = 1
beta = 0.8
R = 25
nrounds = 5

def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])

def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    """
    norms = {}
    vals = np.array([])
    for (t, w) in tw:
        norms[t] = 0
        vals.append(w)
    vals = vals / np.linalg.norm(vals)
    """
    vals = list(tw.values())
    vals = vals / np.linalg.norm(vals)
   # print(np.sum(vals))
    #keys = norms.keys()
    keys = list(tw.keys())
    for i in range(len(vals)):
        #norms[keys[i]] = vals[i]
        tw[keys[i]] = vals[i]
    #return norms
    return tw


def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document

    :param file:
    :return:
    """

    # Get the frequency of the term in the document, and the number of documents
    # that contain the term
    file_tv, file_df = document_term_vector(client, index, file_id)

    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    #tfidfw = []
    tfidfw = {}
    for (t, w),(_, df) in zip(file_tv, file_df):
        tf = w/max_freq
        idf = np.log2(dcount/df)
        #tfidfw.append(zip(t, tf*idf))
        tfidfw[t] = tf * idf
        pass

    return normalize(tfidfw)


def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:document_term_vector
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())


def preprocessQuery(s):
    ret = {}
    for val in s.split(" "):
        a, b = val.split("^"), val.split("~")
        if len(a) > 1:
            ret[a[0]] = float(a[1])
        elif len(b) > 1:
            ret[b[0]] = float(b[1])
        else:
            ret[val] = 1.
    return ret

        
def docsum(docs):
    ret = {}
    for doc in docs:
        ret = {i: ret.get(i, 0) + doc.get(i, 0)
               for i in set(ret).union(doc)}
    return ret
# --------------------------------------------------------------------------------------------------------------------------------------


index = input("Index: ")
inp = input("Query: ")
input = inp
nR = K
client = Elasticsearch()
s = Search(using=client, index=index)
#inp = 'city^2 toronto~2 new'
query = preprocessQuery(inp)
for i in range(nrounds):
    q = Q('query_string',query=inp)  # Feel free to change the word
    s = s.query(q)
    nA = len(list(s))
    response = s[0:K].execute()
    weights = np.array([toTFIDF(client,index,r.meta.id) for r in response])
    # alpha * query
    for key, val in query.items():
        query[key] = val * alpha
    # d_1 + d_2 + ... + d_k
    tfidfunion = docsum(weights)
    # beta * D / K
    tfidfunion = {k: beta * v / K for k, v in tfidfunion.items()}
    # rocchio result
    query = {i: query.get(i, 0) + tfidfunion.get(i, 0)
            for i in set(tfidfunion).union(query)}
    query = dict(sorted(query.items(), key=lambda item: item[1], reverse=True))
    query = dict((key, val) for key, val in list(query.items())[:R])
    inp = ""
    for key, val in query.items():
        inp += key + "^" + str(val) + " "


# open the file in the write mode
id = str(uuid.uuid4().fields[-1])[:5]
f = open('./results/'+index+'/'+id+'.csv', 'w')

# create the csv writer
writer = csv.writer(f)

writer.writerow([" "])
writer.writerow(["INPUT"])
writer.writerow([input])

header = ["PATH", "SCORE"]
# write a row to the csv file
writer.writerow(header)


print()
print(list(query.keys()))
for r in response:  # only returns a specific number of results
    writer.writerow([r.path, r.meta.score])
    # print('ID= %s SCORE=%s' % (r.meta.id,  r.meta.score))
    # print('length:' + str(len(toTFIDF(client,'news',r.meta.id))))
  
    # print('PATH= %s' % r.path)
    # print('TEXT: %s' % r.text[:50])
    # print('-----------------------------------------------------------------')

print()
print("ID: " + id + "\nSuccesfully created " + id +".csv results")

writer.writerow(list(query.keys()))




# close the file
f.close()