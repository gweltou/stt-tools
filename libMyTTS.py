#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 26-01-2022
 
 Common functions for audio file playback and data parsing

"""


import os
import json
from pydub import AudioSegment
#from pydub.playback import play
from pydub.utils import get_player_name
from tempfile import NamedTemporaryFile
import subprocess
import hunspell # https://www.systutorials.com/docs/linux/man/4-hunspell/


ROOT = os.path.dirname(os.path.abspath(__file__))

HS_DIC_PATH = os.path.join(ROOT, os.path.join("hunspell-dictionary", "br_FR.dic"))
HS_AFF_PATH = os.path.join(ROOT, os.path.join("hunspell-dictionary", "br_FR.aff"))
HS_ADD_PATH= os.path.join(ROOT, os.path.join("hunspell-dictionary", "add.txt"))

CORRECTED_PATH = os.path.join(ROOT, "corrected.txt")
CAPITALIZED_PATH = os.path.join(ROOT, "capitalised.txt")
JOINED_PATH = os.path.join(ROOT, "joined.txt")


punctuation = (',', '.', ';', '?', '!', ':', '«', '»', '"', '”', '“', '(', ')', '…', '–')



def get_dict():
    hs = hunspell.HunSpell(HS_DIC_PATH, HS_AFF_PATH)
    with open(HS_ADD_PATH, 'r') as f:
        for w in f.readlines():
            hs.add(w.strip())
    return hs



def get_corrected():
    corrected = dict()
    with open(CORRECTED_PATH, 'r') as f:
        for l in f.readlines():
            k, v = l.strip().split('\t')
            corrected[k] = v
    return corrected



def get_capitalised():
    capitalised = set()
    with open(CAPITALIZED_PATH, 'r') as f:
        for l in f.readlines():
            capitalised.add(l.strip().split()[0].lower())
    return capitalised



def filter_out(text, symbols):
    new_text = ""
    for l in text:
        if not l in symbols: new_text += l
    return ' '.join(new_text.split()) # Prevent multi spaces



def tokenize(line):
    line = filter_out(line.lower(), punctuation)
    line = line.replace('‘', "'")
    line = line.replace('’', "'")
    line = line.replace('ʼ', "'")
    line = line.replace('-', ' ')   # Split words like "sav-heol"
    line = line.replace('/', ' ')
    tokens = []
    for t in line.split():
        if t.startswith("'"):
            tokens.append(t[1:])
        elif t.endswith("'"):
            tokens.append(t[:-1])
        else:
            tokens.append(t) 
    return tokens



def load_segments(filename):
    segments = []
    with open(filename, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            if l:
                t = l.split()
                start = int(t[0])
                stop = int(t[1])
                segments.append((start, stop))
    return segments



def play_segment(i, song, segments, speed):
    start = int(segments[i][0])
    stop = int(segments[i][1])
    utterance = song[start: stop]
    play_with_ffplay(utterance, speed)



def get_audiofile_info(filename):
    r = subprocess.check_output(['ffprobe', '-hide_banner', '-v', 'panic', '-show_streams', '-of', 'json', filename])
    r = json.loads(r)
    return r['streams'][0]


    
def play_with_ffplay(seg, speed=1.0):
    with NamedTemporaryFile("w+b", suffix=".wav") as f:
        seg.export(f.name, "wav")
        player = get_player_name()
        subprocess.call(
            [player, "-nodisp", "-autoexit", "-loglevel", "quiet", "-af", f"atempo={speed}", f.name]
        )

