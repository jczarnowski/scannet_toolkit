#!/bin/bash

SENS_PROG=/home/jancz/dev/co/ScanNet/SensReader/c++/sens 
OUT_DIR=$2

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <sample_file> out_dir"
  exit
fi

# Downloads and uncompresses the .sens file given a scene id
# e.g. 'scene0425_00'
function download_scene_images {
  scene_id=$1

  python download-scannet.py -o . --id $scene_id --type .sens || exit

  # decompress .sens file
  sens_file="scans/$line/$line.sens"
  $SENS_PROG $sens_file "$OUT_DIR/$line" || exit

  # remove .sens file
  rm -rf "$sens_file"
}

function download_scene_ply {
  scene_id=$1
  python download-scannet.py -o $OUT_DIR/$scene_id --id $scene_id --type _vh_clean_2.ply || exit
}

while read scene; do
  echo "Downloading data for scene $scene"

  #download_scene_images $scene
  download_scene_ply $scene

done < $1
