import os
from nltk.stem import PorterStemmer
from WebDB import WebDB
import math
from collections import Counter
import pickle
import visualize as plotly


class BooleanSearchEngine:
    def __init__(self):
        print("Hello! Welcome to Shelby's awesome search engine!")
        print("Supported SMART variants: ltc.ltc, nnn.nnn, ltc.nnn")

        self.p = PorterStemmer()

        self.mode = "ltc"
        self.query_mode = "ltc"
        print("Loading Index ... ")
        self.index = {}
        self.idf = {}

        # default mode is ltc
        if self.mode != 'nnn':
            if self.mode != 'ltc':
                self.mode = 'ltc'
                self.query_mode = 'ltc'

        if self.mode == 'nnn':
            if not os.path.isfile("index_nnn.p"):
                self.build()
                print(self.index)
                self.score(self.mode)
                pickle.dump(self.index, open("index_nnn.p", "wb"))
            else:
                self.index = pickle.load(open("index_nnn.p", "rb"))

        if self.mode == 'ltc':
            if not os.path.isfile("index_ltc.p"):
                self.build()
                self.score(self.mode)
                pickle.dump(self.index, open("index_ltc.p", "wb"))
                pickle.dump(self.idf, open("idf_ltc.p", "wb"))
            else:
                self.index = pickle.load(open("index_ltc.p", "rb"))
                self.idf = pickle.load(open("idf_ltc.p", "rb"))

        self.get_results()

    def build(self):
        clean_path = "data/clean/"
        for i in range(1, len(os.listdir(clean_path)) + 1):
            clean_file = open(clean_path + str(i) + ".txt", "r")
            doc_id = int(i)
            pos_id = 0
            for token in clean_file.readlines():
                token = token.strip("\n")
                pos_id += 1
                if token not in self.index:
                    self.index[token] = dict()
                if doc_id not in self.index[token]:
                    self.index[token][doc_id] = [0]
                self.index[token][doc_id].append(pos_id)
        return self.index

    def score(self, mode):
        doc_len = {}
        clean_path = "data/clean/"
        n = len(os.listdir(clean_path))

        # pass1: build index
        # all terms in vocab
        for token in self.index.keys():
            for doc_id in self.index[token].keys():
                # subtract 1 because of new first spot in positions list
                self.index[token][doc_id][0] = len(self.index[token][doc_id]) - 1
                if mode[0] == 'l':
                    self.idf[token] = math.log(n / len(self.index[token]))
                    self.index[token][doc_id][0] = (1 + math.log(self.index[token][doc_id][0]))

                if mode[1] == 't':
                    self.index[token][doc_id][0] = self.index[token][doc_id][0] * self.idf[token]

                # pass2b: accumulate docLen[docID] += weight^2
                if doc_id not in doc_len:
                    doc_len[doc_id] = 0
                else:
                    doc_len[doc_id] += self.index[token][doc_id][0] ** 2

        if mode[2] == 'c':
            # pass3: divide weight / sqrt (doc_len[docID])
            for token in self.index.keys():
                for doc_id in self.index[token].keys():
                    self.index[token][doc_id][0] /= math.sqrt(doc_len[doc_id])

        return doc_len

    def movement_score(self, query_list, query_mode):
        clean_path = "data/clean/"
        all_docs = len(os.listdir(clean_path))
        docid_cosine_list = [0] * all_docs #so irrelevant documents have a score of 0
        total_weight = 1
        query_dict = Counter(query_list)

        for token in query_dict.keys():
            # logic to exit if token is not in self.index.keys():
            if token not in self.index.keys():
                continue
            if query_mode[0] == 'l':
                query_dict[token] = (1 + math.log(query_dict[token])) #get tf-idf weights for each token in query
                query_dict[token] = query_dict[token] * self.idf[token]
                total_weight += query_dict[token] ** 2

        normalized_query_weight = math.sqrt(total_weight) #square root of the summation of all tokens in query
        for token in query_dict.keys():
            query_dict[token] /= normalized_query_weight

        # calculating dot product
        for token in query_dict.keys():
            try:
                if token in self.index:
                    for doc_id in self.index[token].keys(): #docIDs start at 1 and not 0
                        docid_cosine_list[doc_id - 1] += query_dict[token] * self.index[token][doc_id][0]
            except:
                print("ERROR on token: ", token)

        return docid_cosine_list

    def get_results(self):
        db = WebDB('cache.db')

        all_query_cosines = list()

        clean_path = "data/clean/"
        for i in range(1, len(os.listdir(clean_path)) + 1):
            query_string = " "
            item_queries = open(clean_path + str(i) + ".txt", "r")
            for query in item_queries.readlines():
                query = query.strip("\n")
                query = query.replace('-', " ")
                query = query.replace(',', " ")
                query = query.replace('\'', " ")
                query = query.replace('’)', "")
                query = query.replace('.', "")
                query_string += " " + query

            query_list_for_each_item = query_string.split(' ')

            # cosine_scores is a dictionary with doc_ids mapped to cosine score
            cosine_scores = self.movement_score(query_list_for_each_item, self.query_mode)
            all_query_cosines.append(cosine_scores)

        plotly.make_heatmap(all_query_cosines)

        return all_query_cosines


if __name__ == '__main__':
    bse = BooleanSearchEngine()
