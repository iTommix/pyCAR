#!/usr/bin/python3
# -*- coding: utf-8 -*-
from Adafruit_MAX9744 import MAX9744
import sys
print("Set", sys.argv[1])
amp1 = MAX9744(0x4A)
amp2 = MAX9744(0x4b)
amp1.set_volume(int(sys.argv[1]))
amp2.set_volume(int(sys.argv[1]))
