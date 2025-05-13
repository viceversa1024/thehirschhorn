#!/usr/bin/env python

from qreader import QReader
import cv2
import sys
import re

qreader = QReader()
for f in range(4513,5063):
    img = cv2.imread(f"./photos/IMG_{f}.jpeg")
    try:
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        decoded_text = qreader.detect_and_decode(image=image)
        print(f"{f},{','.join([f for f in decoded_text])}")
    except Exception:
        print(f"{f},")
    sys.stdout.flush()
