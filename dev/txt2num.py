#! /usr/bin/env python3
# -*- coding: utf-8 -*-



import sys
sys.path.append("..")
from libMySTT import split_line, pre_process, tokenize, filter_out, punctuation
from math import inf
from pprint import pprint

from mkchain import mkchain



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
    "ugent",
    "tregont",
    "mil", "vil",
    "kant", "c'hant",
    ]

numerical_tokens_conj = [
    "hanter",
    "ha", "hag",
    "warn",
]

numerical_tokens_all = numerical_tokens + numerical_tokens_conj


chain = {
    "un" :      ['*', "ha", "hag", "warn"],
    "ur" :      ['*', "c'hant", "milion", "miliard"],
    "unan" :    ['*', "ha", "hag", "warn"],
    "daou" :    ['*', "ha", "hag", "warn", "ugent", "c'hant", "vil", "vilion", "viliard"],
    "div" :     ['*', "ha", "hag", "warn"],
    "tri" :     ['*', "ha", "hag", "warn", "ugent", "c'hant", "mil", "milion", "miliard"],
    "teir" :    ['*', "ha", "hag", "warn"],
    "pevar" :   ['*', "ha", "hag", "warn", "ugent", "c'hant", "mil", "milion", "miliard"],
    "peder" :   ['*', "ha", "hag", "warn"],
    "pemp" :    ['*', "ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "c'hwec'h": ['*', "ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "seizh" :   ['*', "ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "eizh" :    ['*', "ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "nav" :     ['*', "ha", "hag", "warn", "c'hant", "mil", "milion", "miliard"],
    "dek" :     ['*', "ha", "mil", "milion", "miliard"],
    "unnek" :   ['*', "ha", "kant", "mil", "milion", "miliard"],
    "daouzek" : ['*', "ha", "kant", "mil", "milion", "miliard"],
    "trizek" :  ['*', "ha", "kant", "mil", "milion", "miliard"],
    "pevarzek": ['*', "ha", "kant", "mil", "milion", "miliard"],
    "pemzek" :  ['*', "ha", "kant", "mil", "milion", "miliard"],
    "c'hwezek": ['*', "ha", "kant", "mil", "milion", "miliard"],
    "seitek" :  ['*', "ha", "kant", "mil", "milion", "miliard"],
    "triwec'h": ['*', "ha", "kant", "mil", "milion", "miliard"],
    "naontek" : ['*', "ha", "kant", "mil", "milion", "miliard"],
    "ugent" :   ['*'],
    "tregont" : ['*'],
    "mil" :     ['*', "un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter"],
    "vil" :     ['*', "un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter"],
    "kant" :    ['*', "un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter"],
    "c'hant" :  ['*', "un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter"],
    "ha" :      ["daou", "tri", "pevar", "tregont"],
    "hag" :     ["hanter"],
    "hanter" :  ["kant"],
    "warn" :    ["ugent"],
}


chain2 = {
    "un" :      ["ha", "hag", "warn"],
    "ur" :      ["c'hant", "milion", "miliard"],
    "unan" :    ["ha", "hag", "warn"],
    "daou" :    ["ha", "hag", "warn", "ugent", "c'hant", "vil", "vilion", "viliard"],
    "div" :     ["ha", "hag", "warn"],
    "tri" :     ["ha", "hag", "warn", "ugent", "c'hant", "mil", "milion", "miliard"],
    "teir" :    ["ha", "hag", "warn"],
    "pevar" :   ["ha", "hag", "warn", "ugent", "c'hant", "mil", "milion", "miliard"],
    "peder" :   ["ha", "hag", "warn"],
    "pemp" :    ["ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "c'hwec'h": ["ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "seizh" :   ["ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "eizh" :    ["ha", "hag", "warn", "kant", "mil", "milion", "miliard"],
    "nav" :     ["ha", "hag", "warn", "c'hant", "mil", "milion", "miliard"],
    "dek" :     ["ha", "mil", "milion", "miliard"],
    "unnek" :   ["ha", "kant", "mil", "milion", "miliard"],
    "daouzek" : ["ha", "kant", "mil", "milion", "miliard"],
    "trizek" :  ["ha", "kant", "mil", "milion", "miliard"],
    "pevarzek": ["ha", "kant", "mil", "milion", "miliard"],
    "pemzek" :  ["ha", "kant", "mil", "milion", "miliard"],
    "c'hwezek": ["ha", "kant", "mil", "milion", "miliard"],
    "seitek" :  ["ha", "kant", "mil", "milion", "miliard"],
    "triwec'h": ["ha", "kant", "mil", "milion", "miliard"],
    "naontek" : ["ha", "kant", "mil", "milion", "miliard"],
    "ugent" :   ["mil", "milion", "miliard"],
    "tregont" : ["mil", "milion", "miliard"],
    "mil" :     ["un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter", "miliard"],
    "vil" :     ["un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter", "miliard"],
    "kant" :    ["un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter", "mil", "milion", "miliard"],
    "c'hant" :  ["un", "unan", "daou", "tri", "pevar", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter", "mil", "milion", "miliard"],
    "ha" :      ["daou", "tri", "pevar", "tregont"],
    "hag" :     ["hanter"],
    "hanter" :  ["kant"],
    "warn" :    ["ugent"],
}

starters = ["zero", "mann", "un", "ur", "unan", "daou", "div", "tri", "teir", "pevar", "peder", "pemp", "c'hwec'h", "seizh", "eizh", "nav", "dek", "unnek", "daouzek", "trizek", "pevarzek", "pemzek", "c'hwezek", "seitek", "triwec'h", "naontek", "ugent", "tregont", "hanter", "kant", "mil"]



token_value = {
    "mann" : 0, "zero" : 0,
    "un" : 1, "ur" : 1, "unan" : 1,
    "daou" : 2, "div" : 2,
    "tri" : 3, "teir" : 3,
    "pevar" : 4, "peder" : 4,
    "pemp" : 5,
    "c'hwec'h" : 6,
    "seizh" : 7,
    "eizh" : 8,
    "nav" : 9,
    "dek" : 10,
    "unnek" : 11,
    "daouzek" : 12,
    "trizek" : 13,
    "pevarzek" : 14,
    "pemzek" : 15,
    "c'hwezek" : 16,
    "seitek" : 17,
    "triwec'h" : 18,
    "naontek" : 19,
    "ugent" : 20,
    "tregont" : 30,
    "kant" : 100, "c'hant" : 100,
    "mil" : 1000, "vil" : 1000,
    "milion" : 1_000_000, "vilion" : 1_000_000,
    "miliard" : 1_000_000_000, "viliard" : 1_000_000_000,
    "hanter" : 0.5,
    "ha" : '+', "hag" : '+', "warn" : '+'
}


def solve(token_list):
    # Token 0.5 ("hanter") takes precedence and is applied to next closest token
    while 0.5 in token_list:
        i = token_list.index(0.5)
        if i < len(token_list) - 1:
            token_list = token_list[:i] + [0.5 * token_list[i+1]] + token_list[i+2:]
        else:
            break

    # Find highest value token
    i_max, val_max = -1, -1
    i_token_add, token_add = -1, False
    for i, val in enumerate(token_list):
        if val == '+':
            token_add = True
            i_token_add = i
        elif val > val_max:
            val_max = val
            i_max = i
    
    if token_add and val_max < 100:
        # Invert two parts of token_list around '+' symbol and solve
        inverted = token_list[i_token_add+1:] + token_list[:i_token_add]
        return solve(inverted)
    else:
        # solve recursively
        if len(token_list) == 0:
            return 0
        elif len(token_list) == 1:
            return token_list[0]
        else:
            left_part = solve(token_list[:i_max])
            if left_part == 0:
                left_part = 1
            right_part = solve(token_list[i_max+1:])
            return left_part * val_max + right_part


def translate(sentence):
    sentence = sentence.replace('-', ' ')
    tokens = sentence.split()
    tokens = [token_value[t] for t in tokens if t in token_value]
    return int(solve(tokens))


def translate_numbers(sentence):
    sentence = sentence.replace('-', ' ')
    tokens = sentence.split()

    ai, bi = 0, 1
    extracted = []
    current = []
    embedded = []
    while ai < len(tokens):
        a = tokens[ai]
        b = tokens[bi]
        if current:
            last = current[-1]
            if a in chain2[last]:
                if b in chain2[a]:
                    # Follow
                    current.append(a)
                    ai += 1
                    bi += 1
                elif b in starters:
                    # New number
                    current.append(a)
                    extracted.append(current)
                    current = []
                    ai += 1
                    bi += 1
                else:
                    # Could be an embedded name
                    pass
        else:
            if a in starters:
                if b in chain2[a]:
                    # Follow
                    current.append(a)
                    ai += 1
                    bi += 1
                elif b in starters:
                    # New number
                    current.append(a)
                    extracted.append(current)
                    current = []
                    ai += 1
                    bi += 1
                else:
                    # Other word, check for stride
                    pass


def validate_bigram(a, b):
    if b not in chain: b = '*'
    return a in chain and b in chain[a]


def analyse(tokens):
    mapping = []
    for i in range(len(tokens)):
        t = tokens[i]
        if t in ("hag", "ha", "warn"):
            mapping.append('+')
        elif i>0 and tokens[i-1] in chain2 and t in chain2[tokens[i-1]]:
            mapping.append(2)
        elif t in starters:
            mapping.append(1)
        else:
            mapping.append(0)
    return mapping



def parse_file(filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            sentences = split_line(line)
            for sentence in sentences:
                tokens = tokenize(sentence)
                validated = parse_tokens(tokens)
                if len(validated) > 0:
                    print(sentence)
                    for val in validated:
                        print("  ", [tokens[i] for i in val])


def build_bigrams(filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            sentences = split_line(line)
            for sentence in sentences:
                tokens = tokenize(sentence)
                sentence_num_tokens = []
                num_tokens = []
                dist = inf
                for t in tokens:
                    dist += 1
                    if t in numerical_tokens:
                        num_tokens.append(t)
                        dist = 0
                    elif dist <= 1:
                        num_tokens.append(t)
                        if t in numerical_tokens_all:
                            dist = 0
                    elif dist <= 2 and t in numerical_tokens_all:
                        num_tokens.append(t)
                    else:
                        if num_tokens:
                            sentence_num_tokens.append(num_tokens)
                            num_tokens = []


                if len(sentence_num_tokens) > 1:
                    #print(sentence)
                    for nt in sentence_num_tokens:
                        print("  ", nt)


def build_mkchain_2ndeg():
    mkchain = dict()

    with open("numbers.txt", 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            _, txt = line.split(" = ")
            txt = txt.replace('-', ' ')
            tokens = txt.split()
            tokens = ['['] + tokens + [']']
            # print(tokens)
            # print(txt)
            for i in range(len(tokens)-2):
                k, v = (tokens[i], tokens[i+1]), tokens[i+2]
                if k in mkchain:
                    if not v in mkchain[k]: mkchain[k].append(v)
                else:
                    mkchain[k] = [v]
        pprint(mkchain)


def test_file():
    with open("numbers.txt", 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            num, txt = line.split(" = ")
            num = int(num)
            rep = translate(txt)
            if rep != num:
                print(num, txt, rep)


def test():
    test_cases = [
        ("un den", "1 den"),
        ("ur marc'h", "1 marc'h"),
        ("ur c'hant bennak a dud", "100 bennak a dud"),
        ("mil daou", "1002"),
        ("mil nav c'hant pevar ha pevar-ugent", "1984"),
        ("naontek kant c'hwec'h ha tregont", "1936"),
        ("er bloavez daou vil tri warn-ugent", "er bloavez 2023"),
        ("kant den hag hanter-kant a oa", "150 den a oa"),
        ("kant daou vil pevarzek", "102014"),
        ("tri kazh ha daou besk", "3 kazh ha 2 besk"),
        ("unan daou tri, staget mat ar c'hi", "1 2 3, staget mat ar c'hi"),
        ("div blac'h kozh ha daou-ugent", "42 blac'h kozh"),
        ("div blac'h kozh ha daou-ugent kazh du", "2 blac'h kozh ha 42 kazh du"),
        ("div blac'h kozh ha daou-ugent aet d'an anaon", "42 blac'h kozh aet d'an anaon"),
        ("kant tri patatezenn hag hanter-kant em eus debret", "153 patatezenn am eus debret")
    ]

    """
    [1000, 2]
    [(1), 1000, 9, 100, 4 "ha" 4, 20]
    [19, 100, 6 "ha" 30]
    [2, 1000, 3 "warn" 20]
    [(1), 100, *, "hag", 0.5, 100]
    [100, 2, 1000, 14]
    """

    for sentence in [s[0] for s in test_cases]:
        tokens = tokenize(sentence)
        print(sentence)
        print(analyse(tokens))
        print()
        # for val in validated:
        #     # print("  ", [tokens[i] for i in val])
        #     print("    ", translate(sentence))


if __name__ == "__main__":
    #build_bigrams("../corpus/wiki_corpus.txt")
    #parse_file("../corpus/wiki_corpus.txt")
    test()
    # test_file()
    # build_mkchain_2ndeg()
