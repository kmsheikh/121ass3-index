import os
import json
import zipfile
from bs4 import BeautifulSoup
import time
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from tokenizer import computeWordFrequencies
from collections import defaultdict
import psutil
# create an inverted index for the corpus
# tokens = alphanumeric sequences in the dataset
# stemming = better textual matches
# important text = bolded and heading text should be more important!!
# all words will be indexed, no stop words

# load inverted index hash map from main memory into partial index 3+ times during index construction
# partial indexes will be merged in the end

# inverted index maps token -> postings
# posting = representation of token's occurrence in document (doc id/name + tf-idf score)

# m1 -- use token frequency instead of tf-idf score


def indexer():
    # Iterate through the json files found in the zip file
    index = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    lookup_file = open("docID.txt", "a", encoding="utf-8")
    
    with zipfile.ZipFile("developer.zip", "r") as zipped:
        files = zipped.namelist()
        docID = 0
        
        for name in files:
            extension = os.path.splitext(name)[-1]  

            if extension == ".json":
                with zipped.open(name) as json_file:
                    json_content = json_file.read()
                    json_dict = json.loads(json_content)
                    
                    page_soup = BeautifulSoup(json_dict['content'], "html.parser")
                    
                    if check_html:
                        docID += 1
                        lookup_file.write("{} {}\n".format(docID, json_dict["url"]))              # Append to docID lookup table

                        print(f"{psutil.virtual_memory()[2]} percent of RAM used at DOC           # {docID}. Size of DICT is {sys.getsizeof(index)}")
                        
                        text = page_soup.find_all(["p", "pre", "li", "h4", "h5", "h6"])           # Get non-important words from html
                
                        for chunk in text:
                            word_list = tokenize_words(chunk.get_text())
                            word_freq = computeWordFrequencies(word_list)       
                            for key in word_freq:
                                index[key][docID][0] += word_freq[key] 

                        text = page_soup.find_all(["title", "h1", "h2", "h3", "b", "strong"])     # Get "important" words from html (replaces text for memory conservation)
                    
                        for chunk in text:
                            word_list = tokenize_words(chunk.get_text())
                            word_freq = computeWordFrequencies(word_list)  
                            for key in word_freq:
                                index[key][docID][1] += word_freq[key] 


    lookup_file.close()
    
    index_list = sorted(index.items(), key=lambda x: (x[0]))                
    print(f"{psutil.virtual_memory()[2]} percent of RAM used at END")

    with open("WordIndex.txt", "w", encoding="utf-8") as index_file:
        for elem in index_list:
            index_file.write("{} ".format(elem[0])),
        
            for doc, count in elem[1].items():
                index_file.write("{}.{}.{} ".format(doc, count[0], count[1])),
            
            index_file.write("\n")


def tokenize_words(text: str) -> list:
    # Uses nltk to tokenize words and returns list of tuples of the words found in the doc and their frequencies in the doc
    port = PorterStemmer()
    alnum_list = []
    word_list = word_tokenize(text)

    for word in word_list:
        word = port.stem(word)

        if word.isalnum():
            alnum_list.append(word)

    return alnum_list
    
    


if __name__ == "__main__":
    indexer()
