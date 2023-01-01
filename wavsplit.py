#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    File : wavesplit.py
    Author: Gweltaz Duval-Guennoc 
    
    Create a split file (time segments) from an audio file
    Convert audio file to correct format (wav mono 16kHz) if needed
    UI to listen and align audio segments with sentences in text file
    
    Dependencies:
        * pydub
        * simpleaudio
        * pyrubberband
"""


import sys
import os
import argparse
import re
from math import floor, ceil
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pydub.playback import _play_with_simpleaudio
from pyrubberband import time_stretch
#import librosa
from libMySTT import *


RESIZE_PATTERN = re.compile(r"([s|e])([-|\+])(\d+)")
SPLIT_PATTERN = re.compile(r"c([0-9\.]+)")


play_process = None



def play_segment_text(idx, song, segments, text, speed):
    global play_process
    if play_process and play_process.is_playing():
        play_process.stop()
    
    if idx < len(text):
        correction, _ = get_correction(text[idx])
        start = round(segments[idx][0] / 1000.0, 1)
        stop = round(segments[idx][1] / 1000.0, 1)
        print(f"[{start}:{stop}] {{{speakers[idx]}}} {correction}")
    #print(f"[{text[idx]}]")
    seg = song[segments[idx][0]:segments[idx][1]]
    if speed != 1.0:
        y = np.array(seg.get_array_of_samples())
        y = time_stretch(y, seg.frame_rate, speed)
        y = np.int16(y * 2**15)
        seg = AudioSegment(y.tobytes(), frame_rate=seg.frame_rate, sample_width=2, channels=1)
    play_process = _play_with_simpleaudio(seg)
    #play_segment(idx, song, segments, speed)



def save_segments(segments, header, filename):
    with open(filename, 'w') as f:
        if header:
            f.write(header + '\n')
        for _, s in enumerate(segments):
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
                # Extract speaker id and other metadata
                metadata_match = METADATA_PATTERN.finditer(l)
                speaker_id_match = SPEAKER_ID_PATTERN.search(l)
                if speaker_id_match:
                    current_speaker = speaker_id_match[1]
                for match in metadata_match:
                    start, end = match.span()
                    l = l[:start] + l[end:]
                
                l = l.strip()
                if l :
                    text.append(l)
                    speakers.append(current_speaker)
    return text, speakers



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'Wavesplit',
                    description = 'Audio file converter, splitter and text alignment')
    parser.add_argument('filename')
    parser.add_argument('-o', '--overwrite', action='store_true', help="Overwrite split file (if present)")
    parser.add_argument('-t', '--thresh', type=float, default=-62, metavar="DB", help="Silence intensity threshold (in decibels)")      # option that takes a value
    parser.add_argument('-d', '--dur', type=int, default=400, metavar="MS", help="Silence minimum duration (in millisecs)")
    args = parser.parse_args()
    print(args)


    PLAYER = get_player_name()
    
    rep, filename = os.path.split(os.path.abspath(args.filename))
    # Removing special characters from filename
    recording_id = filename.split(os.path.extsep)[0]
    recording_id = recording_id.replace('&', '_')
    recording_id = recording_id.replace(' ', '_')
    recording_id = recording_id.replace("'", '')
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
    
    fileinfo = get_audiofile_info(sys.argv[1])
    # Converting sound file to 16kHz mono wav if needed
    if fileinfo["channels"] != 1 or fileinfo["sample_rate"] != "16000" or fileinfo["bits_per_sample"] != 16:
        src = sys.argv[1]
        if os.path.samefile(src, wav_filename):
            rep, filename = os.path.split(src)
            basename, ext = os.path.splitext(filename)
            new_name = basename + "_orig" + ext
            new_src = os.path.join(rep, new_name)
            print(f"WARNING: renaming {filename} to {new_name}")
            os.rename(src, new_src)
            src = new_src
        ret = convert_to_wav(src, wav_filename)
        if ret == -1:
            print("Could not convert audio file")
            sys.exit(1)
        else:
            print("Conversion done")
    
    song = AudioSegment.from_wav(wav_filename)
    
    segments = []
    header = ""
    if os.path.exists(split_filename) and not args.overwrite:
        print("split file exists")
        segments, header = load_segments(split_filename)
    else:
        print("spliting wave file")
        #y, sr = librosa.load(wav_filename)
        #print("file loaded")
        #silence_min_len = 400
        # We need to forward a bit after stop
        # Librosa.effects.split returns start and stop in samples number
        #segments = [(floor(1000*start/sr), ceil(1000*(stop+8000)/sr)) \
        #             for start, stop in librosa.effects.split(y, frame_length=8000, top_db=39)]
        
        # Using pydub instead
        segments = detect_nonsilent(song, min_silence_len=args.dur, silence_thresh=args.thresh)
        
        # Including silences in segments
        if len(segments) >= 2:
            segments[0] = (segments[0][0], segments[0][1] + args.dur)
            segments[-1] = (segments[-1][0] - args.dur, segments[-1][1])
            for i in range(1, len(segments)-1):
                segments[i] = (segments[i][0] - args.dur, segments[i][1] + args.dur)
        
        header = f"# -t {args.thresh} -d {args.dur}"
        save_segments(segments, header, split_filename)
    
    
    short_utterances = []
    for i, (start, stop) in enumerate(segments):
        l = round((stop-start)/1000.0, 1)
        if l < 1.3:
            short_utterances.append(i+1)
    if short_utterances:
        print("Short utterances:", short_utterances)
    
    
    running = True
    idx = 0
    speed = 1
    modified = False
    segments_undo = []
    while running:
        length = round((segments[idx][1] - segments[idx][0]) / 1000.0, 1)
        x = input(f"{idx+1}/{len(segments)} {length}s> ")
        resize_match = RESIZE_PATTERN.match(x)
        split_match = SPLIT_PATTERN.match(x)
        
        # Reload text file if it's been modified
        mtime = os.path.getmtime(text_filename)
        if mtime > textfile_mtime:
            text, speakers = load_textfile(text_filename)
        
        if resize_match:
            segments_undo = segments[:]
            pos = resize_match.groups()[0]
            start, stop = segments[idx]
            delay = int(resize_match.groups()[1] + resize_match.groups()[2])
            if pos == 's':
                segments[idx] = (start + delay, stop)
            elif pos == 'e':
                segments[idx] = (start, stop + delay)
            modified = True
        elif split_match:
            segments_undo = segments[:]
            pc = float(split_match.groups()[0])
            start, stop = segments[idx]
            cut = start + (stop-start) * pc/100.0
            segments = segments[:idx] + [(start, ceil(cut)), (floor(cut), stop)] + segments[idx+1:]
            modified = True
            print(f"Segment split at {pc}% of its length")
        elif x == 'cc': # Automatic split
            segments_undo = segments[:]
            seg = song[segments[idx][0]:segments[idx][1]]
            print(header)
            #subsegments = detect_nonsilent(seg, min_silence_len=args.dur, silence_thresh=args.thresh)
        elif x.isnumeric():
            idx = (int(x)-1) % len(segments)
            play_segment_text(idx, song, segments, text, speed)
        elif x == '.' or x == 'r':
            play_segment_text(max(0, idx), song, segments, text, speed)
        elif x == '+' or x == 'n':
            idx = (idx+1) % len(segments)
            play_segment_text(idx, song, segments, text, speed)
        elif x.startswith('+') and x[1:].isdigit():
            n = int(x[1:])
            idx = (idx+n) % len(segments)
            play_segment_text(idx, song, segments, text, speed)
        elif x == '-' or x == 'p':
            idx = (idx-1) % len(segments)
            play_segment_text(idx, song, segments, text, speed)
        elif x.startswith('-') and x[1:].isdigit():
            n = int(x[1:])
            idx = (idx-n) % len(segments)
            play_segment_text(idx, song, segments, text, speed)
        elif x == '*':
            speed *= 1.15
            print("speed=", speed)
        elif x == '/':
            speed *= 0.9
            print("speed=", speed)
        elif x == 'd':  # Delete segment
            segments_undo = segments[:]
            if play_process and play_process.is_playing():
                play_process.stop()
            del segments[idx]
            idx = max(0, idx-1)
            modified = True
            print("segment deleted")
        elif x == 'j' and idx > 0:  # Join this segment with previous segment
            segments_undo = segments[:]
            start = segments[idx-1][0]
            end = segments[idx][1]
            del segments[idx]
            idx = max(0, idx-1)
            segments[idx] = (start, end)
            modified = True
            print("segments joined")
        elif x == 'a':  # Acronym extraction
            for acr in extract_acronyms(text[idx]):
                add_pron = ""
                if acr in acronyms:
                    while not add_pron in ('a', 'k'):
                        add_pron = input(f"{acr} already known [{acronyms[acr]}], keep/add ? ('k', 'a') ").strip().lower()
                    if add_pron == 'k': continue
                    
                phon = prompt_acronym_phon(acr, song, segments, idx)
                if phon:
                    if add_pron == 'a':
                        acronyms[acr].append(phon)
                    else: acronyms[acr] = [phon]
                    with open(ACRONYM_PATH, 'a') as f:
                            f.write(f"{acr} {phon}\n")
        elif x == 't':  # Transcribe with vosk
            seg = song[segments[idx][0]:segments[idx][1]]
            print(transcribe_segment(seg))
        elif x == 'z':  # Undo
            print("Undone")
            segments = segments_undo
            modified = True
        elif x == 's':  # Save split data to disk
            save_segments(segments, header, split_filename) 
            modified = False
        elif x == 'h' or x == '?':  # Help
            print("'h' or '?'\tShow this help")
            print(". or 'r'\tPlay current segment or stop playback")
            print("+ or 'n'\tGo to next segment and play")
            print("- or 'p'\tGo back to previous segment and play")
            print("-[n] or +[n]\tGo backward/forward n positions")
            print("*\tSpeed playback up")
            print("/\tSlow playback down")
            print("'d'\tDelete current segment")
            print("'j'\tJoin current segment with previous one")
            print("[s/e][+/-]millisecs\tedit segment (ex: e+500, add 500ms to end)")
            print("'c[PC]' split current segment at PC percent of its length (ex: c66.6)")
            print("'z'\tUndo previous segment modification")
            print("'a'\tRegister acronym")
            print("'t'\tAutomatic transcription")
            print("'q'\tQuit")
        elif x == 'q':
            if modified:
                r = input("Save before quitting (y|n) ? ")
                if r == 'y': save_segments(segments, split_filename) 
            running = False
