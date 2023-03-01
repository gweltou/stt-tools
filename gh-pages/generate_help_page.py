#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    Generates a markdown file and extracts audio segments where there's
    undecipherable words (marked with the symbol '{?}')
    
    Usage: ./generate_help_page.py rep
"""



import sys
import os
from pydub import AudioSegment
sys.path.append("..")
from libMySTT import list_files_with_extension, load_textfile, load_segments
from libMySTT import extract_metadata, splitToEafFile
from shutil import copy


PAGES_DIR = "/home/gweltaz/Documents/STT/vosk_bzg/docs"
UTTS_DIR = os.path.join(PAGES_DIR, "utts")
FULL_DIR = os.path.join(PAGES_DIR, "full")

header = """
# Reiñ sikour da treuzskrivañ
 
Amañ e kavit tennadoù son diaes din da gompren e teuliadoù emaon o treuzskrivañ er mare-mañ.

M'ho peus c'hoant reiñ un taol sikour, kasit ur [postel din](mailto:gweltou@hotmail.com) gant ar frazenn klok ha difaziet, hervez ar pezh a gomprenoc'h.
Na zisoñjit ket da skrivañ niverenn ar frazenn (da skouer: `YBD/rann4, 192`).

Gallout a rit implij ar skritur a glot ar muiañ d'ar yezh komzet evel-just.
"""


if __name__ == "__main__":
    content = ""

    split_files = list_files_with_extension(".split", sys.argv[1])
    
    prev_id = ""

    for dir in (UTTS_DIR, FULL_DIR):
        if not os.path.exists(dir):
            os.mkdir(dir)

    for split_file in split_files:
        wav_file = split_file.replace(".split", ".wav")
        wav_file_orig = split_file.replace(".split", "_orig.wav")
        txt_file = split_file.replace(".split", ".txt")

        utterances = load_textfile(txt_file)
        segments,_ = load_segments(split_file)
        
        if len(utterances) != len(segments):
            print(split_file, "diff" , len(utterances), len(segments))
            continue
        
        path, filename = os.path.split(split_file)
        id =  filename.split(os.path.extsep)[0]
        id_full = os.path.split(path)[-1] + '/' + id
        if id_full != prev_id:
            print(id_full)
            prev_id = id_full
            
            splitToEafFile(split_file)

            dest = os.path.join(FULL_DIR, os.path.split(wav_file)[1])
            if not os.path.exists(dest):
                copy(wav_file, dest)
            
            dest = os.path.join(FULL_DIR, os.path.split(txt_file)[1])
            copy(txt_file, dest)

            eaf_file = split_file.replace(".split", ".eaf")
            dest = os.path.join(FULL_DIR, os.path.split(eaf_file)[1])
            os.rename(eaf_file, dest)

            content += f"## {id_full}\n\n"
            content += f"Restroù : [WAV](full/{os.path.split(wav_file)[1]}) \| "
            content += f"[TXT](full/{os.path.split(txt_file)[1]}) \| "
            content += f"[EAF](full/{os.path.split(eaf_file)[1]}) (ELAN)\n\n"


        
        if os.path.exists(wav_file_orig):
            wav_file = wav_file_orig
        song = AudioSegment.from_wav(wav_file)

        for i, (t, metadata) in enumerate(utterances):
            if "unknown_words" in metadata:
                line = f'{{% include embed-audio.html name="{i+1}" src="utts/{id}_seg{i+1:03}.mp3" %}}'
                print(line)
                content += line + '\n\n'
                # line = f"`{t}`"
                line = f"> {t}"
                print(line)
                content += line + '\n\n'
                # content += '---\n\n'

                seg = song[segments[i][0]:segments[i][1]]
                seg_name = os.path.join(UTTS_DIR, os.path.extsep.join((f"{id}_seg{i+1:03d}", 'mp3')))
                if not os.path.exists(seg_name):
                    seg.export(seg_name, format="mp3")
        print()

    with open(os.path.join(PAGES_DIR, "sikour.md"), 'w') as f:
        f.write(header + '\n\n')
        f.write(content)