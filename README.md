# stt-tools

Personal tool kit to build a breton speech-to-text model with Kaldi.

Split files .split should be in the same folder as its related audio file and text file.


## Python packages dependency

Install required python modules with
```
pip install -r requirements.txt
```

## Text normalization and transcription rules

Numerals should be written in all letters \
(E.g. "1942" --> "mil nav c'hant daou ha daou ugent")

Acronyms should be written in capital letters without dots or dashes \
(E.g. UNESCO, COP21)

Regional forms should be kept if their pronouciation isn't too far from the "standard" form (according to personnal taste or political views...) \
(E.g. "meump bet/on eus bet", "nege/an hini eo", "lâret/lavaret")


## Data format

Each piece of data is made of 3 files : a wave file (16b, 16 KHz sample rate), a split file and a text file containing the transcription.

In the transcription files, empty lines and lines starting with the character `#` should be ignored. Line comments can thus be embedded in the transcription files by using the `#` character.

The first line of split files can include a header with the arguments given to `wavsplit`. The header line must start with the character `#`.

Inline metadata can also by found anywhere between the characters `{` and `}` and should be removed before the training process.

The `*` character can be added if front of words you want remove from the corpus and the lexicon (foreign words, repetitions...). Marked words will still be used for training the acoustic model.
 
## Workflow

Run script `unpack.py` found in each dataset folder.

Run script `wavesplit.py audiofile.wav` on each audiofile in datasets to generate `.split` file and manually align text (in `.txt` file) with audio utterances.

Run script `verify_text_files.py dataset/` on each dataset folder to quickly check spelling mistakes and register acronyms.

Those three first step need to be done only once per audio file. The following steps can be done every time you train a new model.

Create a `corpus` folder and inside it, divide datasets in `train` and `test` sets in their respective folders.

Run script `build_kaldi_files.py folder/` on `train` and `test` folders.

Copy generated `data` folder in your Kaldi recipe folder.

Run `run.sh` script in kaldi recipe folder.

Cry, wishing you had a GPU, while waiting for the model to finish its training (more than a hundred hours in my case).

When training is finally done, run script `copy_final_result.sh` to copy necessary files in `model` folder.

Rename `model` folder to your liking and copy it in vosk `model` subfolder.

Enjoy !

## Wikipedia corpus

Tool used to extract corpus from wikipedia:
https://github.com/attardi/wikiextractor

Wikipedia dumps:
https://dumps.wikimedia.org/brwiki/
https://dumps.wikimedia.org/brwikiquote/

```
python3 WikiExtractor.py -o dumps --json brwiki-20220920-pages-articles-multistream.xml.bz2
```

## Gender bias testing


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
 * Build a better tokenizer
 * Text normalization
 * Try reducing the size of the model (number of hidden layer) as well as the number of epochs
 * Phonemes "YE N", "YOU" for plural markers rather than "I E N", "I OU" ?
 * Phoneme "GW" rather than "G OU" ?
 * Add breton sentences to https://commonvoice.mozilla.org/sentence-collector/

## Acknowledgement

``br_FR.dic`` and ``br_FR.aff`` in ``hunspell-dictionary`` folder, from [An Drouizig](http://www.drouizig.org/index.php/br/) [hunspell dictionary](https://github.com/Drouizig/hunspell-br).
