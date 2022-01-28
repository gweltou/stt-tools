#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 28-01-2022
 
 Unpack SAE-Brezhoneg.zip (Skol An Emzav) and organize files

"""

import os
import re
import sys
sys.path.append("..")
from libMySTT import convert_to_wav, concatenate_audiofiles


stage = 5


if __name__ == "__main__":
    if len(sys.argv) > 1:
        stage = int(sys.argv[1])

    if stage <= 0:
        os.system("unzip SAE\ -\ Brezhoneg.zip")
        os.system("rm -rf __MACOSX/")
    
    if stage <= 1:
        print("==== Move audio files in subfolders ====")
        VOL_PATTERN = re.compile(r'SAE Brezhoneg - (b\d+)') 
        for fname in os.listdir(): 
            match = VOL_PATTERN.search(fname) 
            if match: 
                repname = match[1]
                if not os.path.exists(repname):
                    os.mkdir(repname)
                os.rename(fname, os.path.join(repname, fname))
        print("done")
    
    
    if stage <= 2:
        print("==== Move pdf files in subfolders ====")
        VOL_PATTERN = re.compile(r'#[Bb]rezhoneg(\d+)')     
        for fname in os.listdir(): 
            match = VOL_PATTERN.search(fname) 
            if match: 
                repname = 'b' + match[1]
                if not os.path.exists(repname):
                    os.mkdir(repname)
                os.rename(fname, os.path.join(repname, fname))
        print("done")
    
    
    if stage <= 3:
        print("==== Extract text from pdf files ====")
        for fname in os.listdir():
            if os.path.isdir(fname) and fname != '.':
                for fname2 in os.listdir(fname):
                    if fname2.lower().endswith(".pdf"):
                        pdf_filename = os.path.abspath(os.path.join(fname, fname2))
                        text_filename = os.path.abspath(os.path.join(fname, fname+".txt"))
                        os.system(f"../../extract_text.py {pdf_filename} > {text_filename}")
                        print('.', end='')
        print("done")
    
    
    if stage <= 4:
        print("==== Converting mp3 files to wav ====")
        for fname in os.listdir():
            if os.path.isdir(fname):
                mp3_files = [os.path.join(fname, f) for f in os.listdir(fname) if f.lower().endswith('.mp3')]
                for mp3_filename in mp3_files:
                    wav_filename = mp3_filename.replace('.mp3', '.wav')
                    convert_to_wav(mp3_filename, wav_filename)
                    os.remove(mp3_filename)
                    print('.', end='')
        print("done")
    
    
    if stage <= 5:
        print("==== Concatenating wav files ====")
        for fname in os.listdir():
            if os.path.isdir(fname):
                audiofiles = []
                for fname2 in os.listdir(fname):
                    if fname2.endswith(".wav"):
                        audiofiles.append(os.path.join(fname, fname2))
                audiofiles = [os.path.abspath(f) for f in sorted(audiofiles)]
                out_filename = os.path.abspath(os.path.join(fname, fname+'.wav'))
                concatenate_audiofiles(audiofiles, out_filename)
                print(out_filename, len(audiofiles))
                print('.', end='')
        print("done")
