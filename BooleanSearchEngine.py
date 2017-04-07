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
		self.mode = input("Enter SMART Notation for index: ")
		self.query_mode = input("Enter SMART Notation for query: ")
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
		for i in range(len(query_list)):
			query_list[i] = p.stem(query_list[i]).lower()

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
				if doc_id in docid_cosine_dict.keys():
					docid_cosine_dict[doc_id] += query_dict[token] * self.index[token][doc_id][0]
				else:
					docid_cosine_dict[doc_id] = query_dict[token] * self.index[token][doc_id][0]

		return docid_cosine_dict

	def get_results(self):
		db = WebDB('cache.db')

		query_raw_input = input("Enter Query or 'QUIT': ")
		while query_raw_input != 'QUIT':
			item_search_results = {}
			docs_to_items = {}

			query_list = list(query_raw_input.split(' '))

			# cosine_scores is a dictionary with doc_ids mapped to cosine score
			cosine_scores = self.query_score(query_list, self.query_mode)

			sorted_cosine_scores = sorted(cosine_scores, key=cosine_scores.get, reverse=True)

			print("\n URL search results: ")
			for d in range(len(sorted_cosine_scores)):
				(url, docType, title) = db.lookupCachedURL_byID(int(sorted_cosine_scores[d]))
				docs_to_items[sorted_cosine_scores[d]] = str(title).strip("\n")
				if title not in item_search_results.keys():
					item_search_results[title] = cosine_scores.get(sorted_cosine_scores[d])
					print(db.lookupCachedURL_byID(int(sorted_cosine_scores[d])), "--> cosine:", cosine_scores.get(sorted_cosine_scores[d]))
				else:
					item_search_results[title] += cosine_scores.get(sorted_cosine_scores[d])

			# sorting most common titles by largest total cosine score
			top_items = sorted(item_search_results, key=item_search_results.get, reverse=True)

			# printing top 3 items and their accumulated cosine scores
			print("\n Item Search Results: \n", str(top_items[0]).replace("\n", ": "), item_search_results[top_items[0]], "\n",
			      str(top_items[1]).replace("\n", ": "), item_search_results[top_items[1]], "\n",
			      str(top_items[2]).replace("\n", ": "), item_search_results[top_items[2]], "\n")

			print("---------------------------------")

			query_raw_input = input("Enter Another Query or 'QUIT': ")

		return docs_to_items


if __name__ == '__main__':
	p = PorterStemmer()

	bse = BooleanSearchEngine()
