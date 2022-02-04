#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 2-01-2022
 
"""


import sys
import os
import subprocess
#import json
import tarfile

sys.path.append("..")
from libMySTT import convert_to_wav, concatenate_audiofiles, get_audiofile_length



# Modify those to add/remove training and test data
TRAINING_DATA = ["dev.tsv", "train.tsv"]
TEST_DATA = ["test.tsv"]



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} FOLDER data_file.tsv")
    
    tar_file = [f for f in os.listdir() if f.endswith(".tar.gz")][0]
    with tarfile.open(tar_file, 'r') as tar:
        data_folder = tar.getnames()[0]
    
    if not os.path.exists(data_folder):
        # Untar archive
        tar.extractall()
        #os.system("tar xvf cv-corpus-*-br.tar.gz")
    
    
    #DST_FOLDER = sys.argv[1]
    DST_FOLDER = "train"
    
    #data_files = sys.argv[2]
    #data_files = TRAINING_DATA + TEST_DATA
    clips_folder = os.path.join(data_folder, "clips")
    speakers_gender = set()
    parsed_audiofiles = set()   # To make sure every utterance is used only once in datasets
    
    if not os.path.exists(DST_FOLDER):
        os.mkdir(DST_FOLDER)
    
    for data_file in TRAINING_DATA:
        data = []
        cumul_time = 0
        
        data_file = os.path.join(data_folder, data_file)
        print(data_file)
        if os.path.exists(data_file):
            # client_id, path, sentence, up_votes, down_votes, age, gender, accent
            with open(data_file, 'r') as f:
                f.readline() # skip header
                l = f.readline().strip()
                while l:
                    l = l.split('\t')
                    l[0] = l[0][:16]    # Shorten speaker-id
                    data.append(l[:8])  # Keep first 8 fields only
                    l = f.readline().strip()
        else:
            print("File not found:", data_file)
        
        speakers = set([l[0] for l in data])
        print(f"{len(speakers)} speakers found...")
        for speaker in speakers:
            # for each speaker, create a folder an concatenate each of its utterances in one audio file
            print(speaker, end=' ')
            
            utterances = [utt for utt in data if utt[0] == speaker]
            
            # Filter out gwenedeg from training data
            if utterances[0][7] == 'gwenedeg (skipping)':
                print('gwenedeg')
                continue
            
            if utterances[0][6] in ('female', 'male'):
                print(f'[{utterances[0][6][0]}]', end=' ')
                speakers_gender.add((speaker, utterances[0][6][0]))
            
            speaker_folder = os.path.join(DST_FOLDER, speaker)
            if not os.path.exists(speaker_folder):
                os.mkdir(speaker_folder)
            else:
                # Speaker has already been parsed
                print('|')
                continue
            
            audiofiles = []
            text = []
            segments = []
            t = 0
            for utt in utterances:
                if utt[1] in parsed_audiofiles:
                    print("already seen:", utt)
                else:
                    parsed_audiofiles.add(utt[1])
                
                wav = utt[1].replace('.mp3', '.wav')
                src = os.path.join(clips_folder, utt[1])
                dst = os.path.join(speaker_folder, wav)
                # Convert to wav
                if not os.path.exists(dst):
                    convert_to_wav(src, dst)
                #os.remove(src)
                nt = t + get_audiofile_length(dst)*1000
                segments.append((int(t), int(nt)))
                t = nt
                audiofiles.append(dst)
                text.append(utt[2])
                print('.', end='')
            cumul_time += t
            
            # Text file
            with open(os.path.join(speaker_folder, speaker+".txt"), "w") as f:
                f.write(f"{{{speaker}}}\n")
                f.write('\n'.join(text))
            
            # Split file
            with open(os.path.join(speaker_folder, speaker+".split"), "w") as f:
                for delim in segments:
                    f.write(f"{delim[0]} {delim[1]}\n")
            
            # Concatenate audio files of the same speaker
            out_filename = os.path.join(speaker_folder, speaker+'.wav')
            if not os.path.exists(out_filename):
                concatenate_audiofiles(audiofiles, out_filename)
            
            print('|')
    
        minutes, seconds = divmod(round(cumul_time/1000), 60)
        print(f"total clip time kept : {minutes}'{seconds}''")
    
    with open("spk2gender", "w") as f:
        for sg in speakers_gender:
            f.write(f"{sg[0]}\t{sg[1]}\n") 
