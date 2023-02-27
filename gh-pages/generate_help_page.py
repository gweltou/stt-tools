#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    Generates a markdown file and extracts audio segments where there's
    undecipherable words (marked with the symbol '{?}')
    
    Usage: ./generate_help_page.py rep
"""



import sys
import os
from libMySTT import list_files_with_extension, load_textfile, load_segments
from libMySTT import extract_metadata



if __name__ == "__main__":
    split_files = list_files_with_extension(".split", sys.argv[1])
    
    for split_file in split_files:
        wav_file = split_file.replace(".split", ".wav")
        wav_file_orig = split_file.replace(".split", "_orig.wav")
        txt_file = split_file.replace(".split", ".txt")

        if os.path.exists(wav_file_orig):
            wav_file = wav_file_orig

        utterances = load_textfile(txt_file)
        segments,_ = load_segments(split_file)
        
        if len(utterances) != len(segments):
            continue

        print(split_file)

        for i, (t, metadata) in enumerate(utterances):
            if "unknown_words" in metadata:
                print(t)

        print(wav_file)
        print(txt_file)
        print()
