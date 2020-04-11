# scannet_toolkit



Scripts for downloading a smaller random sample of the [ScanNet](http://www.scan-net.org/ScanNet/) dataset 
and generating depth maps from the PLY models of the scenes.

## Important notes

 * PyGLer encodes missing values as having 1m depth (it's a byproduct of setting the clear color to 1). We fix that only in the merge script. Watch out for that

## Installation
Clone the repo recursively:

```
git clone --recurse-submodules https://github.com/jczarnowski/scannet_toolkit.git
```

Obtain the `download-scannet.py` by requesting access to the dataset and following the instructions from [the authors' website](https://github.com/ScanNet/ScanNet#scannet-data). Place this script in the root directory of this repository.

## Usage

We used this repo for sampling a subset of the ScanNet dataset and preprocess it in the following way:
  1) Create random samples for train and val with `sample.sh`
  2) Download both samples with `download_sample.sh`
  3) Preprocess all RGB images to the same size as the depth (640x480). We had to do this as the colour image sizes are inconsistent accross the dataset and our preprocessing code requires that
  4) Render depth using the supplied PLY scene models and ground truth poses with `render.py`. This gives us a nice smooth model to fill the gaps in original depth maps
  5) Merge the original depth maps with the rendered ones using `merge_depths.py`. Thanks to this step, we fill the gaps in the depth maps with the model and model gaps with raw data.


#### Sampling
First, generate a random sample of scenes using `sample.sh`. To generate a 40% sample of the ScanNet training set:
```
bash sample.sh 40 samples/scannetv2_train.txt > samples/my_40_sample.txt
```
Files `samples/scannetv2_train.txt` and `samples/scannetv2_val.txt` contain the scene names for the official ScanNet test/train split.

If you are sampling from the same file, you should also make sure that your generated train/test split is exclusive. This can be quickly done with e.g. grep:
```
grep -Fxf file1 file2
```

#### Downloading

Download your sample using `download_sample.sh` to a directory `out_dir` as follows:
```
bash download_sample.sh samples/my_40_sample.txt <out_dir>
```
The script currently only pulls and decodes the `.sens` files and the `_vh_clean_2.ply` models.

#### Preprocessing colour images
The `preprocess.py` script is a WIP and resizes the images to 640x480.

#### Rendering depth from models
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

#### Merging rendered and raw depth
The `merge_depths.py` script reads in the rendered and the raw depth maps and combines them together into a single image and saves it alongside:
```
<sceneid>/frame-XXXXXX.rendered_depth.png
<sceneid>/frame-XXXXXX.rendered_normal.png
<sceneid>/frame-XXXXXX.merged_depth.png
```

Example usage:
```
python merge_depths.py --data_dir <out_dir>
```

## Authors
 * Jan Czarnowski
 * Ronald Clark
 * Tristan Laidlow
