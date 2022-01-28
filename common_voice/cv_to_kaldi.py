#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 2-01-2022
 
"""


import sys
import os
import subprocess
import json
import libMySTT


DATA_FOLDER = "br"
CLIPS_FOLDER = os.path.join(DATA_FOLDER, "clips")



def get_audiofile_length(filename):
    """
        Get audio file length in milliseconds
    """
    r = subprocess.check_output(['ffprobe', '-hide_banner', '-v', 'panic', '-show_streams', '-of', 'json', filename])
    r = json.loads(r)
    return float(r['streams'][0]['duration'])
    


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} FOLDER data_file.tsv")
        
    KALDI_FOLDER = sys.argv[1]
    data_file = sys.argv[2]
    data = []

    if os.path.exists(data_file):
        # client_id, path, sentence, up_votes, down_votes, age, gender, accent
        with open(data_file, 'r') as f:
            f.readline() # skip header
            l = f.readline().strip()
            while l:
                l = l.split('\t')
                l[0] = l[0][:16]    # Shorten speaker-id
                data.append(l[:8])
                l = f.readline().strip()

    speakers = list(set([l[0] for l in data]))
    speakers_gender = []

    if not os.path.exists(KALDI_FOLDER):
        os.mkdir(KALDI_FOLDER)

    cumul_time = 0
    for speaker in speakers:
        # for each speaker, create a folder an concatenate each of its utterances in one audio file
        
        utterances = []
        for utt in data:
            if utt[0] == speaker:
                utterances.append(utt)
        
        # Filter out gwenedeg from training data
        if utterances[0][7] == 'gwenedeg':
            print('gwenedeg')
            continue
        
        if utterances[0][6] in ('female', 'male'):
            speakers_gender.append((speaker, utterances[0][6][0]))
        
        speaker_folder = os.path.join(KALDI_FOLDER, speaker)
        if os.path.exists(speaker_folder):
            # Speaker as already been parsed, skip
            continue
        print(speaker, end='')
        
        os.mkdir(speaker_folder)
        audio_files = []
        text = []
        segments = []
        t = 0
        for utt in utterances:
            wav = utt[1].replace('.mp3', '.wav')
            src = os.path.join(CLIPS_FOLDER, utt[1])
            dst = os.path.join(speaker_folder, wav)
            # Convert to wav
            convert_to_wav(src, dst)
            #os.remove(src)
            nt = t + get_audiofile_length(dst)*1000
            segments.append((int(t), int(nt)))
            t = nt
            audio_files.append(f"file '{wav}'")
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
        # ffmpeg -f concat -i list.txt -c copy output.wav
        file_list_filename = os.path.join(speaker_folder, "list.txt")
        with open(file_list_filename, 'w') as f:
            f.write('\n'.join(audio_files))
        out_filename = os.path.join(speaker_folder, speaker+'.wav')
        subprocess.call(['ffmpeg', '-v', 'panic', '-f', 'concat', '-i', file_list_filename, '-c', 'copy', out_filename])
        
        # Remove old files
        for utt in utterances:
            os.remove(os.path.join(speaker_folder, utt[1].replace('.mp3', '.wav')))
        os.remove(file_list_filename)
        print('|')
    
    with open(os.path.join(KALDI_FOLDER, "spk2gender"), "w") as f:
        for sg in speakers_gender:
            f.write(f"{sg[0]}\t{sg[1]}\n") 
    
    minutes, seconds = divmod(round(cumul_time/1000), 60)
    print(f"total clip time kept : {minutes}'{seconds}''")
