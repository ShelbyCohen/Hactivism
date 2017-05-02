from bs4 import BeautifulSoup
import urllib.request
import string
from nltk.tokenize import wordpunct_tokenize
from nltk.stem import PorterStemmer
import os
from WebDB import WebDB
from google import search


class WebCrawler:
    def __init__(self):
        print(self)

    def parser(self, page):
        mySpider = WebCrawler()
        soup = BeautifulSoup(page, 'html.parser')

        # remove all script tags in page
        to_extract = soup.findAll('script')
        [item.extract() for item in to_extract]

        text = soup.get_text()
        tokens = wordpunct_tokenize(text)

        # removes punctuation
        tokens = [token.strip(string.punctuation) for token in tokens]

        # filter out empty spots
        tokens = list(filter(None, tokens))
        tokens = mySpider.lower(tokens)
        tokens = mySpider.stem(tokens)

        return tokens

    # normalize
    def lower(self, token_list):
        lower_token_list = [word.lower() for word in token_list]

        return lower_token_list

    def stem(self, token_list):
        word = PorterStemmer()
        stem_token_list = [word.stem(token) for token in token_list]

        return stem_token_list

    def get_terms(self, token_list):
        unique_token_list = list(set(token_list))
        unique_token_list.sort()

        return unique_token_list


if __name__ == '__main__':

    mySpider = WebCrawler()
    db = WebDB('cache.db')

    path = "data/"
    raw_path = path + "raw/"
    clean_path = path + "clean/"
    header_path = path + "header/"
    item_path = path + "item/"

    if not os.path.exists(raw_path):
        os.makedirs(raw_path)

    if not os.path.exists(clean_path):
        os.makedirs(clean_path)

    count = 0
    valid_pages = 0
    file_path = os.path.dirname(item_path)
    for file in os.listdir(file_path):
        item_file = open(item_path + file, "r")
        for line in item_file.readlines():
            count += 1
            valid_pages = 0
            url_list = search(str(line) + " activism movement")
            for url in list(url_list):
                try:
                    if valid_pages < 10:
                        print(line, " count --> ", count, "--> url: ", url)
                        urllib.request.urlretrieve(url, raw_path + str(count) + ".txt")

                        raw_page = open(raw_path + str(count) + ".txt", 'r')
                        tokens = mySpider.parser(raw_page)
                        target = open(clean_path + str(count) + ".txt", 'a')
                        [target.write(t + "\n") for t in tokens]
                        target.close()

                        urlID = db.insertCachedURL(url, "text/html", line)
                        itemID = db.insertItem(line, file)
                        u2iID = db.insertURLToItem(urlID, itemID)

                        valid_pages += 1
                    else:
                        break
                except:
                    continue
