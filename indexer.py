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

import os
import re
import json
from pathlib import Path
from nltk.tokenize import word_tokenize # type: ignore
from nltk.stem import PorterStemmer # type : ignore
from bs4 import BeautifulSoup


documentCount = 0       # Records number of unique documents parsed through
dev_path = "./DEV/"     # Path to the local, UNZIPPED DEV folder
inverted_index = {}     # Complete inverted index storing (token : count)


def parser(file):
    # INPUT: a JSON file
    # OUTPUT: a partial inverted index represented by a set (token : count)

    data = json.load(file)
                    
    # Extract information from .json file
    # NOTE: we use ".get()" since *.json content follows a dictionary format 
    # NOTE: invalid or missing responses return None
    url = data.get("url")
    content = data.get("content")
    encoding = data.get("encoding")     # NOTE: Cannot assume ascii/utf-8! Got some EUC-KR, Windows-1252, ISO-8859-1...

    try:
        # Initialize HTML parser
        soup = BeautifulSoup(content, "html.parser")
        page_text = soup.get_text()

        # Extract bolded text
        bold_texts = [bolded.get_text(strip = True) for bolded in soup.find_all(["b", "strong"])]

        # Extract headings
        header_texts = [headers.get_text(strip = True) for headers in soup.find_all(["h1", "h2", "h3"])]

        # Extract title
        title_texts = [soup.title.string if soup.title.string else None]

        # Extract tokens
        tokens = word_tokenize(page_text)
        tokens = [word for word in tokens if word.isalnum()]

        # Extract stems
        stemmer = PorterStemmer()
        stems = [stemmer.stem(word) for word in tokens]

        print(stems)
    except Exception as e:
        print(f"An error has occurred: {e}")




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


if __name__ == "__main__":

    # Retrieves subfolders under ./DEV/ (i.e. "aiclub_ics_uci_edu", "alderis_ics_uci_edu", etc.)
    list_of_subdirectories = os.listdir(dev_path)

    # Iterates through each subfolder               
    for subdirectory in list_of_subdirectories:

        # Changes relative path to absolute path
        subdirectory_path = Path(dev_path) / subdirectory       

        # Iterates through each .json file in each subfolder
        for json_file in subdirectory_path.rglob("*.json"):
            with json_file.open("r") as file: 
                
                try:
                    parser(file)

                except Exception as e:
                    print(f"Error reading '{json_file.name}': {e}")
