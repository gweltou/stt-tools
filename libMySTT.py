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
ACRONYM_PATH = os.path.join(ROOT, "acronym_lexicon.txt")

SPEAKER_ID_PATTERN = re.compile(r'{([-\'\w]+)}')


punctuation = (',', '.', ';', '?', '!', ':', '«', '»', '"', '”', '“', '(', ')', '…', '–')


def get_hunspell_dict():
    hs = hunspell.HunSpell(HS_DIC_PATH, HS_AFF_PATH)
    with open(HS_ADD_PATH, 'r') as f:
        for w in f.readlines():
            hs.add(w.strip())
    for w in ['euh', 'eba', 'kwa', 'beñ', 'boñ', 'oh']:
        hs.add(w)
    return hs

hs_dict = get_hunspell_dict()



def get_corrected_dict():
    corrected = dict()
    corrected_sentence = dict()
    with open(CORRECTED_PATH, 'r') as f:
        for l in f.readlines():
            k, v = l.replace('\n', '').split('\t')
            k = k.lower()
            if ' ' in k:
                corrected_sentence[k] = v
            else:
                corrected[k] = v
    return corrected, corrected_sentence

corrected, corrected_sentence = get_corrected_dict()



def get_capitalized_dict():
    """
        Returns a set of lower case names (that should be capitalized)
    """
    capitalized = set()
    with open(CAPITALIZED_PATH, 'r') as f:
        for l in f.readlines():
            capitalized.add(l.strip().split('\t')[0].lower())
    return capitalized

capitalized = get_capitalized_dict()



def get_acronyms_dict():
    """
        Acronym are stored in UPPER CASE in dictionary
    """
    acronyms = set()
    if os.path.exists(ACRONYM_PATH):
        with open(ACRONYM_PATH) as f:
            for l in f.readlines():
                if l.startswith('#') or not l: continue
                acr, *pron = l.split()
                acronyms.add(acr)
    else:
        print("Acronym dictionary not found... creating file")
        open(ACRONYM_PATH, 'a').close()
    return acronyms

acronyms = get_acronyms_dict()



def filter_out(text, symbols):
    new_text = ""
    for l in text:
        if not l in symbols: new_text += l
    return ' '.join(new_text.split()) # Prevent multi spaces



def is_acronym(word):
    if len(word) < 2:
        return False
    for letter in word:
        if not letter.isdecimal() and letter.islower():
            return False
    return True



def tokenize(sentence):
    sentence = filter_out(sentence, punctuation)
    sentence = sentence.replace('‘', "'")
    sentence = sentence.replace('’', "'")
    sentence = sentence.replace('ʼ', "'")
    sentence = sentence.replace('-', ' ')   # Split words like "sav-heol"
    sentence = sentence.replace('/', ' ')
    tokens = []
    for t in sentence.split():
        if t.startswith("'"):
            tokens.append(t[1:])
        elif t.endswith("'"):
            tokens.append(t[:-1])
        else:
            tokens.append(t) 
    return tokens



def get_cleaned_sentence(sentence):
    """
        Return a cleaned sentence, proper to put in text files or corpus
               and a quality score (ratio of black-listed words)
    """
    lowered_sentence = sentence.lower()
    for mistake in corrected_sentence.keys():
        if mistake in sentence or mistake in lowered_sentence:
            sentence = sentence.replace(mistake, corrected_sentence[mistake])
    
    tokens = []
    num_blacklisted = 0
    for token in tokenize(sentence):
        lowered_token = token.lower()
        # Ignore black listed words
        if token.startswith('*'):
            tokens.append(token[1:])
            num_blacklisted += 1
        elif lowered_token in corrected:
            tokens.append(corrected[lowered_token])
        elif lowered_token in capitalized:
            tokens.append(token.capitalize())
        elif is_acronym(token):
            tokens.append(token)
            if not token in acronyms:
                num_blacklisted += 1
        else:
            tokens.append(lowered_token)
    return ' '.join(tokens), float(num_blacklisted)/len(tokens)



def get_correction(sentence):
    """
        Return a string which is a colored correction of the sentence
        and the number of spelling mistakes in sentence
    """
    
    sentence = sentence.strip()
    if not sentence:
        return ''
    
    lowered_sentence = sentence.lower()
    for mistake in corrected_sentence.keys():
        if mistake in sentence or mistake in lowered_sentence:
            sentence = sentence.replace(mistake, corrected_sentence[mistake])
    
    num_errors = 0
    tokens = []
    for token in tokenize(sentence):
        spell_error = False
        lowered_token = token.lower()
        # Ignore black listed words
        if token.startswith('*'):
            tokens.append(Fore.YELLOW + token + Fore.RESET)
        elif token.isdigit():
            spell_error = True
            tokens.append(Fore.RED + token + Fore.RESET)
        elif lowered_token in corrected:
            token = corrected[lowered_token]
            
        # Check for hyphenated words
        elif is_acronym(token):
            if token in acronyms:
                tokens.append(Fore.GREEN + token + Fore.RESET)
            else:
                tokens.append(Fore.RED + token + Fore.RESET)
                spell_error = True
        elif lowered_token in capitalized:
            tokens.append(token.capitalize())
        elif not hs_dict.spell(token):
            spell_error = True
            tokens.append(Fore.RED + token + Fore.RESET)
        else:
            tokens.append(lowered_token)
        
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
