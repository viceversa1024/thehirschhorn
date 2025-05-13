#!/usr/bin/env python

from qreader import QReader
import cv2
import sys
import re

qreader = QReader()
f= sys.argv[1]
print(f)
img = cv2.imread(sys.argv[1])
image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
decoded_text = qreader.detect_and_decode(image=image)
print(decoded_text)
