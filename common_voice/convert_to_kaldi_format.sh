#!/usr/bin/env bash


echo "Prepare train dataset"
python3 deepspeech_to_kaldi.py train br/validated.tsv

echo "Prepare test dataset"
python3 deepspeech_to_kaldi.py test br/test.tsv
