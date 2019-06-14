#!/bin/bash

: ${python:=python} #python will take value "python" if not overriden

reader_dir=ScanNet/SensReader/c++
reader_exec="$reader_dir/sens"

# make a temporary file for logging
logfile=$(mktemp /tmp/download-sample-log.XXXXXXX)

die() { echo -e "\n$*" 1>&2 ; echo "See log for more details: $logfile" 1>&2 ; exit 1; }

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

  yes | $python download-scannet.py -o . --id ${_scene_id} --type .sens &>> $logfile || return

  # decompress .sens file
  sens_file="scans/${_scene_id}/${_scene_id}.sens"
  ${reader_exec} ${sens_file} "${_out_dir}/${_scene_id}" &>> $logfile || return
}

# Downloads model ply file for a given scene 'scene0425_00'
function download_scene_ply {
  _scene_id=$1
  _out_dir=$2
  yes | $python download-scannet.py -o .  --id ${_scene_id} --type _vh_clean_2.ply &>> $logfile || return

  # move the downloaded ply into proper scene directory
  mv "scans/${_scene_id}/${_scene_id}_vh_clean_2.ply" "${_out_dir}/${_scene_id}/" || return
}

# Ensure the reader is compiled
function compile_reader {
  if [[ ! -f $reader_exec ]]; then
    echo "Compiling the sens reader"
    make -C $reader_dir
  fi
}

if [[ ! -f "download-scannet.py" ]]; then
  echo "Please download download-scannet.py by following the instructions on the" \
  "dataset website (http://www.scan-net.org/ScanNet) and" \
  "place it alongside this script."
  exit 1
fi

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
  die "Sample file ${sample_file} does not exist"
fi

echo "Logging to: $logfile"

# ensure that sens reader is compiled
compile_reader || die "Failed to compile the sens reader"

# probe the input file for number of scenes
num_scenes=$(cat $1 | wc -l)

# create the output folder
mkdir -p ${out_dir} || die "Failed to create the output directory"

# download the data
echo "Downloading data for $num_scenes scenes"
i=0
while read scene; do
  progress_bar ${i} ${num_scenes}
  download_scene_images ${scene} ${out_dir} || die "Failed to download images for scene ${scene}"
  download_scene_ply ${scene} ${out_dir} || die "Failed to download model for scene ${scene}"

  # clear the downloaded files
  rm -rf scans

  i=$((i + 1))
done < $1
