''' INSTRUCTIONS:

    Given a list of .json documents found in ./dev/, create an inverted index containing
    all tokens from all documents and their associated count. Report should contain: 
        1) Number of documents indexed through
        2) Number of tokens
        3) Total size of index on disk

    For instance:
        INPUT:
            - Doc 1: "dog sits on the mat"
            - Doc 2: "cat sits on the mat"
            - Doc 3: "cat and dogs are friends"
        PROGRAM:
            What the inverted index looks like in memory:
            - "cat"  → [Doc1, Doc3]
            - "dog"  → [Doc2, Doc3]
            - "sits" → [Doc1, Doc2]
            - "mat"  → [Doc1, Doc2]
        OUTPUT:
            1) Doc1, Doc2, Doc3
            2) 4
            3) ... kB

    JSON structure:
        url: contains the URL of the page. Ignore the fragment parts, if you see them around
        content: contains the content of the page, as found during crawling
        encoding: an indication of the encoding of the webpage
'''

''' PROGRAM STRUCTURE:

    Steps:
        1) Create a global data structure to hold inverted index
        2) Create a parser to go through a document
            NOTE: I'm assuming we won't have to analyze validity like Assignment2
            2a) Parser should be able to detect "broken HTML" (via Assignment3 page)
            2b) Parser should tokenize words from on the document
            2c) Parser should return a "partial index" list (token : count)
        3) Repeat (2) for each document still in the corpus
            3a) Initialize a count for each document for report
        4) Run a sorting algorithm through each partial index in O(n log n)
        5) Merge each partial index together also in O(n log n)-- mergesort?
        6) Count number of keys == number of tokens
        7) Calculate file size
        8) Print (3a), (6), (7)

    Methods:
        - parser(file) → handles step (2), where "document" = file
        - sort(index) → sort the inputted partial index
        - merge(index1, index2) → merge index1 and index2
        - print_report() → prints data for report 

'''

documentCount = 0   # Records number of unique documents parsed through


def parser(file):
    # INPUT: a JSON file
    # OUTPUT: a partial inverted index represented by a set (token : count)
     
    return


def sort(index):
    # INPUT: a partial inverted index represented by a set (token : count)
    # OUTPUT: the index sorted alphabetically by the key (the token)

    return


def merge(index1, index2):
    # INPUT: two partially inverted indexes represented by sets (token : count)
    # OUTPUT: a singular partially inverted index merged alphabetically from index1 and index2

    return


def print_report():
    # INPUT: none
    # OUTPUT: prints documentCount, tokenCount, indexFileSize

    return 


def main():
    return