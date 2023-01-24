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


dumps_dirs = [
    # os.path.join("wikipedia_corpus", "dumps"),
    "corpus_skrid"
]

KEMMADUR_PATTERN = re.compile(r" (g|b|d|w|v|c'h){1}/[a-zñ']{3,}", re.IGNORECASE)



# def parse_file(filename):




if __name__ == "__main__":
    articles = []

    filenames = []

    for d in dumps_dirs:
        for filename in os.listdir(d):
            filenames.append(os.path.join(d, filename))
    
    for filename in filenames:
        if "wiki" in filename:
            with open(filename, 'r') as f:
                for line in f.readlines():
                    articles.append(json.loads(line))
        else:
            with open(filename, 'r') as f:
                a = dict()
                # for line in f.readlines():
                a["text"] = f.read()
                articles.append(a)
    
    keepers = set()
    punct_keepers = set()
    acronym_words = set()
    capitalized_words = set()
    santou = set()
    num_outed = 0
    
    vocabulary = dict()

    for a in articles:
        for line in a["text"].split('\n'):
            line = line.strip()
            if line.startswith("#"):
                print(line)
                continue
            for sentence in split_line(line):
                #sentence = filter_out(sentence, punctuation + '*')
                words = sentence.split()
                
                # Filter out short sentences
                if len(words) <= 3:
                    continue
                
                # Filter out sentences with only single letters or short words (ex: excludes "v i v i a n a v i v i a n a")
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
                
                sub_sentences = [get_cleaned_sentence(sub)[0] for sub in sentence.split(',')]
                # nopunct_sentence, _ = get_cleaned_sentence(sentence)
                sub_keepers = []
                for s in sub_sentences:
                    correction, num_errors = get_correction(s)
                    if num_errors == 0:
                        sub_keepers.append(s)
                        for w in s.split():
                            if w in vocabulary:
                                vocabulary[w] += 1
                            else:
                                vocabulary[w] = 1
                    elif num_errors == 1:
                        print(correction)
                        #if num_outed % 200 == 0:
                        #    print(correction)
                        num_outed += 1
                punct_keepers.add(', '.join(sub_keepers))
                keepers.add(get_cleaned_sentence(' '.join(sub_keepers)))

    #print(f"{num_outed} discarded sentences with 1 error")
    
    
    if LIMIT_VOCAB:
        voc_list = sorted(vocabulary.items(), key=lambda x: x[1], reverse=True)
        voc_list = voc_list[:VOCAB_SIZE]
        vocabulary.clear()
        vocabulary.update(voc_list)
    
    kept = 0
    save_dir = "generated_corpus"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    
    with open(os.path.join(save_dir, "corpus.txt"), 'w') as f:
        for sentence in punct_keepers:
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
    
    save_dir = os.path.join(save_dir, "extracted")
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    with open(os.path.join(save_dir, "acronyms.txt"), 'w') as f:
        for a in sorted(acronym_words):
            f.write(a + '\n')
    with open(os.path.join(save_dir, "capitalized.txt"), 'w') as f:
        for w in sorted(capitalized_words):
            f.write(w + '\n')
    with open(os.path.join(save_dir, "sant.txt"), 'w') as f:
        for w in sorted(santou):
            f.write(w + '\n')
    with open(os.path.join(save_dir, "vocab.txt"), 'w') as f:
        for w, n in sorted(vocabulary.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{w}\t{n}\n")
