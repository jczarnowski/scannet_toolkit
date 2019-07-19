import os
import sys
import argparse
import multiprocessing
import subprocess


def preprocess_rgb(sequence):
    sys.stderr.write(('Processing sequence {}\n'.format(sequence)))
    command = 'imgp -x 640x480 -wf {}/*.color.jpg'.format(sequence)
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='Path to directory containing sequences to preprocess', required=True)
    parser.add_argument('--nproc', default=8, help='Number of processes to spawn')
    args = parser.parse_args()

    print("Finding all sequences to process")
    sequences = next(os.walk(args.data_dir))[1]
    sequences.sort()
    sequences = [os.path.join(args.data_dir, seq) for seq in sequences]

    print('Preprocess start')
    pool = multiprocessing.Pool(processes=args.nproc)
    pool.map(preprocess_rgb, sequences)

    pool.close()
    pool.join()   
    print('Done')


if __name__ == "__main__":
    main()
