#/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: scripts/generate_all_borders.sh images/seasonX"
    exit 1
fi

base_path=`pwd`
options="--use-hist-eq 1 --use-threshold 1"
for cam in $1/*; do
    [ -d "${cam}" ] || continue
    cd ${cam}
    echo "${cam}"
    for path in */; do
        [ -d "${path}" ] || continue
        echo "${path}"
        cd ${path}
        find . -name "*tagger.json" | sed s/.tagger.json// | sed s/_wb.jpeg/.jpeg/ > add_border_images.txt
        cat add_border_images.txt
        preprocess add_border_images.txt -o `pwd` $options
        rm add_border_images.txt
        cd ..
    done
    find . -name "*tagger.json" | sed s/.tagger.json// | sed s/_wb.jpeg/.jpeg/ > add_border_images.txt
    preprocess add_border_images.txt -o `pwd` $options
    rm add_border_images.txt
    cd ${base_path}
done
