# stt-tools

Split files .split should be in the same folder as its related audio file and text file.


## Python packages dependency

 * [Librosa](https://librosa.org/)
 * Pydub
 * Hunspell
 * Colorama

## Transcription rules

Numerals should be written in all letters
(E.g. "1942" --> "mil nav c'hant daou ha daou ugent")

Acronyms should be written in capital letters with no dots or dashes
(E.g. UNESCO, COP21)

Regional forms should be kept if their pronouciation is far from the "standard" form
(E.g. "meump bet/on eus bet", "nege/an hini eo", "lâret/lavaret")
 
## Workflow

Run script ``unpack.py`` found in each dataset folder.

Run script ``wavesplit.py audiofile.wav`` on each audiofile in datasets to generate ``.split`` file and manually align text (in ``.txt`` file) with audio utterances.

Run script ``verify_text_files.py dataset/`` on each dataset folder to quickly check spelling mistakes and register acronyms.

Divide datasets in ``train`` and ``test`` sets.

Run script ``build_kaldi_files.py folder/`` on ``train`` and ``test`` folders.

Copy generated ``data`` folder in your Kaldi recipe folder.

Run ``run.sh`` script in kaldi recipe folder.

Cry, wishing you had a GPU, while waiting for dozens of hours.

When training is finally done, run script ``copy_final_result.sh`` to copy necessary files in ``model`` folder.

Rename ``model`` folder and copy it in vosk ``model`` subfolder.

Enjoy !

## Data files
 * corrected.txt
 * capitalized.txt
 * acronyms.txt
 * lexicon_add.txt
 * lexicon_replace.txt

## Acknowledgement

``br_FR.dic`` and ``br_FR.aff`` in ``hunspell-dictionary`` folder from Drouizig hunspell dictionary.
