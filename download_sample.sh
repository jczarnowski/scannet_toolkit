#!/bin/bash

reader_dir=ScanNet/SensReader/c++
reader_exec="$reader_dir/sens"

# Progress bar printing snagged from
# https://github.com/fearside/ProgressBar
function progress_bar {
  let _progress=(${1}*100/${2}*100)/100
  let _done=(${_progress}*4)/10
  let _left=40-$_done
  _fill=$(printf "%${_done}s")
  _empty=$(printf "%${_left}s")
  printf "\rProgress : [${_fill// /\#}${_empty// /-}] ${_progress}%%"
}

# Downloads and uncompresses the .sens file given a scene id
# e.g. 'scene0425_00'
function download_scene_images {
  _scene_id=$1
  _out_dir=$2

  python download-scannet.py -o . --id ${_scene_id} --type .sens &> /dev/null

  # decompress .sens file
  sens_file="scans/${_scene_id}/${_scene_id}.sens"
  ${reader_exec} ${sens_file} "${_out_dir}/${_scene_id}" &> /dev/null
}

# Downloads model ply file for a given scene 'scene0425_00'
function download_scene_ply {
  _scene_id=$1
  _out_dir=$2
  python download-scannet.py -o .  --id ${_scene_id} --type _vh_clean_2.ply &> /dev/null

  # move the downloaded ply into proper scene directory
  mv "scans/${_scene_id}/${_scene_id}_vh_clean_2.ply" "${_out_dir}/${_scene_id}/"
}

# Ensure the reader is compiled
function compile_reader {
  if [[ ! -f $reader_exec ]]; then
    echo "Compiling the sens reader"
    make -C $reader_dir
  fi
}

# check command line args
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <sample_file> <out_dir>"
  exit
fi

# parse args
sample_file=$1
out_dir=$2

# validate args
if [[ ! -f $sample_file ]]; then
  echo "Sample file ${sample_file} does not exist"
  exit -1
fi

# ensure that sens reader is compiled
compile_reader || exit

# probe the input file for number of scenes
num_scenes=$(cat $1 | wc -l)

# create the output folder
mkdir -p ${out_dir} || exit

# download the data
echo "Downloading data for $num_scenes scenes"
i=0
while read scene; do
  progress_bar ${i} ${num_scenes}
  download_scene_images ${scene} ${out_dir} || exit
  download_scene_ply ${scene} ${out_dir} || exit

  # clear the downloaded files
  rm -rf scans

  i=$((i + 1))
done < $1
