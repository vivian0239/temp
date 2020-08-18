#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

import ST7789 as TFT
import datetime
from time import sleep

from PIL import Image, ImageDraw, ImageFont, ImageColor

import numpy as np
import time
import os
import fcntl
import mmap
import struct
import digitalio
import board
#import adafruit_rgb_display.st7789 as st7789

# wait sometime to start
time.sleep(5)

# definitions from linux/fb.h
FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602
FBIOBLANK = 0x4611

FB_TYPE_PACKED_PIXELS = 0
FB_TYPE_PLANES = 1
FB_TYPE_INTERLEAVED_PLANES = 2
FB_TYPE_TEXT = 3
FB_TYPE_VGA_PLANES = 4
FB_TYPE_FOURCC = 5

FB_VISUAL_MONO01 = 0
FB_VISUAL_MONO10 = 1
FB_VISUAL_TRUECOLOR = 2
FB_VISUAL_PSEUDOCOLOR = 3
FB_VISUAL_DIRECTCOLOR = 4
FB_VISUAL_STATIC_PSEUDOCOLOR = 5
FB_VISUAL_FOURCC = 6

FB_BLANK_UNBLANK = 0
FB_BLANK_POWERDOWN = 4

# Raspberry Pi pin configuration:
RST = 25#27
DC  = 24#25
LED = 27#24
SPI_PORT = 0
SPI_DEVICE = 0
SPI_MODE = 0b11
SPI_SPEED_HZ = 40000000

class Bitfield:  # pylint: disable=too-few-public-methods
    def __init__(self, offset, length, msb_right):
        self.offset = offset
        self.length = length
        self.msb_right = msb_right


# Kind of like a pygame Surface object, or not!
# http://www.pygame.org/docs/ref/surface.html
class Framebuffer:  # pylint: disable=too-many-instance-attributes
    def __init__(self, dev):
        self.dev = dev
        self.fbfd = os.open(dev, os.O_RDWR)
        vinfo = struct.unpack(
            "8I12I16I4I",
            fcntl.ioctl(self.fbfd, FBIOGET_VSCREENINFO, " " * ((8 + 12 + 16 + 4) * 4)),
        )
        finfo = struct.unpack(
            "16cL4I3HI", fcntl.ioctl(self.fbfd, FBIOGET_FSCREENINFO, " " * 48)
        )

        bytes_per_pixel = (vinfo[6] + 7) // 8
        screensize = vinfo[0] * vinfo[1] * bytes_per_pixel

        fbp = mmap.mmap(
            self.fbfd, screensize, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ
        )

        self.fbp = fbp
        self.xres = vinfo[0]
        self.yres = vinfo[1]
        self.xoffset = vinfo[4]
        self.yoffset = vinfo[5]
        self.bits_per_pixel = vinfo[6]
        self.bytes_per_pixel = bytes_per_pixel
        self.grayscale = vinfo[7]
        self.red = Bitfield(vinfo[8], vinfo[9], vinfo[10])
        self.green = Bitfield(vinfo[11], vinfo[12], vinfo[13])
        self.blue = Bitfield(vinfo[14], vinfo[15], vinfo[16])
        self.transp = Bitfield(vinfo[17], vinfo[18], vinfo[19])
        self.nonstd = vinfo[20]
        self.name = b"".join([x for x in finfo[0:15] if x != b"\x00"])
        self.type = finfo[18]
        self.visual = finfo[20]
        self.line_length = finfo[24]
        self.screensize = screensize

    def close(self):
        self.fbp.close()
        os.close(self.fbfd)

    def blank(self, blank):
        # Blanking is not supported by all drivers
        try:
            if blank:
                fcntl.ioctl(self.fbfd, FBIOBLANK, FB_BLANK_POWERDOWN)
            else:
                fcntl.ioctl(self.fbfd, FBIOBLANK, FB_BLANK_UNBLANK)
        except IOError:
            pass

    def __str__(self):
        visual_list = [
            "MONO01",
            "MONO10",
            "TRUECOLOR",
            "PSEUDOCOLOR",
            "DIRECTCOLOR",
            "STATIC PSEUDOCOLOR",
            "FOURCC",
        ]
        type_list = [
            "PACKED_PIXELS",
            "PLANES",
            "INTERLEAVED_PLANES",
            "TEXT",
            "VGA_PLANES",
            "FOURCC",
        ]
        visual_name = "unknown"
        if self.visual < len(visual_list):
            visual_name = visual_list[self.visual]
        type_name = "unknown"
        if self.type < len(type_list):
            type_name = type_list[self.type]

        return (
            'mode "%sx%s"\n' % (self.xres, self.yres)
            + "    nonstd %s\n" % self.nonstd
            + "    rgba %s/%s,%s/%s,%s/%s,%s/%s\n"
            % (
                self.red.length,
                self.red.offset,
                self.green.length,
                self.green.offset,
                self.blue.length,
                self.blue.offset,
                self.transp.length,
                self.transp.offset,
            )
            + "endmode\n"
            + "\n"
            + "Frame buffer device information:\n"
            + "    Device      : %s\n" % self.dev
            + "    Name        : %s\n" % self.name
            + "    Size        : (%d, %d)\n" % (self.xres, self.yres)
            + "    Length      : %s\n" % self.screensize
            + "    BPP         : %d\n" % self.bits_per_pixel
            + "    Type        : %s\n" % type_name
            + "    Visual      : %s\n" % visual_name
            + "    LineLength  : %s\n" % self.line_length
        )

device = "/dev/fb0"
fb = Framebuffer(device)
print(fb)

disp = TFT.ST7789(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=SPI_SPEED_HZ),
       mode=SPI_MODE, rst=RST, dc=DC, led=LED)

# Initialize display.
disp.begin()

# Clear display.
disp.clear()

image1 = Image.new("RGB", (240, 240), "BLACK")
draw = ImageDraw.Draw(image1)
disp.display(image1)

while True:
    t = time.monotonic()
    fb.fbp.seek(0)
    b = fb.fbp.read(fb.screensize)
    fbimage = Image.frombytes("RGBA", (fb.xres, fb.yres), b, "raw")
    b, g, r, a = fbimage.split()
    fbimage = Image.merge("RGB", (r, g, b))
    #fbimage = fbimage.resize((width, height)) #mxx
    box = (0, 0, 240, 240) #mxx
    fbimage = fbimage.crop(box) #mxx

    disp.display(fbimage)
    #disp.display(fbimage, rotation)
    print(1.0 / (time.monotonic() - t))
fb.close()


'''
def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


disp = TFT.ST7789(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=SPI_SPEED_HZ),
       mode=SPI_MODE, rst=RST, dc=DC, led=LED)

# Initialize display.
disp.begin()

# Clear display.
disp.clear()

# Analogue clock setting
width = 240
height = 240
w = width       # screen width
h = height      # screen height
dx = 30         # distance between edge of clock and left edge of screen
dy = 57         # distance between edge of clock and bottom edge of screen
r = 90          # r of clock circle
Ls = r - 2      # length of second hand of watch
Lm = r - 8      # length of minute hand of watch
Lh = Lm - 16    # length of hour hand of watch
X1 = w-1-r*2-dx
Y1 = h-1-r*2-dy
X2 = w-1-dx
Y2 = h-1-dy
Xc = w-1-r-dx   # X coordinates of the center of clock
Yc = h-1-r-dy   # Y coordinates of the conter of clock
Pi = 3.14159265358979  # number pi

image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
draw = ImageDraw.Draw(image1)

# Initial screen (Demonstration for displaying images)
image2 = Image.open('raspberry_pi_clock.jpg')
image2.thumbnail((240, 240), Image.ANTIALIAS)
image2 = expand2square(image2, (0,0,0))
image3 = Image.open('raspberry_pi_clock.jpg')
image3.thumbnail((120, 120), Image.ANTIALIAS)
image3 = expand2square(image3, (0,0,0))

disp.display(image1)
sleep(0.2)
disp.display(image3,0,0,119,119)
sleep(0.2)
disp.display(image3,120,0,239,119)
sleep(0.2)
disp.display(image3,0,120,119,239)
sleep(0.2)
disp.display(image3,120,120,239,239)
sleep(1)
disp.display(image1)
sleep(0.2)
image4 = Image.open('1.jpg')
image4.thumbnail((240, 240), Image.ANTIALIAS)
image4 = expand2square(image4, (0,0,0))
disp.display(image4)
sleep(0.5)
image5 = Image.open('2.jpg')
image5.thumbnail((240, 240), Image.ANTIALIAS)
image5 = expand2square(image5, (0,0,0))
disp.display(image5)
sleep(0.5)
image6 = Image.open('3.jpg')
image6.thumbnail((240, 240), Image.ANTIALIAS)
image6 = expand2square(image6, (0,0,0))
disp.display(image6)
sleep(0.5)
image7 = Image.open('4.jpg')
image7.thumbnail((240, 240), Image.ANTIALIAS)
image7 = expand2square(image7, (0,0,0))
disp.display(image7)
sleep(0.5)
disp.display(image1)
sleep(0.2)
image4.thumbnail((120, 120), Image.ANTIALIAS)
image4 = expand2square(image4, (0,0,0))
disp.display(image4,0,0,119,119)
sleep(0.2)
image5.thumbnail((120, 120), Image.ANTIALIAS)
image5 = expand2square(image5, (0,0,0))
disp.display(image5,120,0,239,119)
sleep(0.2)
image6.thumbnail((120, 120), Image.ANTIALIAS)
image6 = expand2square(image6, (0,0,0))
disp.display(image6,0,120,119,239)
sleep(0.2)
image7.thumbnail((120, 120), Image.ANTIALIAS)
image7 = expand2square(image7, (0,0,0))
disp.display(image7,120,120,239,239)
sleep(1)
disp.display(image1)
sleep(0.2)
disp.display(image2)
sleep(0.5)

# font setting
font = ImageFont.load_default()
fontJ = ImageFont.truetype('DejaVuSans.ttf', 28, encoding='unic')

Weekday = ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    #print position
    position = position[0], position[1]
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

try:
    last_time = ""
    time = datetime.datetime.now().time().strftime("%H:%M:%S")
    disp.display(image1)
    while 1:
        #draw = disp.draw()
        # Create blank image for drawing.
        image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1)

        while time == last_time:
            sleep(0.1)
            time = datetime.datetime.now().time().strftime("%H:%M:%S")
        last_time = time
        H = int(time[0:2])
        M = int(time[3:5])
        S = int(time[6:8])

        # Analogue clock
        draw.ellipse((X1, Y1, X2, Y2), outline=(255,255,255), fill=(0,0,0))
        draw.line((Xc, Yc, Xc+Ls*np.sin(Pi*(S/30.0)), Yc-Ls*np.cos(Pi*(S/30.0))), fill=(255,0,0))
        draw.line((Xc, Yc, Xc+Lm*np.sin(Pi*((M/30.0 + S/1800.0))), Yc-Lm*np.cos(Pi*((M/30.0 + S/1800.0)))), fill=(255,255,0))
        draw.line((Xc, Yc, Xc+Lh*np.sin(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0))), Yc-Lh*np.cos(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0)))), fill=(63,255,63))

        # Digital clock
        draw.rectangle((0, 184, 239, 239), outline=(0,0,0), fill=(0,0,0))
        now = datetime.datetime.now()
        date = now.date().strftime("%Y/%m/%d")
        weekday = Weekday[now.weekday()]
        time = now.time().strftime("%H:%M:%S")
        draw_rotated_text(image1, date + "(" + weekday + ")", (15,185), 0, font=fontJ, fill=(255,255,0) )
        draw_rotated_text(image1, time, (60,213), 0, font=fontJ, fill=(255,255,0) )
        disp.display(image1)

except KeyboardInterrupt:
    pass
finally:
    disp.clear()
    disp.display(image1)

    image = Image.open('raspberry_pi_clock.jpg')
    image.thumbnail((240, 240), Image.ANTIALIAS)
    image = expand2square(image, (0,0,0))
    disp.display(image2)
    sleep(1)

    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image1)
    disp.display(image1)
'''
