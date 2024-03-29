#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Build necessary kaldi files to train an ASR model from audio and textual data
 All generated files are written in `data` directory

 Usage :
    
 
 Author:  Gweltaz Duval-Guennoc
"""


import sys
import os
import argparse
import numpy as np
import re
from math import floor, ceil
from libMySTT import extract_metadata, get_cleaned_sentence, is_acronym, load_segments, word2phonetic, split_line, list_files_with_extension
from libMySTT import capitalized, acronyms, verbal_tics, phonemes, LEXICON_ADD_PATH, load_textfile


SAVE_DIR = "data"
LM_SENTENCE_MIN_WORDS = 3
UTTERANCES_MIN_LENGTH = 3 # exclude utterances shorter than this length (in seconds)

spk2gender_files = ["spk2gender.txt", "corpus_common_voice/spk2gender"]



def parse_dataset(file_or_dir):
    if file_or_dir.endswith(".split"):   # Single data item
        return parse_data_file(file_or_dir)
    elif os.path.isdir(file_or_dir):
        data = {
            "path": file_or_dir,
            "wavscp": [],       # Wave filenames
            "utt2spk": [],      # Utterance to speakers
            "segments": [],     # Time segments
            "text": [],         # Utterances text
            "speakers": set(),  # Speakers names
            "lexicon": set(),   # Word dictionary
            "corpus": set(),    # Sentences for LM corpus
            "audio_length": {'m': 0, 'f': 0},    # Audio length for each gender
            "subdir_audiolen": {}   # Size (total audio length) for every sub-folders
            }
        
        for filename in os.listdir(file_or_dir):
            if os.path.isdir(os.path.join(file_or_dir, filename)) or filename.endswith(".split"):
                data_item = parse_dataset(os.path.join(file_or_dir, filename))
                data["wavscp"].extend(data_item["wavscp"])
                data["utt2spk"].extend(data_item["utt2spk"])
                data["segments"].extend(data_item["segments"])
                data["text"].extend(data_item["text"])
                data["speakers"].update(data_item["speakers"])
                data["lexicon"].update(data_item["lexicon"])
                data["corpus"].update(data_item["corpus"])
                data["audio_length"]['m'] += data_item["audio_length"]['m']
                data["audio_length"]['f'] += data_item["audio_length"]['f']
                data["subdir_audiolen"][filename] = data_item["audio_length"]['m'] + data_item["audio_length"]['f']
        
        return data
    else:
        print("File argument must be a split file or a directory")
        return
    


def parse_data_file(split_filename):
    if ' ' in split_filename:
        print("ERROR: whitespaces in path", split_filename)
        sys.exit(1)
    
    recording_id = os.path.basename(split_filename).split(os.path.extsep)[0]
    print(f" * {split_filename[:-6]}")
    text_filename = split_filename.replace('.split', '.txt')
    assert os.path.exists(text_filename), f"ERROR: no text file found for {recording_id}"
    wav_filename = split_filename.replace('.split', '.wav')
    assert os.path.exists(wav_filename), f"ERROR: no wave file found for {recording_id}"
    
    substitute_corpus_filename = split_filename.replace('.split', '.cor')
    replace_corpus = os.path.exists(substitute_corpus_filename)
    
    data = {
        "wavscp": [],       # Wave filenames
        "utt2spk": [],      # Utterance to speakers
        "segments": [],     # Time segments
        "text": [],         # Utterances text
        "speakers": set(),  # Speakers names
        "lexicon": set(),   # Word dictionary
        "corpus": set(),    # Sentences for LM corpus
        "audio_length": {'m': 0, 'f': 0},    # Audio length for each gender
        }
    
    ## PARSE TEXT FILE
    speaker_ids = []
    speaker_id = "unknown"
    sentences = []

    for sentence, metadata in load_textfile(text_filename):
        add_to_corpus = True
        if "parser" in metadata:
            if "no-lm" in metadata["parser"]:
                add_to_corpus = False
            elif "add-lm" in metadata["parser"]:
                add_to_corpus = True
            
        if "speaker" in metadata:
            speaker_id = metadata["speaker"]
            data["speakers"].add(speaker_id)
        
        if "gender" in metadata and speaker_id != "unknown":
            if speaker_id not in speakers_gender:
                # speakers_gender is a global variable
                speakers_gender[speaker_id] = metadata["gender"]
            
        cleaned_sentence, _ = get_cleaned_sentence(sentence)     
        if cleaned_sentence:
            speaker_ids.append(speaker_id)
            sentences.append(cleaned_sentence.replace('*', ''))
            
            # Add words to lexicon
            for word in cleaned_sentence.split():
                # Remove black-listed words (beggining with '*')
                if word.startswith('*'):
                    pass
                elif word in verbal_tics:
                    pass
                elif is_acronym(word):
                    pass
                elif word.lower() in capitalized:
                    pass
                else: data["lexicon"].add(word)
        
        # Add sentence to language model corpus
        if add_to_corpus and not replace_corpus:
            for sub in split_line(sentence):
                cleaned_sub, bl_score = get_cleaned_sentence(sub, rm_bl=True, rm_verbal_ticks=True)
                if not cleaned_sub:
                    continue
                # Ignore if to many black-listed words in sentence
                if bl_score > 0.2:
                    print("rejected", sub)
                    continue
                # Ignore if sentence is too short
                if cleaned_sub.count(' ') < LM_SENTENCE_MIN_WORDS - 1:
                    # print("corpus skip:", cleaned_sentence)
                    continue
                data["corpus"].add(cleaned_sub)
    
    if replace_corpus:
        with open(substitute_corpus_filename, 'r') as f:
            for sentence in f.readlines():
                sentence = sentence.strip()
                if not sentence or sentence.startswith('#'):
                    continue
                sentence, _ = extract_metadata(sentence)
                sentence, _ = get_cleaned_sentence(sentence, rm_bl=True)
                data["corpus"].add(sentence)
    

    ## PARSE SPLIT FILE
    segments, _ = load_segments(split_filename)
    assert len(sentences) == len(segments), \
        f"number of utterances in text file ({len(data['text'])}) doesn't match number of segments in split file ({len(segments)})"

    for i, s in enumerate(segments):
        start = s[0] / 1000
        stop = s[1] / 1000
        if stop - start < UTTERANCES_MIN_LENGTH:
            # Skip short utterances
            continue

        if speaker_ids[i] in speakers_gender:
            speaker_gender = speakers_gender[speaker_ids[i]]
        else:
            print("unknown gender:", speaker_ids[i])
            speaker_gender = 'u'
        
        if speaker_gender == 'm':
            data["audio_length"]['m'] += stop - start
        elif speaker_gender == 'f':
            data["audio_length"]['f'] += stop - start
        
        data["wavscp"].append( (recording_id, os.path.abspath(wav_filename)) )
        utterance_id = f"{speaker_ids[i]}-{recording_id}-{floor(100*start):0>7}_{ceil(100*stop):0>7}"
        data["text"].append((utterance_id, sentences[i]))
        data["segments"].append(f"{utterance_id}\t{recording_id}\t{floor(start*100)/100}\t{ceil(stop*100)/100}\n")
        data["utt2spk"].append(f"{utterance_id}\t{speaker_ids[i]}\n")
    
    return data



def sec2hms(seconds):
    """ Return a string of hours, minutes, seconds from a given number of seconds """
    minutes, seconds = divmod(round(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}' {seconds}''"




##############################################################################
###################################  MAIN  ###################################
##############################################################################


if __name__ == "__main__":
    desc = f"Generate Kaldi data files in directory '{os.path.join(os.getcwd(), SAVE_DIR)}'"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--train", help="train dataset directory", required=True)
    parser.add_argument("--test", help="train dataset directory")
    parser.add_argument("--lm-corpus", help="path of a text file to build the language model")
    parser.add_argument("-d", "--dry-run", help="run script without actualy writting files to disk", action="store_true")
    parser.add_argument("-f", "--draw-figure", help="draw a pie chart showing data repartition", action="store_true")
    args = parser.parse_args()
    print(args)

    if not os.path.isdir(args.train):
        print("`train` argument should be a directory containing aligned audio, text and split files")
        sys.exit(1)
    if args.test and not os.path.isdir(args.test):
        print("`test` argument should be a directory containing aligned audio, text and split files")
        sys.exit(1)
    
    # Add external speakers gender
    speakers_gender = {}
    for fname in spk2gender_files:
        if os.path.exists(fname):
            print(f"Adding speakers from '{fname}'")
            with open(fname, 'r') as f:
                for l in f.readlines():
                    spk, gender = l.strip().split()
                    speakers_gender[spk] = gender
        else:
            print(f"Couldn't find file '{fname}'")
    
    print("\n==== PARSING DATA ITEMS ====")
    corpora = { "train": parse_dataset(args.train) }
    if args.test: corpora["test"] = parse_dataset(args.test)


    if not args.dry_run:

        if not os.path.exists(SAVE_DIR):
            os.mkdir(SAVE_DIR)

        dir_kaldi_local = os.path.join(SAVE_DIR, 'local')
        if not os.path.exists(dir_kaldi_local):
            os.mkdir(dir_kaldi_local)
            

        print("\n==== BUILDING KALDI ====")
        # Copy text from train utterances to language model corpus
        print(f"building file \'{os.path.join(dir_kaldi_local, 'corpus.txt')}\'")
        with open(os.path.join(dir_kaldi_local, "corpus.txt"), 'w') as fout:
            for l in corpora["train"]["corpus"]:
                fout.write(f"{l}\n")
        
        # External text corpus will be added now
        if args.lm_corpus:
            print("parsing and copying external corpus\n")
            with open(os.path.join(dir_kaldi_local, "corpus.txt"), 'a') as fout:
                # for text_file in list_files_with_extension(".txt", LM_TEXT_CORPUS_DIR):
                with open(args.lm_corpus, 'r') as fr:
                    for sentence in fr.readlines():
                        cleaned, _ = get_cleaned_sentence(sentence)
                        for word in cleaned.split():
                            if word.lower() in corpora["train"]["lexicon"]:
                                pass
                            elif word.lower() in capitalized:
                                pass
                            elif is_acronym(word.upper()) and word.upper() in acronyms:
                                pass
                            else:
                                corpora["train"]["lexicon"].add(word)
                        fout.write(cleaned + '\n')
        

        dir_dict_nosp = os.path.join(dir_kaldi_local, 'dict_nosp')
        if not os.path.exists(dir_dict_nosp):
            os.mkdir(dir_dict_nosp)

        # Lexicon.txt
        lexicon_path = os.path.join(dir_dict_nosp, 'lexicon.txt')
        print(f"building file \'{lexicon_path}\'")
        lexicon_phon = set()
        for w in sorted(corpora["train"]["lexicon"]):
            lexicon_phon.add(f"{w} {' '.join(word2phonetic(w))}")
        with open(LEXICON_ADD_PATH, 'r') as f_in:
            for l in f_in.readlines():
                lexicon_phon.add(l.strip())
        for w in acronyms:
            for pron in acronyms[w]:
                lexicon_phon.add(f"{w} {pron}")
        for w in capitalized:
            for pron in capitalized[w]:
                lexicon_phon.add(f"{w.capitalize()} {pron}")
        for w in verbal_tics:
            lexicon_phon.add(f"{w} {verbal_tics[w]}")
        
        with open(lexicon_path, 'w') as f_out:
            f_out.write(f"!SIL SIL\n<SPOKEN_NOISE> SPN\n<UNK> SPN\n")
            for line in sorted(lexicon_phon):
                f_out.write(line + '\n')
                
        
        # silence_phones.txt
        silence_phones_path  = os.path.join(dir_dict_nosp, "silence_phones.txt")
        print(f"building file \'{silence_phones_path}\'")
        with open(silence_phones_path, 'w') as f:
            f.write(f'SIL\noov\nSPN\n')
        

        # nonsilence_phones.txt
        nonsilence_phones_path = os.path.join(dir_dict_nosp, "nonsilence_phones.txt")
        print(f"building file \'{nonsilence_phones_path}\'")
        with open(nonsilence_phones_path, 'w') as f:
            for p in sorted(phonemes):
                f.write(f'{p}\n')
        
        
        # optional_silence.txt
        optional_silence_path  = os.path.join(dir_dict_nosp, "optional_silence.txt")
        print(f"building file \'{optional_silence_path}\'")
        with open(optional_silence_path, 'w') as f:
            f.write('SIL\n')


        for corpus_name in corpora:
            save_dir = os.path.join(SAVE_DIR, corpus_name)
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            
            # Build 'text' file
            fname = os.path.join(save_dir, 'text')
            print(f"building file \'{fname}\'")
            with open(fname, 'w') as f:
                for l in corpora[corpus_name]["text"]:
                    f.write(f"{l[0]}\t{l[1]}\n")
            
            # Build 'segments' file
            fname = os.path.join(save_dir, 'segments')
            print(f"building file \'{fname}\'")
            with open(fname, 'w') as f:
                f.writelines(corpora[corpus_name]["segments"])
            
            # Build 'utt2spk'
            fname = os.path.join(save_dir, 'utt2spk')
            print(f"building file \'{fname}\'")
            with open(fname, 'w') as f:
                f.writelines(corpora[corpus_name]["utt2spk"])
            
            # Build 'spk2gender'
            fname = os.path.join(save_dir, 'spk2gender')
            print(f"building file \'{fname}\'")
            with open(fname, 'w') as f:
                for speaker in sorted(corpora[corpus_name]["speakers"]):
                    f.write(f"{speaker}\t{speakers_gender[speaker]}\n")
            
            # Build 'wav.scp'
            fname = os.path.join(save_dir, 'wav.scp')
            print(f"building file \'{fname}\'")
            with open(fname, 'w') as f:
                for rec_id, wav_filename in corpora[corpus_name]["wavscp"]:
                    f.write(f"{rec_id}\t{wav_filename}\n")
        
    
    print("\n==== STATS ====")

    for corpus in corpora:
        print(f"== {corpus.capitalize()} ==")
        audio_length_m = corpora[corpus]["audio_length"]['m']
        audio_length_f = corpora[corpus]["audio_length"]['f']
        total_audio_length = audio_length_f + audio_length_m
        print(f"- Total audio length:\t{sec2hms(total_audio_length)}")
        print(f"- Male speakers:\t{sec2hms(audio_length_m)}\t{audio_length_m/total_audio_length:.1%}")
        print(f"- Female speakers:\t{sec2hms(audio_length_f)}\t{audio_length_f/total_audio_length:.1%}")


    # print()
    # print("Pleustret gant mouezhioù :")
    # anonymous = 0
    # names = set()
    # for name in speakers:
    #     if "paotr" in name or "plach" in name or "plac'h" in name:
    #         anonymous += 1
    #     else:
    #         names.add(name.replace('_', ' ').title())
    # print(' ॰ '.join(sorted(names)))

    if args.draw_figure:
        import matplotlib.pyplot as plt
        import datetime

        plt.figure(figsize = (8, 8))

        keys, val = zip(*corpora["train"]["subdir_audiolen"].items())
        keys = list(map(lambda x: x.replace('_', ' '), keys))
        total_audio_length = corpora["train"]["audio_length"]["f"] + corpora["train"]["audio_length"]["m"]

        def labelfn(pct):
            if pct > 2:
                return f"{sec2hms(total_audio_length*pct/100)}"
        plt.pie(val, labels=keys, normalize=True, autopct=labelfn)
        plt.title(f"Dasparzh ar roadennoù, {sec2hms(total_audio_length)} en holl")
        plt.savefig(os.path.join(corpora["train"]["path"], f"subset_division_{datetime.datetime.now().strftime('%Y-%m-%d')}.png"))
        print(f"\nFigure saved to \'{corpora['train']['path']}\'")
        # plt.show()