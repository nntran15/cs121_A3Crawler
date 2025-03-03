import os
import time
import pickle
from nltk.tokenize import word_tokenize # type: ignore
from nltk.stem import PorterStemmer     # type: ignore
from collections import Counter
import heapq

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
    # INPUT: user query
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

    # Check if boolean "AND" in the query
    if " AND " in query:
        return boolean_query(query, final_dir)

    # Tokenize and stem the query
    query_tokens = tokenize_query(query, True)

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


def boolean_query(query, final_dir):

    # Splits user query into parts
    # Ex. query = "computer science AND AI" -> tokenized_terms = [["computer", "science"], ["AI"]]
    query_parts = query.split(" AND ")
    tokenized_terms = [tokenize_query(term, True) for term in query_parts]

    # Filter empty terms lists since previous method may create empty lists from filtering stopwords
    tokenized_terms = [terms for terms in tokenized_terms if terms]

    # Condense list of lists into a single list
    all_query_tokens = [token for terms_tokens in tokenized_terms for token in terms_tokens]

    # Empty query
    if not all_query_tokens:
        return []

    # Load associated alphabetical indexes
    partial_index = load_alphabetical_index(final_dir, all_query_tokens)

    # Goes through each document looking for tokenized_terms
    documents_with_terms = []
    for term_tokens in tokenized_terms:
        # Filter valid tokens that exist in partial index
        valid_tokens = [token for token in term_tokens if token in partial_index]

        # No terms in partial index
        if not valid_tokens:
            return []
        
        # Retrieves documents for each token in valid_tokens
        doc_set = set()
        for token in valid_tokens:
            if not doc_set:
                # Adds to list
                doc_set = set(partial_index[token].keys())
            else:
                # Prevents duplicates   
                doc_set |= set(partial_index[token].keys())

        documents_with_terms.append(doc_set)

    # No documents containing tokenized words
    if not documents_with_terms:
        return []

    # Perform intersection for all valid tokens
    list_of_docs = documents_with_terms[0]

    for docs in documents_with_terms[1:]:  # Start from the second token
        list_of_docs &= docs

        # If intersection is empty, return early
        if not list_of_docs:
            return []

    # Track document scores (only for docs in doc_set)
    document_scores = Counter()

    for token in all_query_tokens:
        if token in partial_index:
            for doc_url in list_of_docs:
                if doc_url in partial_index[token]:
                    document_scores[doc_url] += partial_index[token][doc_url]

    # Get top url_count documents with highest scores
    top_docs = heapq.nlargest(url_count, document_scores.items(), key=lambda x: x[1])

    return top_docs  # Return only document URLs


def run_search_interface():
    # Runs the prompt and showcases user query results

    global final_dir

    print("\nNote: Enter 'exit' to quit program.")
    print("Note 2: use 'AND' between terms to find documents containing both terms.")
    while True:
        query = input("\nEnter your search query: ")
        
        # Start a timer to measure how long it would take to query our results
        time_start = time.perf_counter()

        # Exit program
        if query.lower() == "exit":
            print("Exiting search.")
            break
        
        results = search(query, final_dir)

        #End the timer
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
            print(f"{i}. {doc_url} (Score: {score})")
        print(f"Querying took {elapsed_time:.3f} ms\n")


if __name__ == "__main__":
    run_search_interface()