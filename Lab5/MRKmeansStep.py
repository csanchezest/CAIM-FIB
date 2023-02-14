"""
.. module:: MRKmeansDef

MRKmeansDef
*************

:Description: MRKmeansDef

    

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 7:42 

"""
from mrjob.job import MRJob
from mrjob.step import MRStep
from multiset import *

__author__ = 'bejar'


class MRKmeansStep(MRJob):
    prototypes = {}

    def jaccard(self, prot, doc):
        norm_doc1 = sum([freq ** 2 for word, freq in prot])
        norm_doc2 = len(doc)
        a = Multiset([word for word, freq in prot])
        b = Multiset(doc)
        intersection = len(a & b)
        return intersection / (norm_doc1 + norm_doc2 - intersection)

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files

        :return:
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

    def load_data(self):
        """
        Loads the current cluster prototypes

        :return:
        """
        f = open(self.options.prot, 'r')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

    def assign_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document

        Words should be sorted alphabetically in the prototypes and the documents

        This function has to return at list of pairs (prototype_id, document words)

        You can add also more elements to the value element, for example the document_id
        """
        # Each line is a string docid:wor1 word2 ... wordn
        doc, words = line.split(':')
        lwords = words.split()

        #
        # Compute map here
        #
        sim = -1
        prototype = None

        # for key, val in self.prototypes.items():
        for key, val in self.prototypes.items():
            aux = self.jaccard(val, lwords)
            if sim < aux:
                sim = aux
                prototype = key

        # Return pair key, value
        yield prototype, (doc, lwords)
        # yield prototype,  doc, lwords

    def aggregate_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word

        :param key:
        :param values:
        :return:
        """
        docs = []
        wordFreq = {}
        for doc, words in values:
            docs.append(doc)
            for word in words:
                try:
                    wordFreq[word] += 1
                except:
                    wordFreq[word] = 1
        n = len(docs)
        freqs = [(word, freq / n) for word, freq in wordFreq.items()]
        yield key, (docs, freqs)

    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)]


if __name__ == '__main__':
    MRKmeansStep.run()
