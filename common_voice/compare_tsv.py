#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author:        Gweltaz Duval-Guennoc
 
    Analyse (or compare) tsv files
 
"""


import sys
import os
import tarfile
from math import floor, ceil
from pydub import AudioSegment

sys.path.append("..")
from libMySTT import get_audiofile_length



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
        dur_m = 0.0
        dur_f = 0.0
        dur_u = 0.0
        
        # client_id, path, sentence, up_votes, down_votes, age, gender, accent
        with open(filename, 'r') as f:
            f.readline() # skip header
            l = f.readline().strip()
            while l:
                l = l.split('\t')
                speaker_id = l[0][:16]    # Shorten speaker-id
                duration = get_audiofile_length( os.path.join(clip_dir, l[1]) )
                if l[6] == "male":
                    if not speaker_id in speakers:
                        num_m += 1
                    dur_m += duration
                elif l[6] == "female":
                    if not speaker_id in speakers:
                        num_f += 1
                    dur_f += duration
                else:
                    if not speaker_id in speakers:
                        num_u += 1
                    dur_u += duration
                speakers.add(speaker_id)
                sentences.add(l[2])
                l = f.readline().strip()
        print("Number of speakers:", len(speakers))
        print("Number of sentences:", len(sentences))
        total_length = dur_m + dur_f + dur_u
        minutes, seconds = divmod(round(total_length), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Audio length: {hours} h {minutes}'{seconds}''")
        print(f"Male speakers: {num_m} ({round(num_m/len(speakers), 2)}%)")
        minutes, seconds = divmod(round(dur_m), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Male audio length: {hours} h {minutes}'{seconds}'' ({round(dur_m/total_length, 2)}%)")
        print(f"Female speakers: {num_f} ({round(num_f/len(speakers), 2)}%)")
        minutes, seconds = divmod(round(dur_f), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Female audio length: {hours} h {minutes}'{seconds}'' ({round(dur_f/total_length, 2)}%)")
        print(f"Unknown gender: {num_u} ({round(num_u/total_length, 2)}%)")
        minutes, seconds = divmod(round(dur_u), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Unk gender audio length: {hours} h {minutes}'{seconds}'' ({round(dur_u/total_length, 2)}%)")
        print()
        return speakers, sentences
    else:
        print("File not found:", filename)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} data_file.tsv [data_file2.tsv...]")
        sys.exit(1)
    
    clip_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "clips")
    
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
        speakers, sentences = parse_tsv(file)
        speaker_list.append(speakers)
        sentence_list.append(sentences)
        
    
    print("Common speakers:", len(speaker_list[0].intersection(*speaker_list[1:])))
    print("Common sentences:", len(sentence_list[0].intersection(*sentence_list[1:])))
    
