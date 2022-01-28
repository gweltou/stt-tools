#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 28-01-2022
 
"""


import sys
#sys.path.append('..') # To import libMyTTS

import os
import re
import libMySTT



def get_text_files(root):
    textfiles = []
    for dirpath, dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.txt'):
                textfiles.append(os.path.join(dirpath, name))
    return textfiles

    


if __name__ == "__main__":
    #hs = libMyTTS.hs_dict
    
    textfiles = get_text_files(sys.argv[1])
    
    num_errors = 0
    for file in textfiles:
        with open(file, 'r') as f:
            num_line = 0
            for line in f.readlines():
                num_line += 1
                # Remove speaker tag
                speaker_id_match = libMySTT.SPEAKER_ID_PATTERN.search(line)
                if speaker_id_match:
                    speaker_id = speaker_id_match[1]
                    start, end = speaker_id_match.span()
                    line = line[:start] + line[end:]
                
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                    
                corrected, errors = libMySTT.get_corrected_sentence(line)
                num_errors += errors
                if errors:
                    print(f"[{num_line}] {corrected} [{line.strip()}]")
                        
    print(f"{num_errors} spelling mistakes")
            
