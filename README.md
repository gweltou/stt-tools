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
 

``br_FR.dic`` and ``br_FR.aff`` in ``hunspell-dictionary`` folder from Drouizig hunspell dictionary.
