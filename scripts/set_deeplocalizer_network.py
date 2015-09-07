#! /usr/bin/env python3

import json
import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('settings', type=str,
                       help='path to the settings to edits.')
    parser.add_argument('--model', type=str,
                        default='deeplocalizer-model/deploy.prototxt',
                        help='path to the deeplocalizer network'
                             ' deploy.prototxt file')
    parser.add_argument(
        '--weights', type=str,
        default='deeplocalizer-model/latest_iteration.caffemodel',
        help='path to the deeplocalizer *.caffemodel file')

    args = parser.parse_args()
    with open(args.settings, "r") as f:
        settings = json.load(f)
    settings['LOCALIZER']['DEEPLOCALIZER_MODEL_FILE'] = args.model
    settings['LOCALIZER']['DEEPLOCALIZER_PARAM_FILE'] = args.weights
    with open(args.settings, "w") as f:
        json.dump(settings, f, indent=4)
