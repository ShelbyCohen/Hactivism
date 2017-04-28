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
		# self.mode = input("Enter SMART Notation for index: ")
		# self.query_mode = input("Enter SMART Notation for query: ")

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
		for file in sorted(f for f in os.listdir(clean_path)):
			clean_file = open(clean_path + file, "r")
			doc_id = str(file).replace(".txt", "")
			doc_id = int(doc_id)
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
		n = 375

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
		docid_cosine_list = list()
		total_ltc = 1

		query_dict = Counter(query_list)

		for token in query_dict.keys():
			# logic to exit if token is not in self.index.keys():
			if token not in self.index.keys():
				continue
			if query_mode[0] == 'l':
				query_dict[token] = (1 + math.log(query_dict[token]))
				query_dict[token] = query_dict[token] * self.idf[token]
				total_ltc += query_dict[token] ** 2
			query_dict[token] /= math.sqrt(total_ltc)

		# adding a cosine score of 0.0 to all irrelevant documents
		all_docs = 86
		doc_id = 1
		for token in query_dict.keys():
			while doc_id < all_docs:
				try:
					if doc_id not in self.index[token].keys():
						docid_cosine_list.append(0)
					else:
						docid_cosine_list.append(query_dict[token] * self.index[token][doc_id][0])
					doc_id += 1
				except:
					continue

		return docid_cosine_list

	def get_results(self):
		db = WebDB('cache.db')

		item_search_results = {}
		docs_to_items = {}
		i = 0
		query_list_for_each_item = list()
		query_list = list()
		query_string = " "
		all_query_cosines = list()
		in_order_cosine = list()
		cosine_scores = list()

		# item_queries = open("data/item/movements.txt", "r")

		clean_path = "data/clean/"
		for file in sorted(f for f in os.listdir(clean_path)):
			item_queries = open(clean_path + file, "r")
			for query in item_queries.readlines():
				query = query.strip("\n")
				query = query.replace('-', " ")
				query = query.replace(',', " ")
				query = query.replace('\'', " ")
				query_list.append(query)
				query_string += " " + query

			# while i < len(query_list):
			# query_raw_input = query_list[i]
			query_list_for_each_item = query_string.split(' ')

			for e, each_word in enumerate(query_list_for_each_item):
				query_list_for_each_item[e] = self.p.stem(each_word).lower()

			# print(query_raw_input)

			# cosine_scores is a dictionary with doc_ids mapped to cosine score
			cosine_scores = self.movement_score(query_list_for_each_item, self.query_mode)
			# sorted_cosine_scores = sorted(cosine_scores, key=cosine_scores.get, reverse=True)

			all_query_cosines.append(cosine_scores)

			i += 1

		print(all_query_cosines)
		plotly.make_heatmap(all_query_cosines)

		return all_query_cosines


if __name__ == '__main__':
	bse = BooleanSearchEngine()
