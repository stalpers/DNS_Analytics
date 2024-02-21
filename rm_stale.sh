#!/bin/bash
# This script takes a file as input which contains filenames - one per line
# The script will remove the files

# Check if the input file is provided and exists
if [ $# -eq 0 ]; then
  echo "Please provide an input file"
  exit 1
fi

input_file=$1

if [ ! -f "$input_file" ]; then
  echo "Input file does not exist"
  exit 2
fi

# Loop through each line of the input file and remove the file
while read -r line; do
  # Check if the file is writeable
  if [ -w "$line" ]; then
    echo "[INFO] Removing <$line>"
    rm -f "$line"
  else
    echo "[ERR ] File <$line> is not writeable"
  fi
done < "$input_file"

