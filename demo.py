#!/usr/bin/env python

from epd import *
from time import sleep
import sys


# draw lines
def lines():
    for y in [y for y in range(0,601,100)]:
        if y==0:
            y = 1
        epd_line(0,y-1,799,y-1)
    for x in [x for x in range(0,801,100)]:
        if x==0:
            x = 1
        epd_line(x-1,0,x-1,599)
    epd_update()

# draw circles
def circles():
    for x in [x for x in range(50,751,100)]:
        epd_circle(x-1,49,40)
    epd_update()

# draw filled circles
def filled_circles():
    for x in [x for x in range(50,751,100)]:
        epd_fill_circle(x-1,149,40)
    epd_update()

# draw rectangles
def rectangles():
    for x in [x for x in range(10,790,100)]:
        epd_rect(x-1,210,x-1+80,290)
    epd_update()

# draw filled rectangles
def filled_rectangles():
    for x in [x for x in range(10,790,100)]:
        epd_fill_rect(x-1,310,x-1+80,390)
    epd_update()

# draw triangles
def triangles():
    for x in [x for x in range(50,751,100)]:
        epd_triangle(x-1,410,x-1-40,490,x-1+40,490)
    epd_update()

# draw filled triangles
def filled_triangles():
    for x in [x for x in range(50,751,100)]:
        epd_fill_triangle(x-1,510,x-1-40,590,x-1+40,590)
    epd_update()

# draw single pixels
def pixels():
    for p in [(x,y) for x in range(50,751,100) for y in range(448,466,3)]:
        epd_pixel(p[0]-1,p[1]-1)
    epd_update()

# display ascii strings
def english():
    for x in [x for x in range(25,790,100)]:
        epd_ascii(x-1, 30, 'ABC')
    epd_update()

# display Chinese in GB2312 encoding (2 bytes)
def chinese():
    for x in [x for x in range(20,790,100)]:
        epd_chinese(x-1, 215, "C4E3 BAC3")
        epd_chinese(x-1, 250, "CAC0 BDE7")
    epd_update()

# display blocks of long texts
def english_block():
    txt = "The quick brown fox jumps over the lazy dog. "
    wrap_ascii(0,0,txt*6)
    epd_update()
    sleep(0.5)
    wrap_ascii(50,250,txt*6,limit=400)
    epd_update()
    sleep(0.5)
    wrap_ascii(350,150,txt*6,limit=350)
    epd_update()


if __name__=="__main__":
    try:
        epd_connect()
    except:
        sys.exit()

    epd_clear()

    # need some reaction time between each set of drawing commands
    # this may be something to do with the instruction buffer of the epd
    
    # another known issue is if hundreds of draw pixel commands are
    # sent over before calling an update (e.g. in a 2-D loop), the module
    # and in my case, all my USB ports IO are frozen. I lose USB mouse and
    # keyboard. Have to restart the computer to get things working again.

    lines()
    sleep(0.5)
    circles()
    sleep(0.5)
    filled_circles()
    sleep(0.5)
    rectangles()
    sleep(0.5)
    filled_rectangles()
    sleep(0.5)
    triangles()
    sleep(0.5)
    filled_triangles()
    sleep(0.5)
    pixels()
    sleep(0.5)
    epd_set_en_font(ASCII32)
    english()
    sleep(0.5)
    chinese()
    sleep(0.5)
    english_block()
    sleep(0.5)
    epd_bitmap(100,0,"FACE.BMP")
    epd_set_en_font(ASCII48)
    epd_ascii(0,540,"http://github.com/yy502/ePaperDisplay")
    epd_update()

    epd_disconnect()