#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File:       rename_speakers.py
    
    Add source filename to speaker name if the speaker name is a default speaker name (paotrXXX or plachXXX)
    
    Author:     Gweltaz Duval-Guennoc
 
"""


import sys
import os
import re
sys.path.append("..")
import libMySTT



def get_text_files(root):
    textfiles = []
    for dirpath, dirs, files in os.walk(root):
        for name in files:
            if name in ["notes.txt"]:
                continue
            if name.endswith('.txt'):
                textfiles.append(os.path.join(dirpath, name))
    return textfiles
    


if __name__ == "__main__":
    textfiles = get_text_files(os.getcwd())
    
    for file in textfiles:
        split_filename = file.replace('.txt', '.split')
        if not os.path.exists(split_filename):
            continue
        
        text = []
        with open(file, 'r') as f:
            print(file)
            basename = os.path.basename(file).split(os.path.extsep)[0]
            for line in f.readlines():
                speaker_id_match = libMySTT.SPEAKER_ID_PATTERN.search(line)
                if speaker_id_match:
                    speaker_id = speaker_id_match[1]
                    if speaker_id.startswith("paotr") or speaker_id.startswith("plach"):
                        line = line.replace(speaker_id_match[0], f"{{{basename}_{speaker_id}}}")
                    
                text.append(line)
        
        with open(file, 'w') as f:
            f.writelines(text)
