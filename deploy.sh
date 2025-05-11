#!/bin/bash
source .venv/bin/activate
set -e
rm -rf build
mkdir -p build
cd build
pip install -r ../requirements.lambda.txt -t .
cp ../lambda_function.py .
cp -r ../html .
SHA=$(git log --oneline | cut -b1-7 | head -1)
ZIPFILE=barcode-responder-lambda.$(date +%Y-%m-%d-%H-%M).$SHA.zip
ARCHIVE=$HOME/$ZIPFILE
zip -r $ARCHIVE .
aws --profile keene s3 cp $ARCHIVE s3://thehirschhorn.com.lambda.sources/
aws --profile keene lambda update-function-code \
    --function-name barcodeResponder312 \
    --s3-key $ZIPFILE \
    --s3-bucket thehirschhorn.com.lambda.sources
