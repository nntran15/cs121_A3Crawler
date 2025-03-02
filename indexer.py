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


    PROGRAM STRUCTURE:

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
        5) Merge each map together (also in O(n log n)) to get a partially inverted index
        6) Every <batch_size> processed .json files, save the PII to disk
        7) Merge all PIIs to get final inverted index
        8) Count number of keys == number of tokens
        9) Calculate full inverted index's file size
        10) Print (3a), (8), (9)
'''

import os
import json
import pickle
from pathlib import Path
from nltk.tokenize import word_tokenize # type: ignore
from nltk.stem import PorterStemmer     # type: ignore 
from bs4 import BeautifulSoup
from collections import defaultdict

documentCount = 0                                       # Records number of unique documents parsed through
dev_path = "./DEV/"                                     # Path to the local, UNZIPPED DEV folder
output_dir = "./tmp/"                                   # Where all partial indexes to disk will be saved
final_dir = "./index/"                                  # Where completed indexes to disk will be saved
final_index = defaultdict(lambda: defaultdict(int))     # Complete inverted index storing (token : (document : count))
batch_size = 1000                                       # Maximum number of iterated-through *.json file before we save to disk
    

def save_partial_inverted_index(inverted_index, filename):
    # INPUT: an inverted index and a desired filename
    # OUTPUT: inverted index saved onto disk

    os.makedirs(os.path.dirname(filename), exist_ok = True)     # Make directory if does not exist
    tmp = dict(inverted_index)                                  # json.dump doesn't work well with defaultdict

    with open(filename, "wb") as file:
        pickle.dump(tmp, file)


def load_partial_inverted_index(filename):
    # INPUT: an inverted index's filename on disk
    # OUTPUT: inverted index loaded into memory

    with open(filename, "rb") as file:
        return pickle.load(file)
    

def merge_partial_inverted_index_with_frequency_map(inverted_index, freq_map, doc_name):
    # INPUT: 
    #   - inverted_index: a created inverted_index (token : (doc_name : count))
    #   - freq_map: a frequency_map of (token : count)
    #   - doc_name: the unique document name to increase in inverted_index
    # OUTPUT: freq_map included in inverted_index

    for token, count in freq_map.items():       
        inverted_index[token][doc_name] += count
    return inverted_index


def merge_partial_indexes(output_dir, final_dir, filename_format, num_partial_indexes):
    # INPUT:
    #   - final_dir: a path to save the combined index
    #   - filename_format: adds the 0,1,2,... to the end of the saved index
    #   - num_partial_indexes: number of created partial indexes we need to combine
    # OUTPUT: a final inverted index

    global final_index

    # Iterate through all partial indexes
    for i in range(num_partial_indexes):
        partial_filename = os.path.join(output_dir, filename_format.format(batch_id=i))
        partial_index =  load_partial_inverted_index(partial_filename)

        # Iterate through each partial index to add to final_index
        for token, doc_map in partial_index.items():    # For each partial index (token : (doc_id : count)), where doc_map = (doc_id : count) 
            for doc_id, count in doc_map.items():       # For each (doc_id : count) item
                final_index[token][doc_id] += count     # Add to final index (token : (doc_id : count += count))

    # Save to disk
    split_final_index_alphabetically(final_index, final_dir)
    save_partial_inverted_index(final_index, os.path.join(final_dir, "final_inverted_index.pkl"))
    print("Final inverted index saved.")


def process_files(dev_path, output_dir, final_dir):
    # INPUT:
    #   - dev_path: a path to the /DEV/ folder with all the .json files
    #   - output_dir: where to store inverted indexes on disk
    # OUTPUT: a complete inverted index storing (token : (document : count))

    count = 0                                                       # Number of processed .json files so far
    partial_index_counter = 0                                       # Number of PIIs on disk
    partial_index_filename_format = "partial_index_{batch_id}.pkl"  # Format of each PII on disk
    inverted_index = defaultdict(lambda: defaultdict(int))                                      
    global documentCount

    # Iterate through each subfolder in the ./DEV/ directory
    for subdirectory in os.listdir(dev_path):
        subdirectory_path = Path(dev_path) / subdirectory   # Converts the relative path to each subfolder to an absolute path
        json_files = subdirectory_path.rglob("*.json")      # Creates a list of .json files within the subfolder

        # Iterate through each .json file in each subfolder
        for json_file in json_files:

            # If we have <count> partial indexes in memory, save to disk
            if count % batch_size == 0 and count > 0:
                partial_index_filename = os.path.join(output_dir, partial_index_filename_format.format(batch_id=partial_index_counter))     # Format for each PII on disk: ./tmp/partial_index_<0, 1, 2, ...>.json
                print(f"Saving result to disk under name: {partial_index_filename}.")
                save_partial_inverted_index(inverted_index, partial_index_filename)                                                         # Save PII to disk
                partial_index_counter += 1                                                                                              
                inverted_index = defaultdict(lambda: defaultdict(int))                                                                      # Create a new PII in memory to merge freq_maps into

            # Open .json file for extracting
            with json_file.open("r") as file:
                data = json.load(file)
                url = data.get("url")
                content = data.get("content")
                freq_map = parser(content)                                                                                                     # Create a parser to extract the .json file 
                inverted_index = merge_partial_inverted_index_with_frequency_map(inverted_index, freq_map, url)                             # Merge each freq_map to the PII
                documentCount += 1
            
            count += 1
    
    # Saves the final partial PPI (not a typo) to disk
    if inverted_index:
        partial_index_filename = os.path.join(output_dir, partial_index_filename_format.format(batch_id=partial_index_counter))
        save_partial_inverted_index(inverted_index, partial_index_filename)
        partial_index_counter += 1
    
    # After all .json files parsed and PIIs created, merge all PIIs together as a single inverted index
    print("All partially inverted indexes saved. Now merging...")
    merge_partial_indexes(output_dir, final_dir, partial_index_filename_format, partial_index_counter)
        

def parser(content):
    # INPUT: a JSON file
    # OUTPUT: a partial inverted index represented by a set (token : count)

    number_tokens_before_stemming = 0
    number_tokens_after_stemming = 0

    # Skip empty content
    if not content:
        return {}
    
    try:
        # Initialize HTML parser
        soup = BeautifulSoup(content, "html.parser")
        page_text = soup.get_text()

        # Extract tokens
        tokens = word_tokenize(page_text)
        tokens = [word for word in tokens if word.isalnum()]
        number_tokens_before_stemming = len(set(tokens))

        # Extract stems
        stemmer = PorterStemmer()
        stems = [stemmer.stem(word) for word in tokens]
        number_tokens_after_stemming = len(set(stems))

        # Extract bolded text
        bold_texts = [bolded.get_text(strip = True) for bolded in soup.find_all(["b", "strong"])]
        bold_texts = word_tokenize(" ".join(bold_texts))
        bold_texts = [stemmer.stem(word) for word in bold_texts if word.isalnum()]

        # Extract headings
        header_texts = [headers.get_text(strip = True) for headers in soup.find_all(["h1", "h2", "h3"])]
        header_texts = word_tokenize(" ".join(header_texts))
        header_texts = [stemmer.stem(word) for word in header_texts if word.isalnum()]

        # Extract title
        title_texts = []
        if soup.title and soup.title.string:
            title_texts = [soup.title.string.strip()] if soup.title and soup.title.string else []
            title_texts = word_tokenize(title_texts[0])
            title_texts = [stemmer.stem(word) for word in title_texts if word.isalnum()]

    except Exception as e:
        print(f"An error has occurred while extracting info: {e}")
        return {}

    try: 
        # Create token frequency map, increase weights if necessary
        frequency_map = defaultdict(int)

        for word in stems:
            frequency_map[word] += 1

        for word in bold_texts:
            frequency_map[word] += 3

        for word in header_texts:   
            frequency_map[word] += 5
        
        for word in title_texts: 
            frequency_map[word] += 10

        print(f"Found {number_tokens_before_stemming} of tokens before stemming, and {number_tokens_after_stemming} of tokens after stemming.")
    
        return frequency_map
    
    except Exception as e:
        print(f"An error has occurred while creating frequency_map: {e}")
        return {}


def split_final_index_alphabetically(final_index, final_dir):
    # INPUT: final inverted index dictionary object, where to store it
    # OUTPUT: the final inverted index split alphabetically
    # Ex.   final_index = {
    #           "ant": {"doc1.json": 2, "doc2.json": 1}, 
    #           "both": {"doc1.json": 2}, 
    #           "cat": {"doc3.json": 4},
    #           "cactus:" {"doc1.json": 2}
    #       }
    #       split_index = {
    #           "A": {"ant": {"doc1.json": 2, "doc2.json": 1}},
    #           "B": {"both": {"doc1.json": 2}},
    #           "C": {"cat": {"doc3.json": 4}, "cactus": {"doc1.json": 2}}
    #       }
    # NOTE: sorry  

    split_final = defaultdict(dict)

    # Iterate through final index where token = "ant", doc_map = {"doc1.json": 2, "doc2.json": 1}
    for token, doc_map in final_index.items():
        first_letter = token[0].upper()
        split_final[first_letter][token] = doc_map
    
    # Save each term to a separate file so we don't have to load everything into memory
    for letter, terms in split_final.items():
        filename = os.path.join(final_dir, f"terms_{letter}.pkl")
        save_partial_inverted_index(terms, filename)
    
    print("Final index successfully split alphabetically.")
    
def getQuery():
    query = input("Enter your query: ")

if __name__ == "__main__":
    process_files(dev_path, output_dir, final_dir)

    # Results
    print(f"\nNumber of documents indexed through: {documentCount}")
    print(f"Number of unique tokens: {len(final_index)}")
    final_index_location = os.path.join(final_dir, "final_inverted_index.pkl")
    print(f"Size of the inverted index on disk: {os.path.getsize(final_index_location)/1000} kilobytes")