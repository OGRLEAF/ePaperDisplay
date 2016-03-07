#!/bin/bash

if [ -z "$1" ] ; then
    echo -n "No input file"
    echo ""
    exit
else
    IN=$1
fi

convert $IN -colorspace gray +matte -colors 4 -depth 2 -resize '800x600>' pgm:- | ./4_level_gray_4bpp_BMP_converter.py > $IN.bmp
