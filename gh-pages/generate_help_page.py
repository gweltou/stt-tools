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
from libMySTT import extract_metadata


header = ""


if __name__ == "__main__":
    content = ""

    split_files = list_files_with_extension(".split", sys.argv[1])
    
    prev_id = ""

    if not os.path.exists("utts"):
        os.mkdir("utts")

    for split_file in split_files:
        wav_file = split_file.replace(".split", ".wav")
        wav_file_orig = split_file.replace(".split", "_orig.wav")
        txt_file = split_file.replace(".split", ".txt")

        if os.path.exists(wav_file_orig):
            wav_file = wav_file_orig

        utterances = load_textfile(txt_file)
        segments,_ = load_segments(split_file)
        
        if len(utterances) != len(segments):
            print(split_file, "diff" , len(utterances), len(segments))
            continue
        
        path, filename = os.path.split(split_file)
        id =  filename.split(os.path.extsep)[0]
        id_full = os.path.split(path)[-1] + '/' + id
        if id_full != prev_id:
            content += f"## {id_full}\n\n"
            print(id_full)
            prev_id = id_full
        
        song = AudioSegment.from_wav(wav_file)

        for i, (t, metadata) in enumerate(utterances):
            if "unknown_words" in metadata:
                line = f'{{% include embed-audio.html name="seg{i:03}" src="utts/{id}_seg{i:03}.mp3" %}}'
                content += line + '\n\n'
                print(line)
                line = f"`{t}`"
                content += line + '\n\n---\n\n'
                print(line)

                seg = song[segments[i][0]:segments[i][1]]
                seg_name = os.path.join("utts", os.path.extsep.join((id + f"_seg{i:03d}", 'mp3')))
                seg.export(seg_name, format="mp3")
        print()

    with open("sikour.md", 'w') as f:
        f.write(content)