#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Author:        Gweltaz Duval-Guennoc
 Last modified: 26-01-2022
 
 TODO:
    Detect and prompt for capitalized names
    Detect and prompt hyphenated words
"""


import sys
import os
import numpy as np
import re
from math import floor, ceil
from libMyTTS import *


acronym_filename = "acronym_lexicon.txt"
capitalised_filename = "capitalised.txt"
joined_filname = "joined.txt"


speakers_gender = {
    'nolwenn_korbell'   : 'f',
    'maryvonne_berthou' : 'f',
    'maina_audran'  : 'f',
    'claude_an_du'  : 'f',
    'roger_an_du'   : 'm',
    'yann_bijer'    : 'm',
    'bob_simon'     : 'm',
    'jean-mari_ollivier': 'm',
}
    


w2f = {
    'a'     :   'A',
    'añ'    :   'AN',
    'an'    :   'AN N',
    'b'     :   'B',
    'd'     :   'D',
    'ch'    :   'CH',       # CHomm
    "c'h"   :   'X',
    #'.c.'   :   'S E',      # al lizherenn 'C'
    'd'     :   'D',
    'e'     :   'E',        # spErEd
    'ê'     :   'E',        # gÊr
    'ei'    :   'EY',       # kEIn      # could replace with (EH I) maybe ?
    'eu'    :   'EU',       # lEUn
    'eü'    :   'E U',      # EÜrus
    'er.'   :   'EH R',     # hantER
    'em'    :   'EH M',     # lEMm
    'eñ'    :   'EN',       # chEÑch
    'enn'   :   'EH N',     # lENN
    "ec'h"  :   'EH X',     # nec'h
    'f'     :   'F',
    'g'     :   'G',
    'gn'    :   'GN',       # miGNon
    'h'     :   'H',
    'ha.'   :   'A',
    'hag.'  :   'A G',
    'i'     :   'I',
    'iñ'    :   'I N',      # bIÑs
    'iñ.'   :   'I',        # debrIÑ
    'j'     :   'J',        # BeaJiñ
    'k'     :   'K',
    'l'     :   'L',
    'lh'    :   'LH',
    'll'    :   'L',
    'm'     :   'M',
    'mm'    :   'M',
    'n'     :   'N',
    'nn'    :   'N',
    'o'     :   'O',        # nOr
    'on'    :   'ON N',     # dON
    'ont.'  :   'ON N',     # mONt
    'oñ'    :   'ON',       # sOÑjal
    'ou'    :   'OU',       # dOUr
    'où.'   :   'OU',       # goulOÙ
    'or'    :   'OH R',     # dORn      ! dor, goudoriñ
    'orr'   :   'O R',      # gORRe
    'p'     :   'P',
    'r'     :   'R',
    's'     :   'S',
    't'     :   'T',
    'u'     :   'U',        # tUd
    'uñ'    :   'UN',       # pUÑs
    'un.'   :   'OE N',     # UN dra
    'ul.'   :   'OE L',     # UL labous
    'ur.'   :   'OE R',     # UR vag
    'v'     :   'V',
    'v.'    :   'O',        # beV
    'w'     :   'W',
    'ya'    :   'IA',       # YAouank
    'ye'    :   'IE',       # YEzh
    'yo'    :   'IO',       # YOd
    'you'   :   'IOU',      # YOUc'hal
    'z'     :   'Z',
    'zh'    :   'Z',
}

acr2f = {
    'A' :   'A',
    'B' :   'B E',
    'C' :   'S E',
    'D' :   'D E',
    'E' :   'EU',
    'F' :   'EH F',
    'G' :   'J E',
    'H' :   'A CH',
    'I' :   'I',
    'J' :   'J I',
    'K' :   'K A',
    'L' :   'EH L',
    'M' :   'EH M',
    'N' :   'EH N',
    'O' :   'O',
    'P' :   'P E',
    'Q' :   'K U',
    'R' :   'EH R',
    'S' :   'EH S',
    'T' :   'T E',
    'U' :   'U',
    'V' :   'V E',
    'W' :   'OU E',
    'X' :   'I K S',
    
    'Z' :   'Z EH D',
}


phonemes = set()
for val in list(w2f.values()) + list(acr2f.values()):
    for tok in val.split():
        phonemes.add(tok)



def word2phonetic(word):
    head = 0
    phonemes = []
    word = '.' + word.strip().replace('-', '.') + '.'
    while head < len(word):
        for i in (4, 3, 2, 1):
            token = word[head:head+i].lower()
            if token in w2f:
                phonemes.append(w2f[token])
                head += i-1
                break
        head += 1
    
    if len(phonemes) == 0:
        print("ERROR: word2phonetic", word)
    return phonemes


def is_acronym(word):
    if len(word) < 2:
        return False
    for letter in word:
        if letter.islower():
            return False
    return True


def filter_out(text, symbols):
    new_text = ""
    for l in text:
        if not l in symbols: new_text += l
    return ' '.join(new_text.split()) # Prevent multi spaces


def prompt_acronym_phon(w, wav_filename, i):
    guess = ' '.join([acr2f[l] for l in w])
    print(f"Phonetic proposition for '{w}' : {guess}")
    while True:
        answer = input("Press 'y' to validate, 'l' to listen or write different prononciation: ").strip().upper()
        if not answer:
            continue
        if answer == 'Y':
            return guess
        if answer == 'L':
            split_filename = wav_filename[:-3] + 'split'
            segments = load_segments(split_filename)
            song = AudioSegment.from_wav(wav_filename)
            play_segment(i, song, segments, 1.5)
            continue
        valid = True
        for phoneme in answer.split():
            if phoneme not in phonemes:
                print("Error : phoneme not in", ' '.join(phonemes))
                valid = False
        if valid :
            return answer
        


def parse_data(rep):
    split_filename = ""
    for filename in os.listdir(rep):
        if filename.lower().endswith('.split'):
            split_filename = os.path.join(rep, filename)
            break
    assert split_filename, f"ERROR: no split file found in {rep}"
    
    recording_id = os.path.split(split_filename)[1].split(os.path.extsep)[0]
    print(recording_id)
    text_filename = os.path.abspath(os.path.join(rep, recording_id + '.txt'))
    assert os.path.exists(text_filename), f"ERROR: no text file found for {recording_id}"
    wav_filename = os.path.abspath(os.path.join(rep, recording_id + '.wav'))
    assert os.path.exists(wav_filename), f"ERROR: no wave file found for {recording_id}"
    
    text = []
    speaker_ids = []
    speaker_id_pattern = re.compile(r'{([-\w]+)}')
    speaker_id = "unnamed"
    with open(text_filename, 'r') as f:
        n_line = 0
        for l in f.readlines():
            if l.startswith('#'):
                continue
            # Extract speaker id
            speaker_id_match = speaker_id_pattern.search(l)
            if speaker_id_match:
                speaker_id = speaker_id_match[1]
                start, end = speaker_id_match.span()
                l = l[:start] + l[end:]
            cleaned_line = filter_out(l, punctuation)
            cleaned_line = cleaned_line.replace('‘', "'")
            cleaned_line = cleaned_line.replace('’', "'")
            cleaned_line = cleaned_line.replace('ʼ', "'")
            cleaned_line = cleaned_line.replace('-', ' ')   # Split words like "sav-heol"
            cleaned_line = cleaned_line.replace('/', ' ')
            cleaned_line = cleaned_line.strip()
            if cleaned_line:
                speaker_ids.append(speaker_id)
                text.append(cleaned_line.replace('*', ''))
                for w in cleaned_line.split():
                    # Remove black-listed words (beggining with '*') from lexicon
                    if not w.startswith('*'):
                        if is_acronym(w):
                            if w in acronyms:
                                acronyms[w][1].append(n_line)
                            else:
                                phon = prompt_acronym_phon(w, wav_filename, n_line)
                                acronyms[w] = [phon, [n_line]]
                        else: words.add(w)
                n_line += 1
     
    segments_delim = []
    with open(split_filename, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            segments_delim.append(l.split())
    
    assert len(text) == len(segments_delim), \
        "number of utterances in text file doesn't match number of segments in split file"

    segments_data = []
    text_data = []
    utt2spk_data = []
    for i, s in enumerate(segments_delim):
        start = int(s[0]) / 1000
        stop = int(s[1]) / 1000
        utterance_id = f"{speaker_ids[i]}-{recording_id}-{floor(100*start):0>7}_{ceil(100*stop):0>7}"
        text_data.append((utterance_id, text[i]))
        segments_data.append(f"{utterance_id}\t{recording_id}\t{floor(start*100)/100}\t{ceil(stop*100)/100}\n")
        utt2spk_data.append(f"{utterance_id}\t{speaker_ids[i]}\n")
    
    return recording_id, wav_filename, text_data, segments_data, utt2spk_data



if __name__ == "__main__":
    rep = ""
    wavscp = []
    text = []
    segments = []
    utt2spk = []
    words = set()
    
    # Parse acronym lexicon
    acronyms = dict()
    if os.path.exists(acronym_filename):
        with open(acronym_filename) as f:
            for l in f.readlines():
                if l.startswith('#') or not l: continue
                acr, *pron = l.split()
                # Each acronym in file is supposed to be unique
                acronyms[acr] = [' '.join(pron), []]  # First field is phonetic prononciation, second is used to list locations in text file
    else:
        print("No acronym lexicon found...")
    
    if os.path.isdir(sys.argv[1]):
        rep = sys.argv[1]
        for filename in os.listdir(rep):
            filename = os.path.join(rep, filename)
            if os.path.isdir(filename):
                recording_id, wav_filename, text_data, segments_data, utt2spk_data = parse_data(filename)
                wavscp.append((recording_id, os.path.abspath(wav_filename)))
                text.extend(text_data)
                segments.extend(segments_data)
                utt2spk.extend(utt2spk_data)
            elif filename.endswith('.split'):   # Folder with a single data item
                recording_id, wav_filename, text_data, segments_data, utt2spk_data = parse_data(rep)
                wavscp.append((recording_id, os.path.abspath(wav_filename)))
                text.extend(text_data)
                segments.extend(segments_data)
                utt2spk.extend(utt2spk_data)
                break
                
    else:
        print("Argument should be a directory")
        sys.exit(1)
    
    print("acronyms :", ' '.join(acronyms))
    with open(acronym_filename, 'w') as f:
        for acr in sorted(acronyms.keys()):
            f.write(f"{acr}\t{acronyms[acr][0]}\n")
            
    
    if not os.path.exists('data'):
        os.mkdir('data')
    
    save_dir = os.path.join('data', os.path.split(os.path.normpath(rep))[1])
    #save_dir = os.path.abspath(save_dir)
    
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    
    # Build 'text' file
    fname = os.path.join(save_dir, 'text')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        for l in text:
            f.write(f"{l[0]}\t{l[1]}\n")
    
    # Build 'segments' file
    fname = os.path.join(save_dir, 'segments')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        f.writelines(segments)
    
    # Build 'utt2spk'
    fname = os.path.join(save_dir, 'utt2spk')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        f.writelines(utt2spk)
    
    # Build 'spk2gender'
    fname = os.path.join(save_dir, 'spk2gender')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        for speaker_id, speaker_gender in sorted(speakers_gender.items()):
            f.write(f"{speaker_id}\t{speaker_gender}\n")
    
    # Build 'wav.scp'
    fname = os.path.join(save_dir, 'wav.scp')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        for rec_id, wav_filename in wavscp:
            f.write(f"{rec_id}\t{wav_filename}\n")
    
    
    if not os.path.exists(os.path.join('data', 'local')):
        os.mkdir(os.path.join('data', 'local'))
    
    dict_dir = os.path.join('data', 'local', 'dict_nosp')
    if not os.path.exists(dict_dir):
        os.mkdir(dict_dir)
    else:
        if os.path.exists(os.path.join(dict_dir, 'lexicon.txt')):
            print('lexicon.txt file already exists')
            with open(os.path.join(dict_dir, 'lexicon.txt')) as f:
                for l in f.readlines()[3:]:
                    words.add(l.strip().split()[0])
    
    
    # Lexicon.txt
    print('building file data/local/dict_nosp/lexicon.txt')
    with open('data/local/dict_nosp/lexicon.txt', 'w') as f:
        f.write(f"!SIL SIL\n<SPOKEN_NOISE> SPN\n<UNK> SPN\n")
        for w in sorted(words):
            f.write(f"{w} {' '.join(word2phonetic(w))}\n")
    
    
    # nonsilence_phones.txt
    phones = []
    for p in w2f.values():
        phones.extend(p.split())
    phones = sorted(set(phones))
    print('building file data/local/dict_nosp/nonsilence_phones.txt')
    with open('data/local/dict_nosp/nonsilence_phones.txt', 'w') as f:
        for p in phones:
            f.write(f'{p}\n')
    
    
    # silence_phones.txt
    print('building file data/local/dict_nosp/silence_phones.txt')
    with open('data/local/dict_nosp/silence_phones.txt', 'w') as f:
        f.write(f'SIL\noov\nSPN\n')
    
    
    # optional_silence.txt
    print('building file data/local/dict_nosp/optional_silence.txt')
    with open('data/local/dict_nosp/optional_silence.txt', 'w') as f:
        f.write('SIL\n')
    
    
    # Copy text corpus
    with open('data/local/corpus.txt', 'a') as f:
        for l in text:
            f.write(f"{l[1]}\n")
    
