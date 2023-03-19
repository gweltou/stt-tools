#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from colorama import Fore
from libMySTT import extract_metadata, split_line, get_cleaned_sentence, get_correction



def test_extract_metadata():
    sentences = [
        "Ober a reomp ur podskignañ anvet \"Petra c'hoari ganit ?\" {tornoz:m}",
        "Ur c'hoari pep-hini dre vras, pe meur a c'hoari. {geekezig:f}",
        "netra ispisial amañ",
        "ur anv kompozed {b22_plac'h23}",
        "Ya met moaien a zo met ret e vez paeañ anezho. {lors_jouin}",
        "test gant un anv dianv {plac'h12}",
        "ur paotr o komz {paotr}",
        "kar ni meump bet labouret {?} pa oamp yaouank heñ … bet meump bet graet {?}bep seurt heñ,",
        "{parser:no-lm}\noh la la"
    ]

    for s in sentences:
        print(s)
        cleaned, metadata = extract_metadata(s)
        print(cleaned, metadata, end="\n\n")
    


def test_split_lines():
    sentences = [
        "Un tan-gwall a voe d'ar 1añ a viz Gouhere 2011 el leti. Ne voe den ebet gloazet pe lazhet. Un nebeud estajoù nemetken a oa bet tizhet.",
        "E 1938 e voe he gwaz harzet ha lazhet en U. R. S. S., ar pezh na viras ket ouzh Ana Pauker a chom feal d'ar gomunouriezh, d'an U. R. S. S. ha da Jozef Stalin.",
        "Ur maen-koun zo war lein, da bevar barzh eus ar vro : T. Hughes Jones, B.T. Hopkins, J. M. Edwards hag Edward Prosser Rhys.",
        """C'hoariet en deus evit Stade Rennais Football Club etre 1973 ha 1977 hag e 1978-1979. Unan eus ar c'hoarierien wellañ bet gwelet e klub Roazhon e oa. Pelé en deus lavaret diwar e benn : « "Kavet 'm eus an hini a dapo ma flas. Laurent Pokou e anv." ».""",
        """Hervez Levr ar C'heneliezh ec'h eo Yafet eil mab Noah. Hervez ar Bibl e tiskouezas doujañs e-kenver e dad mezv-dall. Benniget e voe gantañ evel Shem : "Frankiz ra roio Doue da Yafet ! Ha ra chomo e tinelloù Shem !" """,
        "Tout an dud en em soñj. Piv int ar skrivagnerien-se ? Eus pelec'h emaint o tont... ?",
        "Tamm ebet. Klasket em boa e-pad 5 miz ha n’on ket bet plijet ; un afer a bublik eo.",
        "unan daou tri : pevar pemp c'hwec'h",
        ]
    lengths = [3, 1, 2, 5, 5, 3, 3, 2]
    for i, s in enumerate(sentences):
        splits = split_line(s)
        print(splits)
        print(len(splits))
        if len(splits) == lengths[i]:
            print(Fore.GREEN + "OK" + Fore.RESET)
        else :
            print(splits)
            print(Fore.RED + "FAIL" + Fore.RESET)
        print()



def test_get_cleaned_sentence():
    sentences = [
        "ar bloavezh 1935 a zo en XXvet kantved",
        "o gwelet Charlez VI e vi warc'hoazh",
        "un test gant ur *ger da *skarzhañ",
        ]
    expected = [
        "ar bloavezh mil nav c'hant pemp ha tregont a zo en ugentvet kantved",
        "o gwelet Charlez c'hwec'h e vi warc'hoazh",
        "un test gant ur ger da *skarzhañ",
        ]
    
    for i, s in enumerate(sentences):
        cleaned, _ = get_cleaned_sentence(s, rm_bl=True)
        correction, _ = get_correction(s)
        error = False
        if cleaned != expected[i]:
            error = True
            print(s)
            print(cleaned)
            print(correction)
        if error:
            print("Error found")



if __name__ == "__main__":

    test_extract_metadata()
    # test_split_lines()
    # test_get_cleaned_sentence()