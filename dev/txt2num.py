"""
mil nav c'hant dek ha tri-ugent


mil:
    unan
    daou
    tri
    pevar
    pemp
    c'hwec'h
    seizh
    eizh
    nav
    dek
    unnek
    daouzek
    trizek
    pevarzek
    pemzek
    c'hwezek
    seitek
    triwec'h
    naontek
    ugent


"""

import sys
sys.path.append("..")
from libMySTT import split_line, pre_process, tokenize, filter_out, punctuation


numerical_tokens = [
    "unan", "un",
    "daou", "div",
    "tri", "teir",
    "pevar", "peder",
    "pemp",
    "c'hwec'h",
    "seizh",
    "eizh",
    "nav",
    "dek",
    "unnek",
    "daouzek",
    "trizek",
    "pevarzek",
    "pemzek",
    "c'hwezek",
    "seitek",
    "triwec'h",
    "naontek",
    "ugent", "warn",
    "tregont",
    "mil", "vil",
    "kant", "c'hant",
    "hanter",
    "ha", "hag",
    ]
    


def build_bigrams(filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            sentences = split_line(line)
            for sentence in sentences:
                sentence = pre_process(sentence)
                sentence = filter_out(sentence, punctuation+'*')
                print(sentence)
                #print(tokenize(sentence))
            print()



if __name__ == "__main__":
    build_bigrams("../corpus/corpus_ya.txt")