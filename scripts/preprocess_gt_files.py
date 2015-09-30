#! /usr/bin/env python3
import sys
import glob
import os
import shutil
import fnmatch
import json

import subprocess
import re

replace_wb_reg = re.compile("_wb.jpeg$")


def strip_wb(fname):
    return replace_wb_reg.sub(".jpeg", fname)

if len(sys.argv) == 1:
    print("Usage is {} [dir/with/gt_files]".format(sys.argv[0]))
    exit(1)

dirname = sys.argv[1]
gt_images = []

tdat_files = []
for root, dirnames, fnames in os.walk(dirname):
    for tdat_file in fnmatch.filter(fnames, "*.tdat"):
        tdat_files.append(os.path.join(root, tdat_file))
        with open(os.path.join(root, tdat_file)) as f:
            tdat = json.load(f)
            images = tdat['value0']["_filenames"]
            images = [os.path.join(root, img + ".jpeg") for img in images]
            gt_images.extend(images)

pathfile = "preprocess.txt"
output_dir = "gt_preprocessed"
with open(pathfile, "w+") as f:
    f.write('\n'.join(gt_images))

for image in gt_images:
    shutil.copy(image, image + ".origin")

subprocess.call(["add_border", "-o", output_dir, "--border", "0", "--use-threshold", "1", "--binary-image", "1", pathfile])

for image in glob.glob(output_dir + "/*_wb.jpeg"):
    shutil.move(image, strip_wb(image))

for tdat_file in tdat_files:
    shutil.copy(tdat_file, output_dir)
