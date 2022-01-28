#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 28-01-2022
 
"""


import sys
sys.path.append('..') # To import libMyTTS

import os
import re
from colorama import Fore
import libMySTT



def get_text_files(root):
    textfiles = []
    for dirpath, dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.txt'):
                textfiles.append(os.path.join(dirpath, name))
    return textfiles

    


if __name__ == "__main__":
    hs = libMyTTS.get_dict()
    corrected = libMyTTS.get_corrected()
    capitalised = libMyTTS.get_capitalised()
    
    textfiles = get_text_files(sys.argv[1])
    speaker_id_pattern = re.compile(r'{([-\w]+)}')
    
    num_errors = 0
    for file in textfiles:
        with open(file, 'r') as f:
            for line in f.readlines():
                # Remove speaker tag
                speaker_id_match = speaker_id_pattern.search(line)
                if speaker_id_match:
                    speaker_id = speaker_id_match[1]
                    start, end = speaker_id_match.span()
                    line = line[:start] + line[end:]
                    
                line = line.strip().lower()
                if line:
                    # Replace text according to "corrected" dictionary
                    for faulty in corrected.keys():
                        if faulty in line:
                            line = line.replace(faulty, corrected[faulty])
                    spell_error = False
                    tokens = []
                    first = True
                    for token in libMyTTS.tokenize(line):
                        # Ignore black listed words
                        if token.startswith('*'):
                            tokens.append(token)
                            continue
                        #if token in corrected:
                        #    tokens.append(corrected[token])
                        #    continue
                        # Check for hyphenated words
                        
                        if token in capitalised:
                            tokens.append(token.capitalize())
                            continue
                        if not hs.spell(token):
                            spell_error = True
                            tokens.append(Fore.RED + token + Fore.RESET)
                        else:
                            tokens.append(token)
                    if spell_error:
                        num_errors += 1
                        print(' '.join(tokens), f"[{line.strip()}]")
                        
    print(f"{num_errors} lines with spelling errors")
            
