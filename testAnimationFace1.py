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

# Raspberry Pi pin configuration:
RST = 25#27
DC  = 24#25
LED = 27#24
SPI_PORT = 0
SPI_DEVICE = 0
SPI_MODE = 0b11
SPI_SPEED_HZ = 40000000

disp = TFT.ST7789(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=SPI_SPEED_HZ),
       mode=SPI_MODE, rst=RST, dc=DC, led=LED)

# Initialize display.
disp.begin()

# Clear display.
disp.clear()

image1 = Image.new("RGB", (240, 240), "BLACK")
draw = ImageDraw.Draw(image1)
disp.display(image1)

path1 = '/home/pi/Python_ST7789/examples/gifToJpg2/frame_'
path2 = '_delay-0.04s.jpg'
i = 0
while True:
    time.sleep(0.1)
    t = time.monotonic()
    if i > 75:
        i = 0
    if i < 10:
        image1 = Image.open(path1 + '0' + str(i) + path2)
    else:
        image1 = Image.open(path1 + str(i) + path2)
    disp.display(image1)
    i = i + 3
    print(1.0 / (time.monotonic() - t))
