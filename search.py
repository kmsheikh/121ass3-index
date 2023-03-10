# QUERY PROCESSING
    # Signal hander installed to quit with crtl+c
    # Using vocab.txt for byte positions, 
    # Seek() the lines in index to solve query

# TO DO:
    # Implment ranking, calculate tf-idf with document weights
    # Prompt user, search interface


from tokenizer import *
import glob
from ntpath import basename
import sys
import asyncio
import signal
import time
import glob
from ntpath import basename
import sys
import asyncio
import signal
from functools import partial


def search_engine():
    # LOADING AUXILARY FILES INTO MEMORY
    vocab_dict = dict()
    with open("vocab.txt", "r", encoding="utf-8") as vocab_file:        # vocab_dict stores token byte_position
        for line in vocab_file:
            (word, byte) = line.split()
            vocab_dict[word] = int(byte)
    
    with open("stopwords.txt", "r") as stop_file:                       # Stop words for filtering queries
        stop_list = stop_file.read().split()
    
    lookup_dict = dict()
    with open("docID.txt", "r", encoding="utf-8") as lookup_file:       # lookup_dict stores docID website
        for line in lookup_file:
            (ID, doc) = line.split()
            lookup_dict[int(ID)] = doc
    
    # INTRO TEXT
    # explain what to search
    # how to quit (after every timestamp?)


    # GET KEYBOARD INPUT
    while(1):
        query = input("Enter your query:\n\t")
        start = time.time()                                         # TIME SEARCH RESULTS       
        postings_lists = gather_postings(query, vocab_dict, index_dict, stop_list)
        


def gather_postings(the_query: str, vocab_dict: dict, index_dict: dict, stop_list: list)->list:
    query_list = tokenize_words(the_query)
    query_set = set()
    for word in query_list:
        if word not in stop_list:
            query_set.add(word)                                     # Lose duplicates and stop words in query

    # GET WORD and POSTINGS FROM THE INDEX
    found_list = extract_postings(vocab_dict, query_list, index_dict)      
    if len(found_list) < len(query_set) or len(found_list) == 0:    # If not all search terms found, return empty list
        return []

    # PARSE POSTING ENTRY, remove tokens
    postings_lists = []                                                
    for found in found_list:    
        entry_list = found.split()                                  # Split entry by whitespace: [word  1/0.0  2/0.0] 
        entry_list.pop(0)                                           # Remove token from parsed entry_list
        postings_lists.append(entry_list)                                      # Append [1/0.0 2/0.0] to postings_list

    return postings_lists


def extract_postings(vocab_dict: dict, query_set: set, index_dict: dict) -> list:
    postings = []
    for word in query_set:
        if word in vocab_dict:
            index_dict[word[0]].seek(vocab_dict[word])  
            postings.append(index_dict[word[0]].readline())   # Append line found in partial_index

    return postings



async def sigint_handler(g_index_dict, signum, frame):
    print("\n\tExiting...\n")
    
    # CLOSE ALL OPEN INDEXES
    for key in g_index_dict.keys():
        g_index_dict[key].close()

    sys.exit(0)



if __name__ == "__main__":
    # OPEN INDEX FILES, save opened files in dict for closing later
    g_index_dict = {}
    index_files = glob.glob("patial-index/*") 
    for file in index_files:
        txt = basename(file)                                                # Retrieve tail of path "a.txt" with basename
        g_index_dict[txt[0]] = open(file, "r", encoding="utf=8")

    signal.signal(signal.SIGINT, partial(sigint_handler, g_index_dict)      # Install signal handler for crtl+C
    
    search_engine()
