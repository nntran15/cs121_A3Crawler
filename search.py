import os
import time
import pickle
from nltk.tokenize import word_tokenize # type: ignore
from nltk.stem import PorterStemmer     # type: ignore
from collections import Counter
import heapq
import indexer

# CHANGE THIS VARIABLE TO SHOWCASE HOW MANY URLS ARE DISPLAYED
url_count = 5
final_dir = "./index/"


def tokenize_query(query):
    # INPUT: user query
    # OUTPUT: tokenized user query

    stemmer = PorterStemmer()
    tokens = word_tokenize(query.lower())
    tokens = [stemmer.stem(word) for word in tokens if word.isalnum()]
    return tokens


def load_alphabetical_index(final_dir, query_tokens):
    # Load n alphabetical indexes corresponding to the n unique first letters of user query
    # INPUT:
    #  - final_dir: where alphabetical indexes are stored
    #  - query_tokens: tokens from user query
    # OUTPUT: the n alphabetical partial inverted indexes loaded into memory

    # Retrieves, as a list, the first letter of every token
    first_letters = {token[0].upper() for token in query_tokens if token} 

    # Load the first_letter partial indexes
    partial_index = {}
    for letter in first_letters:
        file_path = os.path.join(final_dir, f"terms_{letter}.pkl")
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                letter_index = pickle.load(file)
                partial_index.update(letter_index)

    return partial_index 


def search(query, final_dir):
    # Helper function to return the top url_count files 
    # INPUT:
    #  - query: user query
    #  - final_dir: where alphabetical indexes are stored
    # OUTPUT: top url_count links associated with the user query

    global url_count
    
    # Tokenize and stem the query
    query_tokens = tokenize_query(query)

    # Avoid empty queries
    if not query_tokens:
        return []
    
    # Load the partial index associated with the user query
    partial_index = load_alphabetical_index(final_dir, query_tokens)

    # Track document scores
    document_scores = Counter()

    # For each token in the query
    for token in query_tokens:
        if token in partial_index:
            # Retrieve documents containing token
            doc_map = partial_index[token]

            # Update scores for each document
            for doc_url, count in doc_map.items():
                document_scores[doc_url] += count
            
    # Get top 5 documents with highest scores
    top_docs = heapq.nlargest(5, document_scores.items(), key=lambda x: x[1])

    return top_docs


def run_search_interface():
    # Runs the prompt and showcases user query results

    global final_dir

    print("\nNote: Enter 'exit' to quit program.")
    while True:
        query = input("\nEnter your search query: ")
        # Start a timer to measure how long it would take to query our results
        time_start = time.perf_counter()

        # Exit program
        if query.lower() == "exit":
            print("Exiting search.")
            break

        results = search(query, final_dir)
        bool_query = boolean_query(query, final_dir) # gets a boolean query between query indicies
        bq_timer_end = time.perf_counter() # ending timestamp for boolean search query

        #End the timer
        time_end = time.perf_counter()
        elapsed_time = (time_end - time_start) * 1000 # calculates our query time in ms
        bq_elapsed = (bq_timer_end - bq_timer_start) * 1000 # calculates boolean query search time in ms
        
        # No results found
        if not results:
            print("No results found for your query.")
            print(f"Querying took {elapsed_time:.3f} ms")
            continue
        
        # Print results
        print(f"Showing top 5 results...")
        for i, (doc_url, score) in enumerate(results, 1):
            print(f"{i}. {doc_url} (Score: {score})")
        print(f"Querying took {elapsed_time:.3f} ms")
        
        # (i actually have no idea how this will be printed)
        
        # print("Boolean query exists within these documents: ")
        # for doc in bool_query:
        #     print(doc, end=" ")
        # print(f"Boolean querying took {bq_elapsed:.3f} ms")


def boolean_query(query, final_dir):
    global bq_timer_start
    
    query_tokens = tokenize_query(query)

    #No query tokens return empty
    if not query_tokens:
        return []
    
    bq_timer_start = time.perf_counter()

    partial_index = load_alphabetical_index(final_dir, query_tokens)

    #If the tokens in the partial aren't in the partial index return
    valid_tokens = [token for token in query_tokens if token in partial_index]

    if not valid_tokens:
        return []

    #Sorting smallest first
    valid_tokens.sort(key=lambda token: len(partial_index[token]))

    #Setting the document set to our first query valid token
    doc_set = set(partial_index[valid_tokens[0]].keys())
    
    #Loop through the query tokens, set the document to whatever our key is
    for token in query_tokens:
        doc_set &= set(partial_index[token].keys())

        #if there is no common return an empty list
        if not doc_set:
            return []

    return list(doc_set)


if __name__ == "__main__":
    run_search_interface()