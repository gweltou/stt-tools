#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 27-01-2022
 
 TODO:
    Add hunspell support
"""


import sys
import os
import re
from math import floor, ceil
from pydub import AudioSegment
import librosa
from libMySTT import *




def play_segment_text(idx, song, segments, text, speed):
    if idx < len(text):
        corrected, _ = get_corrected_sentence(text[idx])
        print(f"{{{speakers[idx]}}} {corrected}")
        print(f"[{text[idx]}]")
    play_segment(idx, song, segments, speed)



def save_segments(segments, filename):
    with open(filename, 'w') as f:
        for i, s in enumerate(segments):
            start = int(s[0])
            stop =  int(s[1])
            f.write(f"{start} {stop}\n")
    print('segment file saved')



def load_textfile(filename):
    text = []
    speakers = []
    current_speaker = "unknown"
    with open(filename, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            if l and not l.startswith('#'):
                speaker_id_match = SPEAKER_ID_PATTERN.search(l)
                if speaker_id_match:
                    current_speaker = speaker_id_match[1]
                    start, end = speaker_id_match.span()
                    l = l[:start] + l[end:]
                l = l.strip()
                if l :
                    text.append(l)
                    speakers.append(current_speaker)
    return text, speakers



if __name__ == "__main__":
    PLAYER = get_player_name()
    
    rep, filename = os.path.split(os.path.abspath(sys.argv[1]))
    recording_id = filename.split(os.path.extsep)[0]
    recording_id = recording_id.replace('&', '_')
    print(recording_id)
    
    wav_filename = os.path.join(rep, os.path.extsep.join((recording_id, 'wav')))
    split_filename = os.path.join(rep, os.path.extsep.join((recording_id, 'split')))
    text_filename = os.path.join(rep, os.path.extsep.join((recording_id, 'txt')))
    
    # Create text file if it doesn't exist
    if not os.path.exists(text_filename):
        open(text_filename, 'a').close()
    text = []
    speakers = []
    text, speakers = load_textfile(text_filename)
    textfile_mtime = os.path.getmtime(text_filename)
    
    segments = []
    if os.path.exists(split_filename):
        print("split file exists")
        segments = load_segments(split_filename)
    else:
        fileinfo = get_audiofile_info(sys.argv[1])
        #for s in ["codec_name", "channels", "sample_rate", "bits_per_sample"]:
        #    print(f"{s}: {fileinfo[s]}")
        
        # Convert to 16kHz mono wav if needed
        if fileinfo["channels"] != 1 or fileinfo["sample_rate"] != "16000" or \
           fileinfo["bits_per_sample"] != 16:
            print(f"converting {sys.argv[1]}...")
            convert_to_wav(sys.argv[1], wav_filename);
            print("conversion done")
        
        print("spliting wave file")
        y, sr = librosa.load(wav_filename)
        
        # We need to forward a bit after stop
        # Librosa.effects.split returns start and stop in samples number
        segments = [(floor(1000*start/sr), ceil(1000*(stop+8000)/sr)) \
                     for start, stop in librosa.effects.split(y, frame_length=8000, top_db=39)]
        save_segments(segments, split_filename)
    
    
    print(f"{len(segments)} segments")
    
    
    song = AudioSegment.from_wav(wav_filename)
    
    running = True
    idx = 0
    speed = 1
    while running:
        x = input(f"{idx+1}> ")
        
        # Reload text file if it's been modified
        mtime = os.path.getmtime(text_filename)
        if mtime > textfile_mtime:
            text, speakers = load_textfile(text_filename)
        
        if x.isnumeric():
            idx = (int(x)-1) % len(segments)
            play_segment_text(idx, song, segments, text, speed)
        elif x == '.' or x == 'r':
            play_segment_text(max(0, idx), song, segments, text, speed)
        elif x == '+' or x == 'n':
            idx = (idx+1) % len(segments)
            play_segment_text(idx, song, segments, text, speed)
        elif x == '-' or x == 'p':
            idx -= 1
            play_segment_text(idx, song, segments, text, speed)
        elif x == '*':
            speed *= 1.15
            print("speed=", speed)
        elif x == '/':
            speed *= 0.9
            print("speed=", speed)
        elif x == 'd':  # Delete segment (by commenting it out)
            del segments[idx]
            idx = max(0, idx-1)
        elif x == 'j' and idx > 0:  # Join this segment with previous segment
            start = segments[idx-1][0]
            end = segments[idx][1]
            del segments[idx]
            idx = max(0, idx-1)
            segments[idx] = (start, end)
            print("segments joined")
        elif x == 's':  # Save split data to disk
            save_segments(segments, split_filename) 
        elif x == 'h':  # Help
            print(". or 'r'\tPlay current segment")
            print("+ or 'n'\tGo to next segment and play")
            print("- or 'p'\tGo back to previous segment and play")
            print("*\tSpeed playback up")
            print("*\tSlow playback down")
            print("'d'\tDelete current segment")
            print("'j'\tJoin current segment with previous one")
            print("'q'\tQuit")
        elif x == 'q':
            running = False
