#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Score every utterance of every data item in a giver folder
"""


import sys
import argparse
import os
from pydub import AudioSegment
from libMySTT import list_files_with_extension, load_segments, load_textfile, get_segment, transcribe_segment, get_cleaned_sentence
from jiwer import wer, cer



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score every utterance of every data item in a giver folder")
    parser.add_argument("data_folder", metavar='FOLDER', help="Folder containing data files")
    args = parser.parse_args()

    print(args.data_folder)
    split_files = list_files_with_extension('.split', args.data_folder)
    for split_file in sorted(split_files):
        basename, _ = os.path.splitext(split_file)
        wav_file = basename + os.path.extsep + "wav"
        text_file = basename + os.path.extsep + "txt"
        segments, _ = load_segments(split_file)
        utterances = load_textfile(text_file)
        song = AudioSegment.from_file(wav_file)
        _, basename = os.path.split(basename)
        print("==== " + basename + " ====")
        for i in range(len(segments)):
            sentence, _ = get_cleaned_sentence(utterances[i][0])
            transcription = transcribe_segment(get_segment(i, song, segments))
            score_wer = wer(sentence, transcription)
            score_cer = cer(sentence, transcription)
            #if score_cer >= 0.2 or score_wer > 0.4:
            if score_cer >= 0.4 and score_wer > 0.6:
                print(i+1, "\twer:", round(score_wer, 2), "cer:", round(score_cer, 2))
                print("GT", sentence)
                print("->", transcription)
                print(flush=False)
