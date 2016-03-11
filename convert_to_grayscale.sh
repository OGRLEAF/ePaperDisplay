#!/bin/bash

if [ -z "$1" ] ; then
    echo -n "No input file"
    echo ""
    exit
else
    IN=$1
fi

# "-colors n" seems funny with grayscale
# it produces n-1 grays most of the times
# but occasionally it does produce n grays
# here's a workaround to try to get it to 4 grays

for COUNT in {4..6}
do
    TEST=`convert $IN -resize '800x600>' -colorspace gray +matte -colors $COUNT -depth 2 -define histogram:unique-colors=true -format %c histogram:info:- | wc -l`
    if [ $TEST -eq 4 ] || [ $COUNT -eq 6 ] ; then
        convert $IN -resize '800x600>' -colorspace gray +matte -colors $COUNT -depth 2 pgm:- | ./4_level_gray_4bpp_BMP_converter.py > $IN.BMP
        echo "$IN.BMP contains $TEST colours with '-colors $COUNT' flag"
        break
    fi
done
