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
            2c) Parser should return a token frequency map (token : count)
        3) Repeat (2) for each document still in the corpus
            3a) Initialize a count for each document for report
        4) Run a sorting algorithm through each frequency map in O(n log n)
        5) Merge each map together (also in O(n log n)) to get a term-document matrix (TDM)
        6) Convert the TDM to an inverted index
        7) Count number of keys == number of tokens
        8) Calculate full inverted index's file size
        9) Print (3a), (7), (8)

    Methods:
        - parser(file) → handles step (2), where "document" = file
        - merge(map1, map2) → merge map1 and map2
        - print_report() → prints data for report 

'''

import os
import json
from pathlib import Path
from nltk.tokenize import word_tokenize # type: ignore
from nltk.stem import PorterStemmer     # type: ignore 
from bs4 import BeautifulSoup


documentCount = 0       # Records number of unique documents parsed through
dev_path = "./DEV/"     # Path to the local, UNZIPPED DEV folder
inverted_index = {}     # Complete inverted index storing (token : documentID)

stop_words = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an',
    'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before',
    'being', 'below', 'between', 'both', 'but', 'by', 'could', 'did', 'do',
    'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
    'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers',
    'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into',
    'is', 'it', "it's", 'its', 'itself', 'just', 'me', 'more', 'most',
    'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only',
    'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 's',
    'same', 'she', "she's", 'should', 'so', 'some', 'such', 't', 'than',
    'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves',
    'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to',
    'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what',
    'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with',
    'you', 'your', 'yours', 'yourself', 'yourselves']
    

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
    
    frequency_map = {}

    try:
        # Initialize HTML parser
        soup = BeautifulSoup(content, "html.parser")
        page_text = soup.get_text()

        # Extract tokens
        tokens = word_tokenize(page_text)
        tokens = [word for word in tokens if word.isalnum()]

        # Extract stems
        stemmer = PorterStemmer()
        stems = [stemmer.stem(word) for word in tokens]
        stems = sorted(stems)

        # Extract bolded text
        bold_texts = [bolded.get_text(strip = True) for bolded in soup.find_all(["b", "strong"])]
        bold_texts = word_tokenize(bold_texts[0])
        bold_texts = [word for word in bold_texts if word.isalnum()]
        bold_texts = [stemmer.stem(word) for word in bold_texts]

        # Extract headings
        header_texts = [headers.get_text(strip = True) for headers in soup.find_all(["h1", "h2", "h3"])]
        header_texts = [stemmer.stem(word) for word in header_texts]

        # Extract title
        title_texts = [soup.title.string.strip()] if soup.title and soup.title.string else []
        title_texts = word_tokenize(title_texts[0])
        title_texts = [word for word in title_texts if word.isalnum()]
        title_texts = [stemmer.stem(word) for word in title_texts]

        # Create token frequency map, increase weights if necessary
        # NOTE: I'm excluding stopwords in bolded, header, and title words when increasing frequency
        for word in stems:
            if word in frequency_map:
                frequency_map[word] += 1
            else:
                frequency_map[word] = 1

        for word in bold_texts:
            if word in stop_words:
                continue
            if word in frequency_map:
                frequency_map[word] += 3
            else:
                frequency_map[word] = 3

        for word in header_texts:   
            if word in stop_words:
                continue
            if word in frequency_map:
                frequency_map[word] += 5
            else:
                frequency_map[word] = 5
        
        for word in title_texts: 
            if word in stop_words:
                continue
            if word in frequency_map:
                frequency_map[word] += 10
            else:
                frequency_map[word] = 10

        print(f"URL: {url}\nTITLE: {soup.title.string.strip()}\nFrequency map: {frequency_map}\n")
    
    except Exception as e:
        print(f"An error has occurred: {e}")
    
    return frequency_map


def merge(map1, map2, json1, json2):
    # INPUT: two frequency maps represented by sets (token : count)
    # OUTPUT: a singular frequency map merged alphabetically from map1 and map2
    # NOTE: I'm going to use the name of the *.json file to uniquely identify documents 

    pass


def print_report():
    # INPUT: none
    # OUTPUT: prints documentCount, tokenCount, indexFileSize

    pass 


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

                # Parse through each .json file 
                parser(file)
