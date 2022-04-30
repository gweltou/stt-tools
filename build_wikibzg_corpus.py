#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from libMySTT import filter_out, punctuation, valid_chars, hs_dict

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

for a in articles:
    for line in a["text"].split('\n'):
        for sentence in split_line(line):
            sentence = filter_out(sentence, punctuation)
            words = sentence.split()
            valid = True
            if len(words) <= 3:
                continue
            for w in words:
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
