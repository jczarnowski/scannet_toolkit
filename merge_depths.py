import os
import sys
import argparse
import multiprocessing
import cv2
import numpy as np
import tqdm
from functools import partial


def merge_depths(data, nframes):
    num, frame = data

    # load both depth maps
    depth_rendered = cv2.imread('{}.rendered_depth.png'.format(frame), cv2.IMREAD_ANYDEPTH)
    depth_original = cv2.imread('{}.depth.pgm'.format(frame), cv2.IMREAD_ANYDEPTH)

    # the faulty rendering assigns 1 to missing depth values, fix that
    depth_rendered = np.where(depth_rendered == 1000, 0, depth_rendered)

    depth_rendered = depth_rendered.astype(np.float32) / 1000.0
    depth_original = depth_original.astype(np.float32) / 1000.0

    # merge them
    depth_merged = np.where(np.abs(depth_original - depth_rendered) > 0.1, depth_original,
                            depth_rendered)
    depth_merged = np.where(depth_merged == 0, depth_rendered, depth_merged)

    # import tfslam
    # avgdpt = 2
    # prx_rendered = tfslam.dpt_to_prx(depth_rendered, avgdpt)
    # prx_orig = tfslam.dpt_to_prx(depth_original, avgdpt)
    # prx_merged = tfslam.dpt_to_prx(depth_merged, avgdpt)

    # frac = np.count_nonzero(depth_rendered) / 640. / 480.
    # print(frac)
    # if frac < 0.6:
    #     mosaic = tfslam.create_mosaic([[prx_orig, prx_rendered, prx_merged]])
    #     cv2.imshow('results', mosaic)
    #     cv2.waitKey(0)

    # save result
    cv2.imwrite('{}.merged_depth.png'.format(frame), (depth_merged * 5000.0).astype(np.uint16))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='Path to directory containing sequences to preprocess', required=True)
    parser.add_argument('--nproc', default=8, help='Number of processes to spawn')
    args = parser.parse_args()

    # generate all frame names
    print('Generating frame list')
    all_frames = list()
    sequences = sorted(next(os.walk(args.data_dir))[1])
    nframes = 0
    for seq in sequences:
        infofile = os.path.join(args.data_dir, seq, '_info.txt')
        seqlen = int(open(infofile, 'r').readlines()[-1].split(' ')[-1])
        all_frames += [[nframes + i, '{}/{}/frame-{:06d}'.format(args.data_dir, seq, i)] for i in range(seqlen)]
        nframes += seqlen

    nframes = len(all_frames)

    print('Number of sequences: ', len(sequences))
    print('Number of frames: ', nframes)

    pool = multiprocessing.Pool(processes=args.nproc)
    do_work = partial(merge_depths, nframes=nframes)
    for _ in tqdm.tqdm(pool.imap_unordered(do_work, all_frames), total=len(all_frames)):
        pass

    pool.close()
    pool.join()
    print('Done')


if __name__ == "__main__":
    main()
