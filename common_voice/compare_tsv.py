#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author:        Gweltaz Duval-Guennoc
 
    Unpack Mozilla's Common Voice dataset and prepare data
    to be used for Kaldi framework
 
"""


import sys
import os
import tarfile
from math import floor, ceil
from pydub import AudioSegment

sys.path.append("..")
import libMySTT



spk2gender_file = "spk2gender"
blacklisted_speakers_file = "blacklisted_speakers.txt"


def parse_tsv(filename):
    print(filename)
    if os.path.exists(filename):
        speakers = set()
        sentences = set()
        num_m = 0
        num_f = 0
        num_u = 0
        
        # client_id, path, sentence, up_votes, down_votes, age, gender, accent
        with open(filename, 'r') as f:
            f.readline() # skip header
            l = f.readline().strip()
            while l:
                l = l.split('\t')
                speaker_id = l[0][:16]    # Shorten speaker-id
                if not speaker_id in speakers:
                    speakers.add(speaker_id)
                    if l[6] == "male":
                        num_m += 1
                    elif l[6] == "female":
                        num_f += 1
                    else:
                        num_u += 1
                sentences.add(l[2])
                l = f.readline().strip()
        return speakers, sentences, num_m, num_f, num_u
    else:
        print("File not found:", filename)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} data_file.tsv [data_file2.tsv...]")
        sys.exit(1)
    
    speakers_gender = dict()
    if os.path.exists(spk2gender_file):
        with open(spk2gender_file, 'r') as f:
            for l in f.readlines():
                speaker, gender = l.split()
                speakers_gender[speaker] = gender
    else:
        print("spk2gender file not found")
    
    blacklisted_speakers = []
    if os.path.exists(blacklisted_speakers_file):
        with open(blacklisted_speakers_file, 'r') as f:
            blacklisted_speakers = [l.split()[0] for l in f.readlines()]
    else:
        print("Blacklist speaker file not found")
    
    speaker_list = []
    sentence_list = []
    files = sys.argv[1:]    
    for file in files:
        speakers, sentences, nm, nf, nu = parse_tsv(file)
        speaker_list.append(speakers)
        sentence_list.append(sentences)
        print("Number of speakers:", len(speakers))
        print("Number of sentences:", len(sentences))
        print("Male speakers:", nm)
        print("Female speakers:", nf)
        print("Unknown gender:", nu)
        print()
    
    print("Common speakers:", len(speaker_list[0].intersection(*speaker_list[1:])))
    print("Common sentences:", len(sentence_list[0].intersection(*sentence_list[1:])))
    
