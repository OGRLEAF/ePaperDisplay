import os
import socket
from time import sleep
from platform import system

VERBOSE = False
LAN = "192.168.0.22" # EPD's home IP
AP = "192.168.1.1"   # EPD's own AP IP
PORT = 3333
MAC = "/dev/cu.usbserial"
LINUX = "/dev/ttyUSB0"
DEV = ""

if system()=='Linux':
    DEV = LINUX
elif system()=='Darwin':
    DEV = MAC
else:
    DEV = raw_input('Define serial port for EPD connection (e.g. /dev/ttyUSB1 or just hit enter for none): ')

soc                 = None
BAUD_RATE           = 115200
BAUD_RATE_DEFAULT   = 115200
BAUD_RATES          = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
MAX_STRING_LEN      = 1024 - 4

# frame segments
FRAME_BEGIN         = "A5"
FRAME_END           = "CC33C33C"

# colours
BLACK               = "00"
DARK_GRAY           = "01"
GRAY                = "02"
WHITE               = "03"

# commands
CMD_HANDSHAKE       = "00"  # handshake
CMD_SET_BAUD        = "01"  # set baud
CMD_READ_BAUD       = "02"  # read baud
CMD_MEMORYMODE      = "07"  # set memory mode
CMD_STOPMODE        = "08"  # enter stop mode 
CMD_UPDATE          = "0A"  # update
CMD_SCREEN_ROTATION = "0D"  # set screen rotation
CMD_LOAD_FONT       = "0E"  # copy font files from SD card to NandFlash.
                            # Font files include GBK32/48/64.FON
                            # 48MB allocated in NandFlash for fonts
                            # LED will flicker 3 times when starts and ends.
CMD_LOAD_PIC        = "0F"  # Import the image files from SD card to the NandFlash.
                            # LED will flicker 3 times when starts and ends.
                            # 80MB allocated in NandFlash for images
CMD_SET_COLOR       = "10"  # set colour
CMD_SET_EN_FONT     = "1E"  # set English font
CMD_SET_CH_FONT     = "1F"  # set Chinese font

CMD_DRAW_PIXEL      = "20"  # set pixel
CMD_DRAW_LINE       = "22"  # draw line
CMD_FILL_RECT       = "24"  # fill rectangle
CMD_DRAW_RECT       = "25"  # draw rectangle
CMD_DRAW_CIRCLE     = "26"  # draw circle
CMD_FILL_CIRCLE     = "27"  # fill circle
CMD_DRAW_TRIANGLE   = "28"  # draw triangle
CMD_FILL_TRIANGLE   = "29"  # fill triangle
CMD_CLEAR           = "2E"  # clear screen use back colour
CMD_DRAW_STRING     = "30"  # draw string
CMD_DRAW_BITMAP     = "70"  # draw bitmap


# FONT SIZE (32/48/64 dots)
GBK32               = "01"
GBK48               = "02"
GBK64               = "03"
    
ASCII32             = "01"
ASCII48             = "02"
ASCII64             = "03"


# Memory Mode
MEM_NAND            = "00"
MEM_SD              = "01"


# set screen rotation
EPD_NORMAL          = "00"     #screen normal
EPD_INVERSION       = "01"     #screen inversion      


# command define
_cmd_handshake   = FRAME_BEGIN+"0009"+CMD_HANDSHAKE+FRAME_END
_cmd_read_baud   = FRAME_BEGIN+"0009"+CMD_READ_BAUD+FRAME_END
_cmd_stopmode    = FRAME_BEGIN+"0009"+CMD_STOPMODE+FRAME_END
_cmd_update      = FRAME_BEGIN+"0009"+CMD_UPDATE+FRAME_END
_cmd_clear       = FRAME_BEGIN+"0009"+CMD_CLEAR+FRAME_END
_cmd_import_font = FRAME_BEGIN+"0009"+CMD_LOAD_FONT+FRAME_END
_cmd_import_pic  = FRAME_BEGIN+"0009"+CMD_LOAD_PIC+FRAME_END
_cmd_use_nand    = FRAME_BEGIN+"000A"+CMD_MEMORYMODE+MEM_NAND+FRAME_END
_cmd_use_sd      = FRAME_BEGIN+"000A"+CMD_MEMORYMODE+MEM_SD+FRAME_END


# ASCII string to Hex string. e.g. "World" => "576F726C64"
def A2H(string):
    hex_str = ""
    for c in string:
        hex_str = hex_str+hex(ord(c))[-2:]
    return hex_str+"00" # append "00" to string as required


# hex string to bytes with parity byte at the end
def H2B(hexStr):
    bytes = []
    parity = 0x00
    hexStr = hexStr.replace(" ",'')
    for i in range(0, len(hexStr), 2):
        byte = int(hexStr[i:i+2],16)
        bytes.append(chr(byte))
        parity = parity ^ byte
    bytes.append(chr(parity))
    return ''.join(bytes)


def send(cmd):
    if type(soc) == socket._socketobject:
        soc.send(H2B(cmd))
    else:
        soc.write(H2B(cmd))
        if VERBOSE:
            print ">",soc.readline()


def epd_connect():
    global soc
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.settimeout(1)
    for ip in [LAN, AP]:
        try:
            soc.connect((LAN, PORT))
            print "> EPD connected at %s:%s" % (ip, PORT)
            break
        except:
            print ">> EPD not found at %s:%s" % (ip, PORT)
    else:
        if os.path.exists(DEV):
            import serial
            try:
                soc = serial.Serial(
                    port=DEV,
                    baudrate=BAUD_RATE,
                    timeout=1
                )
                print "> EPD connected via serial port"
                return
            except:
                print ">> Unable to connect to USB serial port", DEV
        else:
            print ">> Serial port unavailable",DEV


def epd_verbose(v):
    global VERBOSE
    if v:
        VERBOSE = True
    else:
        VERBOSE = False


def epd_handshake():
    print "> EPD handshake"
    send(_cmd_handshake)


def epd_disconnect():
    global soc
    soc.close()
    print "> EPD connection closed."


def epd_update():
    send(_cmd_update)


def epd_clear():
    send(_cmd_clear)
    epd_update()


def reset_baud_rate():
    BAUD_RATE = BAUD_RATE_DEFAULT


def epd_set_baud(baud_rate): # 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200
    global BAUD_RATE
    if baud_rate in BAUD_RATES:
        BAUD_RATE = baud_rate
        hex_rate=('0000000'+hex(baud_rate)[2:])[-8:]
        _cmd = FRAME_BEGIN+"000D"+CMD_SET_BAUD+hex_rate+FRAME_END;
        send(_cmd)
        epd_disconnect()
        sleep(10)
        epd_connect()
    else:
        print "> Invalid baud rate. Pick from 75, 110, 300, 1200, 2400, 4800, 9600, 19200, 38400, 57600 and 115200 (default)"


def epd_read_baud():
    print "> EPD baud rate:"
    send(_cmd_read_baud)


def epd_set_memory_nand():
    send(_cmd_use_nand)

def epd_set_memory_sd():
    send(_cmd_use_sd)


def epd_halt():
    print "> EPD halt"
    send(_cmd_stopmode)


def epd_screen_normal():
    _cmd = FRAME_BEGIN+"000A"+CMD_SCREEN_ROTATION+EPD_NORMAL+FRAME_END
    send(_cmd)
    epd_update()

def epd_screen_invert():
    _cmd = FRAME_BEGIN+"000A"+CMD_SCREEN_ROTATION+EPD_INVERSION+FRAME_END
    send(_cmd)
    epd_update()


def epd_import_font():
    send(_cmd_import_font)


def epd_import_pic():
    send(_cmd_import_pic)


def epd_set_color(fg, bg):
    if fg in [BLACK, DARK_GRAY, GRAY, WHITE] and bg in [BLACK, DARK_GRAY, GRAY, WHITE]:
        _cmd = FRAME_BEGIN+"000B"+CMD_SET_COLOR+fg+bg+FRAME_END
        send(_cmd)


def epd_set_en_font(en_size):
    _cmd = FRAME_BEGIN+"000A"+CMD_SET_EN_FONT+en_size+FRAME_END
    send(_cmd)


def epd_set_ch_font(ch_size):
    _cmd = FRAME_BEGIN+"000A"+CMD_SET_CH_FONT+ch_size+FRAME_END
    send(_cmd)


def epd_pixel(x0, y0):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    _cmd = FRAME_BEGIN+"000D"+CMD_DRAW_PIXEL+hex_x0+hex_y0+FRAME_END
    send(_cmd)


def epd_line(x0, y0, x1, y1):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0011"+CMD_DRAW_LINE+hex_x0+hex_y0+hex_x1+hex_y1+FRAME_END
    send(_cmd)


def epd_rect(x0, y0, x1, y1):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0011"+CMD_DRAW_RECT+hex_x0+hex_y0+hex_x1+hex_y1+FRAME_END
    send(_cmd)


def epd_fill_rect(x0, y0, x1, y1):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0011"+CMD_FILL_RECT+hex_x0+hex_y0+hex_x1+hex_y1+FRAME_END
    send(_cmd)


def epd_circle(x0, y0, r):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_r = ("000"+hex(r)[2:])[-4:]
    _cmd = FRAME_BEGIN+"000F"+CMD_DRAW_CIRCLE+hex_x0+hex_y0+hex_r+FRAME_END
    send(_cmd)


def epd_fill_circle(x0, y0, r):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_r = ("000"+hex(r)[2:])[-4:]   
    _cmd = FRAME_BEGIN+"000F"+CMD_FILL_CIRCLE+hex_x0+hex_y0+hex_r+FRAME_END
    send(_cmd)


def epd_triangle(x0, y0, x1, y1, x2, y2):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    hex_x2 = ("000"+hex(x2)[2:])[-4:]
    hex_y2 = ("000"+hex(y2)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0015"+CMD_DRAW_TRIANGLE+hex_x0+hex_y0+hex_x1+hex_y1+hex_x2+hex_y2+FRAME_END
    send(_cmd)


def epd_fill_triangle(x0, y0, x1, y1, x2, y2):
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    hex_x2 = ("000"+hex(x2)[2:])[-4:]
    hex_y2 = ("000"+hex(y2)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0015"+CMD_FILL_TRIANGLE+hex_x0+hex_y0+hex_x1+hex_y1+hex_x2+hex_y2+FRAME_END
    send(_cmd)


def epd_ascii(x0, y0, txt):
    if len(txt) <= MAX_STRING_LEN:
        hex_x0 = ("000"+hex(x0)[2:])[-4:]
        hex_y0 = ("000"+hex(y0)[2:])[-4:]
        hex_txt = A2H(txt)
        hex_size = ("000"+hex(13+len(hex_txt)/2)[2:])[-4:]
        _cmd = FRAME_BEGIN+hex_size+CMD_DRAW_STRING+hex_x0+hex_y0+hex_txt+FRAME_END
        send(_cmd)
    else:
        print "> Too many characters. Max length =",MAX_STRING_LEN


def epd_chinese(x0, y0, gb2312_hex): # "hello world" in Chinese: C4E3 BAC3 CAC0 BDE7
    gb2312_hex = gb2312_hex.replace(" ","")+"00"
    if len(gb2312_hex)/2 <= MAX_STRING_LEN:
        hex_x0 = ("000"+hex(x0)[2:])[-4:]
        hex_y0 = ("000"+hex(y0)[2:])[-4:]
        hex_size = ("000"+hex(13+len(gb2312_hex)/2)[2:])[-4:]
        _cmd = FRAME_BEGIN+hex_size+CMD_DRAW_STRING+hex_x0+hex_y0+gb2312_hex+FRAME_END
        send(_cmd)
    else:
        print "> Too many characters. Max length =",MAX_STRING_LEN


def epd_bitmap(x0, y0, name): # file names must be all capitals and <10 letters including '.'
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_name = A2H(name)
    hex_size = ("000"+hex(13+len(hex_name)/2)[2:])[-4:]
    _cmd = FRAME_BEGIN+hex_size+CMD_DRAW_BITMAP+hex_x0+hex_y0+hex_name+FRAME_END
    send(_cmd)


def get_width(txt,size=32): # size in [32,48,64]
                            # characters in size 32 are manually measured so their
                            # widths are accurate. font size 48 and 64 are assumed
                            # widths based on simple calculation for rough estimates.
    if not size in [32, 48, 64]:
        print "> Error: size must be in [32,48,64]"
        return
    width = 0
    for c in txt:
        if c in "'":
            width += 5
        elif c in "ijl|":
            width += 6
        elif c in "f":
            width += 7
        elif c in " It![].,;:/\\":
            width += 8
        elif c in "r-`(){}":
            width += 9
        elif c in '"':
            width += 10
        elif c in "*":
            width += 11
        elif c in "x^":
            width += 12
        elif c in "Jvz":
            width += 13
        elif c in "cksy":
            width += 14
        elif c in "Labdeghnopqu$#?_1234567890":
            width += 15
        elif c in "T+<>=~":
            width += 16
        elif c in "FPVXZ":
            width += 17
        elif c in "ABEKSY&":
            width += 18
        elif c in "HNUw":
            width += 19
        elif c in "CDR":
            width += 20
        elif c in "GOQ":
            width += 21
        elif c in "m":
            width += 22
        elif c in "M":
            width += 23
        elif c in "%":
            width += 24
        elif c in "@":
            width += 27
        elif c in "W":
            width += 28
        else: # non-ascii or Chinese character
            width += 32
    return int(width * (size/32.0))


def wrap_ascii(x,y,txt,limit=800,size=32): # does not work well with size 48 or 64
    DELIMITER = " "
    DELIMITER_WIDTH = get_width(DELIMITER,size)
    WHITE_WIDTH = get_width(" ",size)
    lines = txt.strip().split("\n")
    y_offset = 0
    for l in lines:
        words = l.strip().split(DELIMITER)
        line = ""
        line_width = 0
        for word in words:
            word_width = get_width(word,size)
            if line_width+DELIMITER_WIDTH+word_width <= limit:
                line += DELIMITER + word
                line_width += DELIMITER_WIDTH + word_width
            else:
                # clear line up to the whole line width
                epd_set_color(WHITE,WHITE)
                epd_fill_rect(x,y+y_offset,x+limit,y+y_offset+size)
                epd_set_color(BLACK,WHITE)
                epd_ascii(x,y+y_offset,line.strip(DELIMITER))
                y_offset += size
                line = word
                line_width = word_width
        if line != "":
            # clear line up to the whole line width
            epd_set_color(WHITE,WHITE)
            epd_fill_rect(x,y+y_offset,x+limit,y+y_offset+size)
            epd_set_color(BLACK,WHITE)
            epd_ascii(x,y+y_offset,line.strip(DELIMITER))
            y_offset += size


def help(): # list all available functions
    print """\
epd_connect()                           # opens a connection to EPD (TCP/IP or USB serial)
epd_handshake()                         # check if EPD is ready via serial connection
epd_disconnect()                        # close serial connection to EPD
epd_verbose(True|False)                 # enable/disable(default) verbose serial communication (SLOW!)
epd_halt()                              # put EPD to sleep. to wake up pin by physical pin only

epd_read_baud()                         # read EPD serial connection baud rate
epd_set_baud(int)                       # set EPD serial baud rate & restart & reconnect

epd_set_memory_nand()                   # use internal memory (default)
epd_set_memory_sd()                     # use SD card

epd_import_font()                       # copy font files form SD card to internal memory
epd_import_pic()                        # copy images from SD card to internal memory

epd_set_color(foreground,background)    # set colours from BLACK|DARK_GRAY|GRAY|WHITE

epd_set_ch_font(GBK32|GBK48|GBK64)      # set Chinese font size
epd_set_en_font(ASCII32|ASCII48|ASCII64)# set ASCII font size

epd_screen_normal()                     # flip EPD screen back to normal
epd_screen_invert()                     # flip EPD screen 180 degrees
epd_clear()                             # clear display
epd_update()                            # update screen with buffered commands

epd_ascii(x,y,"ascii string")           # display ascii string
epd_chinese(x,y,"hex code of Chinese")  # display Chinese string

wrap_ascii(x,y,txt,limit=800,size=32)   # auto-wraps a paragraph of ascii texts and displays
                                        # from origin x,y with optional width limit and font size

epd_pixel(x,y)                          # draw a pixel
epd_line(x0,y0,x1,y1)                   # draw a line
epd_rect(x0,y0,x1,y1)                   # draw a rectangle
epd_fill_rect(x0,y0,x1,y1)              # draw a filled rectangle
epd_circle(x,y,radius)                  # draw a circle
epd_fill_circle(x,y,radius)             # draw a filled circle
epd_triangle(x0,y0,x1,y1,x2,y2)         # draw a triangle
epd_fill_triangle(x0,y0,x1,y1,x2,y2)    # draw a filled triangle

epd_bitmap(x,y,"image file name")       # display image
"""