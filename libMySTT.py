#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 26-01-2022
 
 Common functions for audio file playback and data parsing

"""


import os
import json
import re
from pydub import AudioSegment
#from pydub.playback import play
from pydub.utils import get_player_name
from tempfile import NamedTemporaryFile
import subprocess
import hunspell # https://www.systutorials.com/docs/linux/man/4-hunspell/
from colorama import Fore



ROOT = os.path.dirname(os.path.abspath(__file__))

HS_DIC_PATH = os.path.join(ROOT, os.path.join("hunspell-dictionary", "br_FR.dic"))
HS_AFF_PATH = os.path.join(ROOT, os.path.join("hunspell-dictionary", "br_FR.aff"))
HS_ADD_PATH= os.path.join(ROOT, os.path.join("hunspell-dictionary", "add.txt"))

CORRECTED_PATH = os.path.join(ROOT, "corrected.txt")
CAPITALIZED_PATH = os.path.join(ROOT, "capitalized.txt")
JOINED_PATH = os.path.join(ROOT, "joined.txt")

SPEAKER_ID_PATTERN = re.compile(r'{([-\'\w]+)}')


punctuation = (',', '.', ';', '?', '!', ':', '«', '»', '"', '”', '“', '(', ')', '…', '–')


def get_dict():
    hs = hunspell.HunSpell(HS_DIC_PATH, HS_AFF_PATH)
    with open(HS_ADD_PATH, 'r') as f:
        for w in f.readlines():
            hs.add(w.strip())
    return hs

hs_dict = get_dict()



def get_corrected():
    corrected = dict()
    corrected_sentence = dict()
    with open(CORRECTED_PATH, 'r') as f:
        for l in f.readlines():
            k, v = l.replace('\n', '').split('\t')
            if ' ' in k:
                corrected_sentence[k] = v
            else:
                corrected[k] = v
    return corrected, corrected_sentence

corrected, corrected_sentence = get_corrected()



def get_capitalized():
    """
        Returns a set of lower case names (that should be capitalized)
    """
    capitalized = set()
    with open(CAPITALIZED_PATH, 'r') as f:
        for l in f.readlines():
            capitalized.add(l.strip().split()[0].lower())
    return capitalized

capitalized = get_capitalized()



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



def get_corrected_sentence(sentence):
    """
        Return a string which is the corrected sentence
        and the number of spelling mistakes in sentence
    """
    #corrected = get_corrected()
    #capitalized = get_capitalized()
    sentence = sentence.strip().lower()
    if not sentence:
        return ''
    
    for mistake in corrected_sentence.keys():
        if mistake in sentence:
            sentence = sentence.replace(mistake, corrected_sentence[mistake])
    
    spell_error = False
    num_errors = 0
    tokens = []
    for token in tokenize(sentence):
        # Ignore black listed words
        if token.startswith('*'):
            tokens.append(token)
        
        elif token.isdigit():
            spell_error = True
            tokens.append(Fore.RED + token + Fore.RESET)
        
        elif token in corrected:
            token = corrected[token]
            
        # Check for hyphenated words
        
        elif token in capitalized:
            tokens.append(token.capitalize())
        
        elif not hs_dict.spell(token):
            spell_error = True
            tokens.append(Fore.RED + token + Fore.RESET)
        
        else:
            tokens.append(token)
        
        if spell_error:
            num_errors += 1
        
    return ' '.join(tokens), num_errors


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



def convert_to_wav(src, dst):
    """
        Convert 16kHz wav
        Validate filename
    """
    dst = dst.replace(' ', '_')
    dst = dst.replace("'", '')
    subprocess.call(['ffmpeg', '-v', 'panic',
                     '-i', src, '-acodec', 'pcm_s16le',
                     '-ac', '1', '-ar', '16000', dst])


def concatenate_audiofiles(file_list, out_filename, remove=True):
    if len(file_list) <= 1:
        return
    
    file_list_filename = "audiofiles.txt"
    with open(file_list_filename, 'w') as f:
        f.write('\n'.join([f"file '{wav}'" for wav in file_list]))
    
    subprocess.call(['ffmpeg', #'-v', 'panic',
                     '-f', 'concat',
                     '-safe', '0',
                     '-i', file_list_filename,
                     '-c', 'copy', out_filename])
    os.remove(file_list_filename)
    
    if remove:
        for fname in file_list:
            os.remove(fname)
