import os
import glob
import multiprocessing

folder = 'train'

def convert_to_jpg(rgb_file):
    print('Processing file {}'.format(rgb_file))
    command = 'mogrify -format jpg -resize 640x480 {}'.format(rgb_file)
    print(command)
    os.system(command)

def convert_to_png(dpt_file):
    print('Processing file {}'.format(dpt_file))
    command = 'mogrify -format png -resize 640x480 {}'.format(dpt_file)
    print(command)
    os.system(command)

def main():
    print("globbing all pgms")
    jpg_files = glob.iglob(os.path.join(folder,'**/*.jpg'), recursive=True)
    png_files = glob.iglob(os.path.join(folder,'**/*.png'), recursive=True)

    print('Preprocess start')
    pool = multiprocessing.Pool(processes=12)
    #pool.map(convert_to_png, png_files)
    pool.map(convert_to_jpg, jpg_files)
    pool.close()
    pool.join()   
    print('done')

if __name__ == "__main__":
    main()
