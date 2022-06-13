# stt-tools

Split files .split should be in the same folder as its related audio file and text file.


## Python packages dependency

 * numpy \
   ``pip3 install numpy``
 * [Librosa](https://librosa.org/)
 * Pydub
 * Hunspell \
   ``pip3 install cyhunspell``
 * Colorama

## Transcription rules

Numerals should be written in all letters \
(E.g. "1942" --> "mil nav c'hant daou ha daou ugent")

Acronyms should be written in capital letters with no dots or dashes \
(E.g. UNESCO, COP21)

Regional forms should be kept if their pronouciation is far from the "standard" form (but that's open to awkward an unending debates) \
(E.g. "meump bet/on eus bet", "nege/an hini eo", "lâret/lavaret")
 
## Workflow

Run script ``unpack.py`` found in each dataset folder.

Run script ``wavesplit.py audiofile.wav`` on each audiofile in datasets to generate ``.split`` file and manually align text (in ``.txt`` file) with audio utterances.

Run script ``verify_text_files.py dataset/`` on each dataset folder to quickly check spelling mistakes and register acronyms.

Those three first step need to be done only once per audio file. The following steps can be done every time you train a new model.

Create a ``corpus`` folder and inside it, divide datasets in ``train`` and ``test`` sets in their respective folders.

Run script ``build_kaldi_files.py folder/`` on ``train`` and ``test`` folders.

Copy generated ``data`` folder in your Kaldi recipe folder.

Run ``run.sh`` script in kaldi recipe folder.

Cry, wishing you had a GPU, while waiting for the model to finish its training (more than a hundred hours in my case).

When training is finally done, run script ``copy_final_result.sh`` to copy necessary files in ``model`` folder.

Rename ``model`` folder to your liking and copy it in vosk ``model`` subfolder.

Enjoy !

## Data files
 * ``corrected.txt`` \
    List of key -> values separated by a tabulation.\
    Two types of corrections, single token substitution or raw text substitution (when a space is present in key).\
    Keys of single token are case insensitive but corrections must be capitalized when appropriate.
 * ``capitalized.txt``\
    List of single words followed by phonemes
 * ``acronyms.txt``\
    List of acronyms (in capital letters) followed by phonemes
 * ``lexicon_add.txt``\
    Store additional regional pronouciations for breton words
 * ``lexicon_replace.txt``\
    Replace phonetics for words in lexicon (foreign words for instance)

## TODO
 * Try reducing the size of the model (number of hidden layer) as well as the number of epochs
 * Phonemes "YE N", "YOU" for plural markers rather than "I E N", "I OU" ?
 * Phoneme "GW" rather than "G OU" ?

## Acknowledgement

``br_FR.dic`` and ``br_FR.aff`` in ``hunspell-dictionary`` folder, from [An Drouizig](http://www.drouizig.org/index.php/br/) hunspell dictionary.
