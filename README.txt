Lab1 & Lab2:
    To run: run WebCrawler.py to build the document collection

    Note: if the directories clean, header, and raw do not exist this program will create them

    I deleted the raw and header directories so when you run WebCrawler.py it will create them

    If I were to re-write labs 1 & 2 I would organize my code better with less in main. As the labs went on I
    changed my coding style to utilize the initializer and focus on Object Oriented Code

Lab3 - BooleanRetrieval
    The code for this lab was located in BooleanSearchEngine.py but now has been changed to suit the needs for lab4

    The previously present code supported single token queries, phrase queries, and queries involving the AND, OR,
    and NEAR operators. It had a simple interactive text-based user interface that was used to show off this query
    functionality. The report specific statistics about the results from various queries is location on the course wiki.

Lab4
    To run: run BooleanSearchEngine.py

    Enter SMART Notation for index and query, if you do not enter anything or enter an invalid input the default is 'ltc.ltc'

    BooleanSearchEngine.py includes:
        Code to create TF-IDF weights and normalize document vectors
        Code to calculate cosine scores for each webpage given a query
        Code to find top scoring items for a query
        A bunch of sample queries can be typed in by the user
            (e.g., distorted electric guitar, nobel prize, romance comedy)

Lab 5 is located in the pycharm project lab5 in separate zip file!!