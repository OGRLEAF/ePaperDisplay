# 4.3 inch e-Paper Display

Scripts to display vector shapes, BMP images and texts on [WaveShare 4.3 inch e-paper display module](http://www.waveshare.com/wiki/4.3inch_e-Paper) via command-line instead of the Windows-only tools provided by the manufacture.

`epd.py` is based on the Arduino/C++ library provided by the manufacture.

`4_level_gray_4bpp_BMP_converter.py` is the solution to my question on [StackExchange](http://stackoverflow.com/a/35834109/3349573) about converting images for the e-paper display. It relies on imagemagick for preprocessing the pixels and pipe into the converter as input.

Execute `./convert_to_grayscale.sh <source_image>` to convert the source image to BMP format. 

The outcome is a BMP image with the following attributes:
* indexed colours - `00 00 00 00`/`55 55 55 00`/`AA AA AA 00`/`FF FF FF 00`
* 2bbp grayscale - i.e. `00`/`01`/`10`/`11`, but
* 4bpp little-endian per pixel - i.e. `00 00`/`01 00`/`10 00`/`11 00`
* each row of pixels is aligned to 4 bytes or 8 pixels

## Interact With the e-Paper Display

```Python
>>> from epd import *
>>> help()              # prints help message which details all available functions
...
>>> epd_connect()       # must initiate a connection first, and then send commands to EPD
> EPD connected
> EPD handshake
...                     # whatever you want to do with EPD
>>> epd_disconnect()    # a clean finish after use
```

## Enabling WiFi Communication

The original e-paper display does not have WiFi support. I added an ESP8266 module to it as a TCP-serial relay and it works pretty well. `epd_connect()` will try TCP connection first, else falls back to serial port. All function calls are the same for TCP or serial connection, except I have not implemented read-reply via TCP. i.e. no VERBOSE mode for TCP/IP connection.

The baud rate should not be changed while connected via TCP/IP, as the WiFi module defaults to 115200 bps which does not change with the e-paper display.

In `wifi-relay` folder you will find the firmware and scripts to be deployed onto the ESP8266 WiFi module.

* `init.lua` - lua script to set up the WiFi module in both AP (access point) and station (client) mode, with `AP_SSID` and `AP_PASSWORD`of your choice. So that when the EPD is not near home router, you can connect directly to it. e.g. control the EPD via smartphone in a car (TESTED!). `SSID` and `PASSWORD` are obviously for connecting to your home router, so change them before uploading.
* `nodemcu-master-10-modules-2016-01-22-12-53-39-float.bin` NodeMCU firmware with a number of commonly used libraries built-in. You can build your own from [NodeMCU custom builds](https://nodemcu-build.com/) or use mine. In this case, we are not using any sensors or fancy functions, so selecting the default modules will do.

### Enabling ESP8266

`ESP8266 module does not work with 5V.`

I suggest you get a cheap USB serial adapter from ebay, which supports 3.3V power output.

You will need to connect a 4.7k or 10k Ohm resistor across `VCC` and `CH_PD` to enable the module (in other words, to make it run). I have soldered a resistor in-place permanently.

### Flashing Firmware

1. Power off the module
2. Connect `GPIO0` and `GND`
3. Power on

Now it is in `flash mode` and will take new firmware. You can now disconnect `GPIO0` and `GND`.

[esptool.py](https://github.com/espressif/esptool/blob/master/esptool.py) is the simplest and best tool I could find to flash firmware into ESP8266. It's up to you to download that single file script, and execute as below:

    python esptool.py --port /dev/tty<YOUR_SERIAL_INTERFACE> write_flash 0x00000 nodemcu-master-10-modules-2016-01-22-12-53-39-float.bin

Note that NodeMCU default baud rate is `9600 bps`.

### Uploading Lua Script

I use [ESPlorer](https://esp8266.ru/esplorer/) to connect and upload lua scripts to ESP8266. It's up to you to download and run it. Again, the initial baud rate is 9600. Once you upload `init.lua` and restart the ESP8266 WiFi module, it will use `115200 bps` as specified in `init.lua`.

Do not change this rate, because it is the default baud rate of the EPD. Or they won't talk to each other.

### Wiring Up

**Power Supply**

ESP8266 can only tolerate up to 3.6V, and the EPD can work with minimal voltage of 3.3V. So I used a DC-DC step down module to convert 5V from USB to 3.3V for both ESP8266 module and the EPD. It is basically one AMS1117 3.3v regulator with a few capacitors to smooth the voltage output. You can use 2x AA batteries or other means of power supply as long as you don't burn your ESP8266 module!

**Serial Pins**

This is intuitive - connect RX and TX on the EPD to TX and RX on the WiFi module, so one end transmits and the other end receives. The EPD and WiFi module should use the same power supply so we don't need to worry about different voltages in transmitting/receiving.

                                                                +-----------------------------------------------+
                                                                |                                               |
    +-----------------------------------------------------+     |                                               |
    |                                                     |     |                                               |
    |                                                     |     |  +--------------------+                       |
    |                                                  V+ +-----+--+                 V+ +----------+            |
    |                                                     |        |   3.3V Regulator   |            5V USB     |
    |                                                  V- +-----+--+                 V- +----------+            |
    |                                                     |     |  +--------------------+                       |
    |                                                     |     |                                               |
    |                        EPD                          |     |                                               |
    |                                                     |     +-------------------------+                     |
    |                                                     |                               |                     |
    |                                                     |           +---------------+   |                     |
    |                                                  RX +-----------+TX          GND+---+                     |
    |                                                     |           |    ESP8266    |                         |
    |                                                  TX +-----------+RX          VCC+-------------------------+
    |                                                     |           +---------------+
    +-----------------------------------------------------+



## Notes on File Management

The manufacture's manual isn't very clear about this. I consulted their technical support regarding how to remove the preloaded files, but the answer he gave some isn't the fact by my experiments. So here's my conclusion:

* The 128MB internal storage is partitioned into 48MB for fonts and 80MB for images (according to the manual, unverified)
* When calling the import functions (one for fonts and one for images), the relevant internal partition gets CLEARED and the fonts or images in the *root* directory of the SD card are copied over.
* Valid fonts or images are determined by the file names:
  * `GBK32.FON`,`GBK48.FON` and `GBK64.FON` for fonts
  * capital letters and digits followed by `.BMP` for images. Note that the total length of file names must be no more than 10 chracters including `.BMP`.
* If no valid font or image is found on SD card, the import functions will just clear the relevant internal storage.
```Python
# Example: to import images
# insert SD card
> epd_set_memory_sd()
> epd_import_pic()
> epd_set_memory_nand()
# remove SD card
```

## Error Codes

```
0       Invalid command
1       SD card initiation failed
2       Invalid arguments
3       SD card not inserted
4       File not found
20      Validation failed
21      Invalid frame
250     Undefined error
```