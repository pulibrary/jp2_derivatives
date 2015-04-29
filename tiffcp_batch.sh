#!/bin/bash
TIFFCP=/usr/bin/tiffcp
DIR=$1

for tiff in $(find $DIR -name "*.tif" ! -name ".*"); do
  tmp_name=$tiff.tmp
  bak_name=$tiff.bak
  $TIFFCP $tiff $tmp_name
	if [ $? == 0 ]; then
    mv $tiff $bak_name
    mv $tmp_name $tiff
  else
    echo "There was a problem with $tiff"
  fi
done