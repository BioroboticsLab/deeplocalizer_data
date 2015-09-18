#/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: scripts/generate_all_borders.sh images/seasonX"
    exit 1
fi

base_path=`pwd`

for cam in $1/*; do
    [ -d "${cam}" ] || continue
    cd ${cam}
    echo "${cam}"
    for path in */; do
        [ -d "${path}" ] || continue
        echo "${path}"
        cd ${path}
        find . -name "*tagger.desc" | sed s/.tagger.desc// | sed s/_wb.jpeg/.jpeg/ > add_border_images.txt
        add_border add_border_images.txt -o `pwd`
        rm add_border_images.txt
        cd ..
    done
    cd ${base_path}
done
