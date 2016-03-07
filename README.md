# ePaperDisplay
Scripts to display vector shapes, BMP images and texts on [WaveShare 4.3 inch e-paper display module](http://www.waveshare.com/wiki/4.3inch_e-Paper) via command-line instead of the Windows-only tools provided by the manufacture.

`epd.py` is based on the Arduino/C++ library provided by the manufacture.

`4_level_gray_4bpp_BMP_converter.py` is the solution to my question on [StackExchange](http://stackoverflow.com/a/35834109/3349573) about converting images for the e-paper display. It depends on imagemagick for preprocessing the pixels and pipe into my converter as the following:
```Bash
convert in.png +matte -colors 4 -depth 8 -colorspace gray pgm:- | ./4_level_gray_4bpp_BMP_converter.py > out.bmp
```
