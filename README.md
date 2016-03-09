# 4.3 inch e-Paper Display

Scripts to display vector shapes, BMP images and texts on [WaveShare 4.3 inch e-paper display module](http://www.waveshare.com/wiki/4.3inch_e-Paper) via command-line instead of the Windows-only tools provided by the manufacture.

`epd.py` is based on the Arduino/C++ library provided by the manufacture.

`4_level_gray_4bpp_BMP_converter.py` is the solution to my question on [StackExchange](http://stackoverflow.com/a/35834109/3349573) about converting images for the e-paper display. It relies on imagemagick for preprocessing the pixels and pipe into the converter as input.

Execute `./convert_to_grayscale.sh <source_image>` to convert the source image to BMP format. 

The outcome is a BMP image with the following attributes:
* indexed colours - 00000000/55555500/AAAAAA00/FFFFFF00
* 2bbp grayscale - i.e. 00/01/10/11, but
* 4bpp little-endian per pixel - i.e. 0000/0100/1000/1100
* each row of pixels is aligned to 4 bytes or 8 pixels

## Notes on File Management

The manuafacture's manual isn't very clear about this. I consulted their technical support regarding how to remove the preloaded files, but the answer he gave some isn't the fact by my experiments. So here's my conclusion:

* The 128MB internal storage is partitioned into 48MB for fonts and 80MB for images (according to the manual, unverified)
* When calling the import functions (one for fonts and one for images), the relavant internal partition gets cleared and the fonts or images in the *root* directory of the SD card are copied over.
* Valid fonts or images are determined by the file names:
* * `GBK32.FON`,`GBK32.FON` and `GBK32.FON` for fonts
* * capital letters and digits followed by `.BMP` for images. Note that the totol length of file names must be no more than 10 chracters including `.BMP`.
* If no valid font or image is found on SD card, the import functions will just clear the relavant internal storage.

