#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 2-01-2022
 
"""


import sys
import os
import re
from colorama import Fore
import hunspell # https://www.systutorials.com/docs/linux/man/4-hunspell/
from libMyTTS import *



def get_text_files(root):
    textfiles = []
    for dirpath, dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.txt'):
                textfiles.append(os.path.join(dirpath, name))
    return textfiles

    


if __name__ == "__main__":

    hs = hunspell.HunSpell('br_FR.dic', 'br_FR.aff')
    
    textfiles = get_text_files(sys.argv[1])
    speaker_id_pattern = re.compile(r'{([-\w]+)}')
    
    for file in textfiles:
        with open(file, 'r') as f:
            for line in f.readlines():
                speaker_id_match = speaker_id_pattern.search(line)
                if speaker_id_match:
                    speaker_id = speaker_id_match[1]
                    start, end = speaker_id_match.span()
                    line = line[:start] + line[end:]
                if line.strip():
                    print(line.strip())
                    tokens = tokenize(line)
                    tokens =  [Fore.RED + t + Fore.RESET if not hs.spell(t) and not hs.spell(t.capitalize()) else t for t in tokens]
                    print("  -->", ' '.join(tokens))
            
