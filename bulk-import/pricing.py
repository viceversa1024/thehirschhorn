#!/usr/bin/env python
import json
import csv
import os
import subprocess
BUCKET_NAME="thehirschhorn.com"

with open('./pricing2.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(f"Doing {row['barcode']}")
        blob = {"dimensions": row['size'],
                "price": row['price'],
                "notes": "",
                }
        fn = "thing.json"
        fh = open(fn, "w+")
        fh.write(json.dumps(blob))
        fh.close()
        subprocess.run(["aws", "s3", "cp", fn, f"s3://{BUCKET_NAME}/{row['barcode']}.json"])
        os.remove(fn)

