# scannet_toolkit

Scripts for downloading a smaller random sample of the [ScanNet](http://www.scan-net.org/ScanNet/) dataset 
and generating depth maps from the PLY models of the scenes.

## Installation
Clone the repo recursively:

```
git clone --recurse-submodules https://github.com/jczarnowski/scannet_toolkit.git
```

Obtain the `download-scannet.py` following the instructions from [the authors' website](http://www.scan-net.org/ScanNet/#scannet-c-toolkit)
and place it in the repo root directory.

## Usage

#### Sampling
First, generate a random sample of scenes using `sample.sh`. To generate a 40% sample of the ScanNet training set:
```
bash sample.sh 40 samples/scannetv2_train.txt > samples/my_40_sample.txt
```
Files `samples/scannetv2_train.txt` and `samples/scannetv2_val.txt` contain the scene names for the official ScanNet test/train split.

You should also make sure that your generated train/test samples are exclusive. This can be quickly done with e.g. grep:
```
grep -Fxf file1 file2
```

#### Downloading

Download your sample using `download_sample.sh` to a directory `out_dir` as follows:
```
bash download_sample.sh samples/my_40_sample.txt <out_dir>
```
The script currently only pulls and decodes the `.sens` files and the `_vh_clean_2.ply` models.

#### Preprocessing
The `preprocess.py` script is a WIP and resizes the images to 640x480.

### Rendering
The `render.py` script uses the trajectory and the scene PLY models to render completed depth maps and normals. Example usage:
```
python render.py --data_dir <out_dir>
```

Rendered depth and normals are saved alongside the images:
```
<sceneid>/frame-XXXXXX.rendered_depth.png
<sceneid>/frame-XXXXXX.rendered_normal.png
```

Depth is in milimeters and normals are converted to be in range `[0,1]` with: `out_normal = (in_normal + 1) / 2.0`

## Authors
 * Jan Czarnowski
 * Ronald Clark
 * Tristan Laidlow
