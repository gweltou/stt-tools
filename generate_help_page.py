#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    Generates a markdown file and extracts audio segments where there's
    undecipherable words (marked with the symbol '{?}')
    
    Usage: ./generate_help_page.py rep
"""



import sys
from libMySTT import list_files_with_extension



if __name__ == "__main__":
    split_files = list_files_with_extension(".split", sys.argv[1])
    
    for split_file in split_files:
        wav_file = split_file.replace(".split", ".wav")
        txt_file = split_file.replace(".split", ".txt")
        
        print(split_file)
        print(wav_file)
        print(txt_file)
        print()
