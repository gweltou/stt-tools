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
 
    Usage: python3 build_lm_corpus.py 

    Author:  Gweltaz Duval-Guennoc
  
"""


import os
import json
import re
import argparse
from colorama import Fore
from libMySTT import split_line, filter_out, punctuation, capitalized, is_acronym, acronyms, get_correction, get_cleaned_sentence



LIMIT_VOCAB = False
VOCAB_SIZE = 10000

dumps_dirs = [
    os.path.join("corpus_wikipedia", "dumps"),
    # "corpus_skrid"
]

KEMMADUR_PATTERN = re.compile(r" (g|b|d|w|v|c'h){1}/[a-zñ']{3,}", re.IGNORECASE)



# def parse_file(filename):




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a clean corpus text from dumps (wikiedia) or other")
    parser.add_argument("source", help="Source of raw corpus data (directory of wikipedia dumps or text files)", metavar="DIR_OR_FILE", nargs='+')
    parser.add_argument("-o", "--output", help="Output directory", default="generated")
    parser.add_argument("-t", "--min-tokens", help="Minimum number of valid tokens per sentence", type=int, default=4)
    parser.add_argument("--rem-punct", help="Remove punctuation", action="store_true")
    args = parser.parse_args()
    print(args)


    filenames = []
    for d in args.source:
        if os.path.isfile(d) and d.endswith(".txt"):
            filenames.append(d)
        elif os.path.isdir(d):
            for filename in os.listdir(d):
                # if filename.endswith(".txt"):
                filenames.append(os.path.join(d, filename))
    
    articles = []
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
    keepers_nopunct = set()
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
                words = sentence.split()
                
                # Filter out short sentences
                if len(sentence) < 10:
                    continue

                # Filter out sentences with only single letters or short words (ex: "v i v i a n a v i v i a n a")
                if len(sentence)/len(words) < 2.0:
                    continue
                
                first_word = True
                sant = False
                for w in words:
                    w = filter_out(w, punctuation)
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
                
                sub_sentences = sentence.split(', ')
                sub_keepers = []
                for sub in sub_sentences:
                    if not sub.strip(): continue

                    correction, num_errors = get_correction(sub)

                    if num_errors == 0 and len(correction) > 1:
                        sub_keepers.append(get_cleaned_sentence(sub, rm_bl=True, keep_punct=args.rem_punct)[0])
                    elif num_errors == 1:
                        # if num_outed % 200 == 0:
                        #    print(correction)
                        num_outed += 1
                keepers.add(', '.join(sub_keepers))
                sentence_nopunct = ' '.join(filter_out(' '.join(sub_keepers), punctuation).split()) # Remove multi white-spaces
                keepers_nopunct.add(sentence_nopunct)
                for w in sentence_nopunct.split():
                    if w in vocabulary:
                        vocabulary[w] += 1
                    else:
                        vocabulary[w] = 1

    #print(f"{num_outed} discarded sentences with 1 error")
    
    
    if LIMIT_VOCAB:
        voc_list = sorted(vocabulary.items(), key=lambda x: x[1], reverse=True)
        voc_list = voc_list[:VOCAB_SIZE]
        vocabulary.clear()
        vocabulary.update(voc_list)
    
    kept = 0

    OUTPUT_DIR = args.output
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    with open(os.path.join(OUTPUT_DIR, "corpus.txt"), 'w') as f:
        for sentence in keepers_nopunct if args.rem_punct else keepers:
            words = sentence.split()
            
            # Filter out short sentences
            if len(words) < args.min_tokens:
                continue

            # Keep sentences with common words only
            for w in words:
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
    
    OUTPUT_DIR = os.path.join(OUTPUT_DIR, "extracted")
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    with open(os.path.join(OUTPUT_DIR, "acronyms.txt"), 'w') as f:
        for a in sorted(acronym_words):
            f.write(a + '\n')
    with open(os.path.join(OUTPUT_DIR, "capitalized.txt"), 'w') as f:
        for w in sorted(capitalized_words):
            f.write(w + '\n')
    with open(os.path.join(OUTPUT_DIR, "sant.txt"), 'w') as f:
        for w in sorted(santou):
            f.write(w + '\n')
    with open(os.path.join(OUTPUT_DIR, "vocab.txt"), 'w') as f:
        for w, n in sorted(vocabulary.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{w}\t{n}\n")
