import os
from nltk.stem import PorterStemmer
from WebDB import WebDB
import math
from collections import Counter
import pickle


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

	def query_score(self, query_list, query_mode):
		docid_cosine_dict = {}
		total_ltc = 1

		# stem and lower query
		# for i in range(len(query_list)):
		#	query_list[i] = self.p.stem(query_list[i]).lower()

		# Counter creates a dictionary that maps each token in query to # of times it is present
		# i.e. query = "duck duck goose", query_dict = {duck: 2, goose: 1}
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

		for token in query_dict.keys():
			for doc_id in self.index[token].keys():
				if doc_id not in self.index[token].keys():
					continue
				elif doc_id in docid_cosine_dict.keys():
					docid_cosine_dict[doc_id] += query_dict[token] * self.index[token][doc_id][0]
				else:
					docid_cosine_dict[doc_id] = query_dict[token] * self.index[token][doc_id][0]

		return docid_cosine_dict

	def get_results(self):
		db = WebDB('cache.db')

		# query_raw_input = input("Enter Query or 'QUIT': ")

		item_search_results = {}
		docs_to_items = {}
		i = 0
		query_list_for_each_item = list()

		query_list = list()

		item_queries = open("data/item/movements.txt", "r")
		for query in item_queries.readlines():
			query = query.strip("\n")
			query = query.replace('-', " ")
			query_list.append(query)



		# while query_raw_input != 'QUIT':
		while i < len(query_list):
			query_raw_input = query_list[i]
			# print(query_raw_input)
			query_list_for_each_item = query_raw_input.split(' ')

			for i, each_word in enumerate(query_list_for_each_item):
				query_list_for_each_item[i] = self.p.stem(each_word).lower()

			print(query_raw_input)
			print(query_list_for_each_item)

			# cosine_scores is a dictionary with doc_ids mapped to cosine score
			cosine_scores = self.query_score(query_list_for_each_item, self.query_mode)
			# sorted_cosine_scores = sorted(cosine_scores, key=cosine_scores.get, reverse=True)

			# print("\n URL search results: ")
			for d in range(len(cosine_scores)):
				(url, docType, title) = db.lookupCachedURL_byID(d+1)
				docs_to_items[d+1] = str(title).strip("\n")
				print(title)

				if title not in item_search_results.keys():
					item_search_results[title] = cosine_scores[d]
					print(cosine_scores[d+1])

					# print(len(item_search_results))
					# print(db.lookupCachedURL_byID(int(sorted_cosine_scores[d])), "--> cosine:", cosine_scores.get(sorted_cosine_scores[d]))
				else:
					item_search_results[title] += cosine_scores.get(d)

			# sorting most common titles by largest total cosine score
			top_items = sorted(item_search_results, key=item_search_results.get, reverse=True)

			print("\n Item Search Results: ", query_raw_input)
			# printing top items and their accumulated cosine scores
			for item in range(len(cosine_scores)):
				print(str(top_items[item].replace("\n", ": ")), item_search_results[top_items[item]], "\n")

			i += 1

			# query_raw_input = input("Enter Another Query or 'QUIT': ")

		return docs_to_items


if __name__ == '__main__':
	# p = PorterStemmer()

	bse = BooleanSearchEngine()
