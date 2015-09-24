#!/usr/bin/python
from collections import defaultdict
import sys
import os

with open(sys.argv[1], 'r') as f:
    filenames = f.readlines()

trainfiles = []
testfiles = []
test_to_train_ratio = 0.15
dirnames = {os.path.dirname(f) for f in sorted(filenames)}
for dirname in dirnames:
    files_in_dir = [f for f in filenames if f.startswith(dirname)]
    n = len(files_in_dir)
    s = round(n*test_to_train_ratio)
    trainfiles.extend(files_in_dir[s:])
    testfiles.extend(files_in_dir[:s])

for fname, fnamelist in [('train.txt', trainfiles), ('test.txt', testfiles)]:
    with open(fname, 'w') as f:
        f.write(''.join(fnamelist))

