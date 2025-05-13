#!/usr/bin/env python

import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

BUCKET_NAME = "thehirschhorn.com"
MAX_WORKERS = 20

def upload_files(row):
    barcode = row['barcode']
    print(f"Doing {barcode}")
    try:
        subprocess.run(["aws", "s3", "cp", "--acl=public-read", f"./photos-2/IMG_{row['front']}.jpeg", f"s3://{BUCKET_NAME}/{barcode}.front.jpg"], check=True)
        subprocess.run(["aws", "s3", "cp", "--acl=public-read", f"./photos-2/IMG_{row['back']}.jpeg", f"s3://{BUCKET_NAME}/{barcode}.back.jpg"], check=True)
        subprocess.run(["aws", "s3", "cp", "empty.json", f"s3://{BUCKET_NAME}/{barcode}.json"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed for {barcode}: {e}")

def main():
    with open('./batch.02.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(upload_files, row) for row in rows]
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions caught during execution

if __name__ == "__main__":
    main()
