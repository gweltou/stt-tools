#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from libMySTT import filter_out, punctuation, valid_chars, hs_dict, capitalized, is_acronym, acronyms


dumps_dir = os.path.join("wikipedia_corpus", "dumps")

#RE_PATTERN = re.compile(r'{([-\w]+):*([mf])*}')


def contains_numbers(s):
    for n in "0123456789":
        if n in s:
            return True
    return False


def split_line(s):
    if '. ' in s:
        i = s.index('. ')
        if len(s) > i+2 and s[i+2].isupper() and i>2 and s[i-2] != ' ':
            return [s[:i]] + split_line(s[i+2:])
    return [s]



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

for a in articles:
    for line in a["text"].split('\n'):
        for sentence in split_line(line):
            sentence = filter_out(sentence, punctuation)
            words = sentence.split()
            valid = True
            if len(words) <= 3:
                continue
            first_word = True
            sant = False
            for w in words:
                if sant:
                    santou.add(w)
                    sant = False
                elif w == "Sant":
                    sant = True
                
                if is_acronym(w) and w not in acronyms:
                    acronym_words.add(w)
                elif not first_word and w.istitle() and w.isalpha() and w not in capitalized:
                    capitalized_words.add(w)
                first_word = False
                if not hs_dict.spell(w) or contains_numbers(w):
                    valid = False
                    break
            if valid:
                keepers.add(sentence)

print(len(keepers))



if __name__ == "__main__":
    save_dir = "corpus"
    with open(os.path.join(save_dir, "wiki_corpus.txt"), 'w') as f:
        for sentence in keepers:
            if sentence.endswith(" ar") or sentence.endswith(" an"):
                pass
            elif "ar kantved" in sentence or "an kantved" in sentence:
                pass
            elif "er kantved" in sentence or "en kantved" in sentence:
                pass
            else:
                f.write(sentence + '\n')
    
    with open("wiki_acronyms.txt", 'w') as f:
        for a in sorted(acronym_words):
            f.write(a + '\n')
    with open("wiki_capitalized.txt", 'w') as f:
        for w in sorted(capitalized_words):
            f.write(w + '\n')
    with open("wiki_sant.txt", 'w') as f:
        for w in sorted(santou):
            f.write(w + '\n')
