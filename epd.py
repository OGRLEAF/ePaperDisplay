import serial
from time import sleep
from platform import system as os

VERBOSE = False

MAC='/dev/cu.usbserial'
LINUX='/dev/ttyUSB0'
PORT = ''

if os()=='Linux':
    PORT = LINUX
elif os()=='Darwin':
    PORT = MAC
else:
    PORT = raw_input('Define serial port for EPD connection (e.g. /dev/ttyUSB0): ')

ser                 = None
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
    ser.write(H2B(cmd))
    if VERBOSE:
        print ">",ser.readline()


def epd_connect():
    global ser
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD_RATE,
        timeout=1
    )
    print "> EPD connected"
    epd_handshake()


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
    global ser
    ser.close()
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


def epd_pixel(x0, y0): # int,int
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    _cmd = FRAME_BEGIN+"000D"+CMD_DRAW_PIXEL+hex_x0+hex_y0+FRAME_END
    send(_cmd)


def epd_line(x0, y0, x1, y1): # int,int,int,int
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0011"+CMD_DRAW_LINE+hex_x0+hex_y0+hex_x1+hex_y1+FRAME_END
    send(_cmd)


def epd_rect(x0, y0, x1, y1): # int,int,int,int
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0011"+CMD_DRAW_RECT+hex_x0+hex_y0+hex_x1+hex_y1+FRAME_END
    send(_cmd)


def epd_fill_rect(x0, y0, x1, y1): # int,int,int,int
    hex_x0 = ("000"+hex(x0)[2:])[-4:]
    hex_y0 = ("000"+hex(y0)[2:])[-4:]
    hex_x1 = ("000"+hex(x1)[2:])[-4:]
    hex_y1 = ("000"+hex(y1)[2:])[-4:]
    _cmd = FRAME_BEGIN+"0011"+CMD_FILL_RECT+hex_x0+hex_y0+hex_x1+hex_y1+FRAME_END
    send(_cmd)


def epd_circle(x0, y0, r): # int,int,int
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

