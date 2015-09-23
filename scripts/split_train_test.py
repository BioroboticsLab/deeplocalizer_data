#!/usr/bin/python

import sys

with open(sys.argv[1], 'r') as f:
    filenames = f.readlines()

lastdir = ''
trainfiles = []
testfiles = []
for file in filenames:
    splitted = file.split('/')
    dir = splitted[len(splitted) - 2]
    if dir != lastdir:
        testfiles.append(file)
    else:
        trainfiles.append(file)
    lastdir = dir

for fname, fnamelist in [('train.txt', trainfiles), ('test.txt', testfiles)]:
    with open(fname, 'w') as f:
        f.write(''.join(fnamelist))
