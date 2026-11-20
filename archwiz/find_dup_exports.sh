#!/bin/bash
dir1="$1"
dir2="$2"
if [ ! -d "$dir1" ] || [ ! -d "$dir2" ]; then
  echo "Usage: find_dup_exports.sh <dir1> <dir2>"
  exit 1
fi
# Compute hashes for dir1
find "$dir1" -type f -exec md5sum {} \; | sort > /tmp/dup1.txt
# Compute hashes for dir2
find "$dir2" -type f -exec md5sum {} \; | sort > /tmp/dup2.txt
# Join on hash
join -j 1 /tmp/dup1.txt /tmp/dup2.txt | while read -r hash file1 file2; do
  echo "MATCH: $hash"
  echo "  $file1"
  echo "  $file2"
done
