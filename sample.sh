#!/bin/bash

percent=$1
file=$2

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <percent_sample> <seq_file>"
  exit
fi

num_scans=$(cat "$file" | wc -l)

# calculate number of things to 
num=$(echo "$percent * 0.01 * $num_scans" | bc)
num=${num%%.*}

cat $file | sort -R | head -n $num
