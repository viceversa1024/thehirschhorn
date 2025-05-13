#!/usr/bin/env python

import csv
import subprocess
BUCKET_NAME="thehirschhorn.com"
with open('./batch.01.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(f"Doing {row['barcode']}")
        subprocess.run(["aws", "s3", "cp", f"./photos/IMG_{row['front']}.jpeg", f"s3://{BUCKET_NAME}/{row['barcode']}.front.jpeg"])
        subprocess.run(["aws", "s3", "cp", f"./photos/IMG_{row['back']}.jpeg", f"s3://{BUCKET_NAME}/{row['barcode']}.back.jpeg"])
        subprocess.run(["aws", "s3", "cp", "empty.json", f"s3://{BUCKET_NAME}/{row['barcode']}.json"])
