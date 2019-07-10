#!/bin/bash

dir=$1

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 data_dir"
  exit
fi

for seqdir in $dir/*/; do
  echo "Processing $seqdir"
  ls $seqdir | grep jpg | sort > $seqdir/frames.txt
done
