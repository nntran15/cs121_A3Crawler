import os
import time
import pickle
from nltk.tokenize import word_tokenize # type: ignore
from nltk.stem import PorterStemmer     # type: ignore
from collections import Counter
import heapq
import math

# CHANGE THIS VARIABLE TO SHOWCASE HOW MANY URLS ARE DISPLAYED
url_count = 5

# CHANGE THIS TO WHERE PARTIAL ALPHABETICAL INDEXES ARE STORED
final_dir = "./index/"


# Stop words to be filtered
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


def tokenize_query(query, remove_stopwords):
    # Tokenizes a user's query with the 
    # INPUT:
    #   - query: the user's query
    #   - remove_stopwords: boolean whether we want to remove (TRUE) or keep stopwords (FALSE)
    # OUTPUT: tokenized user query

    stemmer = PorterStemmer()
    tokens = word_tokenize(query.lower())

    # Filter stopwords if remove_stopwords = True
    if remove_stopwords:
        tokens = [word for word in tokens if word.isalnum() and word.lower() not in stop_words]
    else:
        tokens = [word for word in tokens if word.isalnum()]

    # Apply stemming
    tokens = [stemmer.stem(word) for word in tokens]

    return tokens


def load_partial_inverted_index(filename):
    # Load a pickle file into memory
    # INPUT: an inverted index's filename on disk
    # OUTPUT: inverted index loaded into memory

    with open(filename, "rb") as file:
        return pickle.load(file)


def find_chunk_for_term(term, final_dir):
    # Since terms.pkl files are lexographically sorted and broken into different chunk sizes (defined on indexer.py), we can avoid going through each individual .pkl file to find a term
    # "key_{first_letter}.pkl" holds a tuple of every last term in an index along with the index name: (term : file name where the term the last term in)
    # Function shifts through all keys.pkl and compares a searched-for term and the last term in every .pkl file
    # Ex. term = "apple", key_A.pkl contains (aaaa : term_AP1.pkl), (aabb : term_AP2.pkl), (azzz : term_AP3.pkl). So "apple" must be in term_AP3.pkl
    # INPUT:
    #   - term: term we want to find the term.pkl file for
    #   - final_dir: where alphabetical indexes are stored
    # OUTPUT:
    #   - returns both the term.pkl file and filename of the file

    first_letter = term[0].upper()

    # Load lookup dictionary for letter
    lookup_file = os.path.join(final_dir, f"key_{first_letter}.pkl")
    lookup_dict = load_partial_inverted_index(lookup_file)

    # Search for term.pkl file
    target_file = None
    for last_term, file in sorted(lookup_dict.items()):
        if term <= last_term:
            target_file = file
            break
    
    # No associated term.pkl file found
    if target_file is None:
        return None, None
    
    # Load chunk file
    chunk_data = load_partial_inverted_index(target_file)

    return chunk_data, target_file


def load_term_data(query_tokens, final_dir):
    # Parent function for find_chunk_for_term
    # Receives ALL user query tokens then loads each associated term.pkl file for each token
    # INPUT:
    #   - query_tokens: the user's query
    #   - final_dir: where alphabetical indexes are stored
    # OUTPUT:
    #   - A dictionary (token : its associated term.pkl file)
    #   - ALL term.pkl files into memory

    term_data = {}      # Stores term information as a dictionary: (token : its associated term.pkl file)
    loaded_chunks = {}  # Cache for loaded chunks of inverted indices that have already been loaded

    # Iterates through query tokens
    for token in query_tokens:

        # Checks for invalid tokens
        if not token:
            continue
        
        # Checks for if token exists in already loaded chunks
        token_found = False
        for chunk_data in loaded_chunks.values():
            if token in chunk_data:
                term_data[token] = chunk_data[token]
                token_found = True
                break

        # Found in cache
        if token_found:
            continue

        # Not found in cache
        chunk_data, chunk_filename = find_chunk_for_term(token, final_dir)

        # Valid data found -> store in cache
        if chunk_data and chunk_filename:
            loaded_chunks[chunk_filename] = chunk_data
            if token in chunk_data:
                term_data[token] = chunk_data[token]
        
    return term_data


def search(query, final_dir):
    # Helper function to return the top url_count files for a user query
    # INPUT:
    #  - query: user query
    #  - final_dir: where alphabetical indexes are stored
    # OUTPUT: top url_count links associated with the user's query

    global url_count

    # Check if boolean "AND" in the query
    if " AND " in query:
        return boolean_query(query, final_dir)

    # Tokenize and stem the query
    query_tokens = tokenize_query(query, True)

    # Avoid empty queries
    if not query_tokens:
        return []
    
    # Load the partial index associated with the user query
    term_data = load_term_data(query_tokens, final_dir)

    # Track tf-idf scores
    document_scores = Counter()

    N_directory = os.path.join(final_dir, f"total_documents.pkl")
    N = load_partial_inverted_index(N_directory)

    # Calculate tf-idf scores
    for token in query_tokens:
        if token in term_data:
            doc_map = term_data[token]
            dft = len(doc_map)
            if dft > 0:
                for doc_url, count in doc_map.items():
                    tftd = count
                    wtd = (1+math.log(tftd) * math.log(N/dft))
                    document_scores[doc_url] += wtd

    # Get top 5 documents with highest scores
    top_docs = heapq.nlargest(url_count, document_scores.items(), key=lambda x: x[1])

    return top_docs


def boolean_query(query, final_dir):
    # Helper function to return documents that contain ALL terms of a user's query
    # INPUT: 
    #  - query: user query
    #  - final_dir: where alphabetical indexes are stored
    # OUTPUT:
    #  - top url_count links associated with ALL parts of a user's query

    # Split query
    query_parts = query.split(" AND ")

    # Tokenize each part of the query
    tokenized_parts = []
    for part in query_parts:
        tokens = tokenize_query(part, True)
        if tokens:
            tokenized_parts.append(tokens)
    
    # Avoid no valid parts
    if not tokenized_parts:
        return []

    # Get rid of empty lists in the list of lists 
    query_tokens = [token for part in tokenized_parts for token in part]

    # Load partial index associated with the user query
    term_data = load_term_data(query_tokens, final_dir)

    # Running list to track intersection of documents
    candidate_docs = None

    # Iterates through all query tokens (not including "AND" of course)
    for tokens in tokenized_parts:
        part_docs = set()

        # Track only the tokens found in term_data == term.pkl files (recall: (term : (docID : freq)))
        valid_tokens = [token for token in tokens if token in term_data]

        # No tokens found in term.pkl files
        if not valid_tokens:
            return []
        
        # Store all document IDs that contain tokens in valid_tokens
        for token in valid_tokens:
            part_docs.update(term_data[token].keys())
        
        # Perform intersection on documents in candidate_docs to ensure AND
        if candidate_docs is None:
            candidate_docs = part_docs
        else:
            candidate_docs &= part_docs
        
        # No intersection between any documents
        if not candidate_docs:
            return []

    # Track tf-idf scores
    document_scores = Counter()

    N_directory = os.path.join(final_dir, f"total_documents.pkl")
    N = load_partial_inverted_index(N_directory)

    # Calculate tf-idf scores
    for token in query_tokens:
        if token in term_data:
            dft = len(term_data[token])
            if dft > 0:   
                idf = math.log(N / dft)
                for doc_id in candidate_docs:
                    if doc_id in term_data[token]:
                        tf = term_data[token][doc_id]
                        wtd = (1+math.log(tf) * math.log(N/dft))
                        document_scores[doc_id] += wtd
    
    # Get top 5 documents with highest scores
    top_docs = heapq.nlargest(url_count, document_scores.items(), key=lambda x: x[1])

    return top_docs


def run_search_interface():
    # Runs the prompt and showcases user query results

    global final_dir

    # Prompts
    print("\nNote: Enter 'exit' to quit program.")
    print("Note 2: use 'AND' between terms to find documents containing both terms.")

    # Continue until user enters "exit"
    while True:
        query = input("\nEnter your search query: ")
        
        # Start a timer to measure how long it would take to query our results
        time_start = time.perf_counter()

        # Exit program
        if query.lower() == "exit":
            print("Exiting search.")
            break
        
        # Go through index using query terms
        results = search(query, final_dir)

        # End the timer
        time_end = time.perf_counter()
        elapsed_time = (time_end - time_start) * 1000 # calculates our query time in ms
        
        # No results found
        if not results:
            print("No results found for your query.")
            print(f"Querying took {elapsed_time:.3f} ms")
            continue
        
        # Print results
        print(f"Showing top 5 results...")
        for i, (doc_url, score) in enumerate(results, 1):
            print(f"{i}. {doc_url} (TF-IDF score: {score:.3f})")
        print(f"Querying took {elapsed_time:.3f} ms\n")


if __name__ == "__main__":
    run_search_interface()