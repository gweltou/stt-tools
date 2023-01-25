#! /bin/bash

FILES="
acronyms.txt
capitalized.txt
gwenedeg.txt
lexicon_add.txt
lexicon_replace.txt
hunspell-dictionary/add.txt
"

for file in $FILES
do
    sort $file -o $file
done
