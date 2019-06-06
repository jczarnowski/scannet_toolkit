# scannet_toolkit

Scripts for downloading a smaller random sample of the [ScanNet](http://www.scan-net.org/ScanNet/) dataset 
and generate depth maps from the PLY models of the scenes.

## Installation
Clone the repo recursively:

```
git clone --recurse-submodules git@github.com:jczarnowski/scannet_toolkit.git
```

## Usage
First, generate a random sample of scenes using `sample.sh`. To generate a 40% sample of the ScanNet training set:
```
bash sample.sh 40 samples/scannetv2_train.txt > samples/my_40_sample.txt
```
Files `samples/scannetv2_train.txt` and `samples/scannetv2_val.txt` contain the scene names for the official ScanNet test/train split.

Download your sample using `download_sample.sh` to a directory `out_dir` as follows:
```
bash download_sample.sh samples/my_40_sample.txt <out_dir>
```

The script currently only pulls and decodes the `.sens` files and the `_vh_clean_2.ply` models.

The `preprocess.py` script is WIP and resizes the images to 640x480 and convers pgm to png concurrently.

## Authors
 * Jan Czarnowski
 * Ronald Clark
