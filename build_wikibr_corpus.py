#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Build a text corpus from wikipedia br dumps
 Outputs text files:
    * "corpus/wiki_corpus.txt", the main corpus of sentences
    * "wikipedia_corpus/wiki_acronyms.txt", a list of possible acronyms
    * "wikipedia_corpus/wiki_capitalized.txt", a list of capitalized words
    * "wikipedia_corpus/wiki_sant.txt", a list of saints, convenient to retrieve first names
    * "wikipedia_corpus/wiki_vocab.txt", the vocabulary of the corpus
 
 Author:  Gweltaz Duval-Guennoc
  
"""


import os
import json
import re
from colorama import Fore
from libMySTT import split_line, filter_out, punctuation, capitalized, is_acronym, acronyms, get_correction, get_cleaned_sentence



LIMIT_VOCAB = False
VOCAB_SIZE = 10000


dumps_dir = os.path.join("wikipedia_corpus", "dumps")

KEMADUR_PATTERN = re.compile(r" (g|b|d|w|v|c'h){1}/[a-zñ']{3,}" ,re.IGNORECASE)



if __name__ == "__main__":
    articles = []

    for filename in os.listdir(dumps_dir):
        filename = os.path.join(dumps_dir, filename)
        with open(filename, 'r') as f:
            for line in f.readlines():
                articles.append(json.loads(line))
    
    keepers = set()
    acronym_words = set()
    capitalized_words = set()
    santou = set()
    num_outed = 0
    
    vocabulary = dict()

    for a in articles:
        for line in a["text"].split('\n'):
            for sentence in split_line(line):
                sentence = filter_out(sentence, punctuation + '*')
                words = sentence.split()
                
                # Filter out short sentences
                if len(words) <= 3:
                    continue
                
                # Filter out sentences with only single letters or short words (ex: "v i v i a n a v i v i a n a")
                if len(sentence)/len(words) < 2.0:
                    continue
                
                first_word = True
                sant = False
                for w in words:
                    if sant:
                        if w.lower() not in capitalized:
                            santou.add(w)
                        sant = False
                    elif w == "Sant":
                        sant = True
                    
                    if is_acronym(w) and w not in acronyms:
                        acronym_words.add(w)
                    elif not first_word and w.istitle() and w.isalpha() and w.lower() not in capitalized:
                        capitalized_words.add(w)
                    first_word = False
                
                correction, num_errors = get_correction(sentence)
                if num_errors == 0:
                    cleaned_sentence, _ = get_cleaned_sentence(sentence)
                    keepers.add(cleaned_sentence)
                    for w in cleaned_sentence.split():
                        if w in vocabulary:
                            vocabulary[w] += 1
                        else:
                            vocabulary[w] = 1
                elif num_errors == 1:
                    #if num_outed % 200 == 0:
                    #    print(correction)
                    num_outed += 1

    #print(f"{num_outed} discarded sentences with 1 error")
    
    
    if LIMIT_VOCAB:
        voc_list = sorted(vocabulary.items(), key=lambda x: x[1], reverse=True)
        voc_list = voc_list[:VOCAB_SIZE]
        vocabulary.clear()
        vocabulary.update(voc_list)
    
    kept = 0
    save_dir = "corpus"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    
    with open(os.path.join(save_dir, "wiki_corpus.txt"), 'w') as f:
        for sentence in keepers:
            # Keep sentences with common words only
            for w in sentence.split():
                if LIMIT_VOCAB and not w in vocabulary:
                    break
            else:   # Executed only if previous for loop exited normally
                if sentence.endswith(" ar") or sentence.endswith(" an"):
                    pass
                elif "ar kantved" in sentence or "an kantved" in sentence:
                    pass
                elif "er kantved" in sentence or "en kantved" in sentence:
                    pass
                else:
                    f.write(sentence + '\n')
                    kept += 1
    
    print(f"{kept} sentences kept")
    
    with open(os.path.join("wikipedia_corpus", "wiki_acronyms.txt"), 'w') as f:
        for a in sorted(acronym_words):
            f.write(a + '\n')
    with open(os.path.join("wikipedia_corpus", "wiki_capitalized.txt"), 'w') as f:
        for w in sorted(capitalized_words):
            f.write(w + '\n')
    with open(os.path.join("wikipedia_corpus", "wiki_sant.txt"), 'w') as f:
        for w in sorted(santou):
            f.write(w + '\n')
    with open(os.path.join("wikipedia_corpus", "wiki_vocab.txt"), 'w') as f:
        for w, n in sorted(vocabulary.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{w}\t{n}\n")
