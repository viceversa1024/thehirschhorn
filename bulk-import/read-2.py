#!/usr/bin/env python

from qreader import QReader
import cv2
import sys
import re
import os
qreader = QReader()
rename = False
for f in range(5068,5287):
    if rename:
        try:
            os.rename(f"photos-2/IMG_{f} 2.jpeg", f"photos-2/IMG_{f}.jpeg")
        except FileNotFoundError:
            print(f"no file {f}")
    else:
        try:
            img = cv2.imread(f"./photos-2/IMG_{f}.jpeg")
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            decoded_text = qreader.detect_and_decode(image=image)
            print(f"{f},{','.join([f for f in decoded_text])}")
        except Exception:
            print(f"{f},")
        sys.stdout.flush()
