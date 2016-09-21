#!/usr/bin/env python3

import click
import random
import json
import h5py
import os

import cv2
import numpy as np
from tqdm import tqdm
from scipy.stats import multivariate_normal
from skimage.io import imread


def parse_tagger_files(deeplocalizer_data_dir):
    gt = []

    for root, dirs, files in os.walk(deeplocalizer_data_dir):
        for file in files:
            if file.endswith('tagger.json'):
                path = os.path.join(root, file)
                data = json.loads(open(path, 'r').read())
                data['filename'] = os.path.join(root, data['filename'].split('/')[-1])

                if '_wb' in data['filename']:
                    data['filename'] = ''.join(data['filename'].split('_wb'))
                if '.b.' in data['filename']:
                    data['filename'] = ''.join(data['filename'].split('.b'))
                if '.clahe.' in data['filename']:
                    data['filename'] = ''.join(data['filename'].split('.clahe'))
                if not os.path.exists(data['filename']):
                    print('{} is missing'.format(data['filename']))
                else:
                    gt.append(data)

    return gt


def create_hdf5_repo(path, num_files, samples_per_file, roi_size):
    hf = h5py.File(path, 'w')
    num_samples = num_files * samples_per_file

    group = hf.create_group('saliency')
    group.create_dataset('X', shape=(num_samples, roi_size, roi_size), dtype=np.float32)
    group.create_dataset('Y', shape=(num_samples, roi_size, roi_size), dtype=np.float32)

    return hf, group.get('X'), group.get('Y')


def generate_dataset(gt, clahe, X, Y, tag_size, samples_per_file):
    indices = list(range(len(X)))
    random.shuffle(indices)

    pdf = multivariate_normal.pdf(
        np.dstack(np.meshgrid(np.arange(-80, 80), np.arange(-80, 80))),
        mean=(0, 0),
        cov=(250, 250))

    idx = 0
    for gt_file in tqdm(gt):
        fname = gt_file['filename']

        image = imread(fname)
        if image.ndim == 3:
            image = image[:, :, 0]

        image = clahe.apply(image)
        image = np.pad(image, 32, mode='edge')

        saliency = np.zeros((image.shape[0]+200, image.shape[1]+200), dtype=np.float)

        for tag in gt_file['tags']:
            if tag['tagtype'] == 'istag':
                sx = slice(tag['y']+100-80, tag['y']+100+80)
                sy = slice(tag['x']+100-80, tag['x']+100+80)
                saliency[sx, sy] = np.maximum(saliency[sx, sy], pdf)

        saliency /= np.max(saliency)
        saliency_padded = np.copy(saliency)
        saliency = saliency[100:-100, 100:-100]
        assert(saliency.shape[:2] == image.shape[:2])

        sample_indices = np.random.choice(
            len(saliency.flatten()),
            size=samples_per_file,
            replace=False,
            p=(saliency.flatten() + 0.01) / np.sum(saliency + 0.01))

        sample_coords = np.unravel_index(sample_indices, saliency.shape) + \
            np.array((100, 100))[:, np.newaxis]

        image_padded = np.pad(image, 100, mode='edge')
        samples = [image_padded[x-tag_size//2:x+tag_size//2,
                                y-tag_size//2:y+tag_size//2] for x, y in sample_coords.T]
        samples_saliency_im = \
            [saliency_padded[x-tag_size//2:x+tag_size//2,
                             y-tag_size//2:y+tag_size//2] for x, y in sample_coords.T]

        for x, y in zip(samples, samples_saliency_im):
            X[indices[idx]] = x
            Y[indices[idx]] = y
            idx += 1


@click.command()
@click.option('--path', help='Location of deeplocalizer_data repo',
              type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--output', help='Location of trainset hdf5 file',
              type=click.Path(exists=False, dir_okay=False, file_okay=True))
@click.option('--roi_size', type=int, default=128, help='ROI width and height')
@click.option('--samples_per_file', type=int, default=2048,
              help='How many samples to extract from each file')
@click.option('--clahe_clip_limit', type=int, default=2)
@click.option('--clahe_tile_width', type=int, default=64)
@click.option('--clahe_tile_heigth', type=int, default=64)
def generate_trainset(path, output, roi_size, samples_per_file,
                      clahe_clip_limit, clahe_tile_width, clahe_tile_heigth):
    gt_files = parse_tagger_files(path)
    hf, X, Y = create_hdf5_repo(output, len(gt_files), samples_per_file, roi_size)
    clahe = cv2.createCLAHE(clahe_clip_limit, (clahe_tile_width, clahe_tile_heigth))

    generate_dataset(gt_files, clahe, X, Y, roi_size, samples_per_file)

    hf.close()


if __name__ == '__main__':
    generate_trainset()
