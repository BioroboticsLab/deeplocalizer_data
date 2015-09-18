#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: scripts/generate_train_test.sh images/seasonX"
    exit 1
fi

find $1 -name "*tagger.desc" | sed s/.tagger.desc// > data.txt

scripts/split_train_test.py data.txt

wc -l train.txt
wc -l test.txt
