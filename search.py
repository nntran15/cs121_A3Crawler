import os
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

        # Exit program
        if query.lower() == "exit":
            print("Exiting search.")
            break

        results = boolean_query(query, final_dir)

        # No results found
        if not results:
            print("No results found for your query.")
            continue

        # Print results
        print(f"Showing top 5 results...")
        for i, (doc_url, score) in enumerate(results, 1):
            print(f"{i}. {doc_url} (Score: {score})")


def boolean_query(query, final_dir):
    query_tokens = tokenize_query(query)

    # No query tokens return empty
    if not query_tokens:
        return []

    partial_index = load_alphabetical_index(final_dir, query_tokens)

    # Filter valid tokens that exist in partial index
    valid_tokens = [token for token in query_tokens if token in partial_index]

    if not valid_tokens:
        return []

    # Sorting smallest first (to optimize intersection)
    valid_tokens.sort(key=lambda token: len(partial_index[token]))

    # Initialize doc_set with the first token's document set
    doc_set = set(partial_index[valid_tokens[0]].keys())

    # Perform intersection for all valid tokens
    for token in valid_tokens[1:]:  # Start from the second token
        doc_set &= set(partial_index[token].keys())

        # If intersection is empty, return early
        if not doc_set:
            return []

    # Track document scores (only for docs in doc_set)
    document_scores = Counter()

    for token in valid_tokens:
        for doc_url, count in partial_index[token].items():
            if doc_url in doc_set:  # Ensure only intersected docs are scored
                document_scores[doc_url] += count

    # Get top 5 documents with highest scores
    top_docs = heapq.nlargest(5, document_scores.items(), key=lambda x: x[1])

    return [doc for doc, _ in top_docs]  # Return only document URLs



if __name__ == "__main__":
    run_search_interface()