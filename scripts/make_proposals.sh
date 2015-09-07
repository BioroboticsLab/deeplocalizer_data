#! /usr/bin/env bash


set -e

IMAGE_DIR=${1%/}      # remove optional slash at the end

function printUsage() {
    echo "./scripts/make_proposals.sh IMAGE_DIR"
    echo "    where IMAGE_DIR is the path to a directory with the images to preprocess"
    echo "This scripts preprocesses the images, generates proposals"
    echo "and creates a file with the right image paths."
    echo "You are highly encouraged to run this script on the data before tagging."
}

if [ "$IMAGE_DIR" == "" ]; then
    printUsage
    exit 1
fi

if [ "$IMAGE_DIR" == "-h" ] || [ "$IMAGE_DIR"  == "--help" ]; then
    printUsage
    exit 0
fi

if [ ! -d "$IMAGE_DIR" ]; then
    echo "Directory does not exists: $IMAGE_DIR"
    exit 1
fi

if [ $(which add_border) == "" ]; then
    echo "Could not find the 'add_border command."
    echo "Did you add the deeplocalizer-tagger binaries to your PATH"
    exit 1
fi

ADD_BORDER_FILE="$IMAGE_DIR/add_border_images.txt"
GENERATE_PROPOSALS="$IMAGE_DIR/proposals_images.txt"
function shouldAddBorder {
    if [ ! -e "$ADD_BORDER_FILE" ]; then
        echo "yes"
    fi
    while read img; do
        if [ ! -e $img ]; then
            echo "yes"
            return
        fi
    done <"$ADD_BORDER_FILE"
    echo "no"
}
cd $IMAGE_DIR

if [ $(shouldAddBorder) == "yes"  ]; then
    find $IMAGE_DIR -name "*.jpeg" | sort | grep -e "groundtruth" | grep -e "wb.jpeg" > "$ADD_BORDER_FILE"

    echo "$ADD_BORDER_FILE"
    N_FILES="$(wc -l "$ADD_BORDER_FILE")"

    echo "adding border to $N_FILES"
    add_border --output-pathfile=$GENERATE_PROPOSALS --output-dir=$IMAGE_DIR --pathfile=$ADD_BORDER_FILE
fi
echo "generate proposals for $N_FILES"

cd $IMAGE_DIR;
    CONFIG_FILE="pipeline-config.json"
    if [ ! -e $CONFIG_FILE ]; then
        ln -s parameter/settings.json pipeline-config.json
    fi
    GENERATE_PROPOSALS="proposals_images.txt"
    generate_proposals --pathfile $GENERATE_PROPOSALS


