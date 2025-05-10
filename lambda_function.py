import json
import boto3
import os
import urllib.parse
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader
from botocore.config import Config
import jwt
from jwt import PyJWKClient
import requests


BUCKET_NAME = "thehirschhorn.com"
EXPIRE_SECONDS = 300
COGNITO_USER_POOL_ID = "us-east-1_5r30JFnCk"
COGNITO_REGION = "us-east-1"
COGNITO_CLIENT_ID = "7ci7n0p7ol4eoeep96gpkndbsp"
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
JWKS = requests.get(JWKS_URL).json()
jwk_client = PyJWKClient(JWKS_URL)


def jwt_decode(jwt_token):
    print(jwt_token)
    signing_key = jwk_client.get_signing_key_from_jwt(jwt_token).key
    decoded = jwt.decode(
        jwt_token,
        signing_key,
        algorithms=["RS256"],
        audience=COGNITO_CLIENT_ID,
        issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}",
    )
    return decoded


def object_exists(s3, bucket_name, object_key):
    try:
        s3.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            # Some other error occurred
            raise


def get_signed_urls(s3, event, barcode):
    body = event["body"]
    if event.get("isBase64Encoded", False):
        body = base64.b64decode(body).decode()

    form_data = urllib.parse.parse_qs(body)

    # Extract values
    front = form_data.get("frontpicture", [""])[0]
    back = form_data.get("backpicture", [""])[0]
    json = {
        "dimensions": form_data.get("dimensions", [""])[0],
        "price": form_data.get("price", [""])[0],
        "notes": form_data.get("notes", [""])[0],
    }

    # Now you can use `password`, `front`, `back` safely
    # print("Front:", front)
    # print("Back:", back)

    front_key = f"{barcode}.front.jpg"
    back_key = f"{barcode}.back.jpg"
    json_key = f"{barcode}.json"

    front_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": front_key,
            "ContentType": "image/jpeg",
            "ACL": "public-read",
        },
        ExpiresIn=EXPIRE_SECONDS,
    )

    back_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": back_key,
            "ContentType": "image/jpeg",
            "ACL": "public-read",
        },
        ExpiresIn=EXPIRE_SECONDS,
    )

    json_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": json_key,
            "ContentType": "application/json",
            "ACL": "bucket-owner-full-control",
        },
        ExpiresIn=EXPIRE_SECONDS,
    )

    return {"front_url": front_url, "back_url": back_url, "json_url": json_url}, 200


def lambda_handler(event, context):
    clear_cookie = False
    upload_urls = None
    print("Event: ", event)
    jwt_token = event.get("headers", {}).get("cookie", None)
    if jwt_token:
        try:
            user = jwt_decode(jwt_token.split("=")[1])["email"]
        except jwt.ExpiredSignatureError:
            print("JWT token expired")
            clear_cookie = True
            user = None
    else:
        user = None
    print(f"user: {user}")
    s3 = boto3.client(
        "s3", region_name="us-east-2", config=Config(s3={"addressing_style": "virtual"})
    )
    if "path" in event and event["path"] == "/":
        template_name = "index.html"
        path = None
        s3_object = None
    elif "path" in event and len(event["path"]) > 1:
        s3_object = f"{event['path'][1:]}.json"
        path = event["path"]
        template_name = None
    else:
        template_name = "index.html"
        s3_object = None
        path = None

    dumped_event = json.dumps(event)
    print(f"template_name: {template_name}")
    if event["httpMethod"] == "POST":
        message, status = get_signed_urls(s3, event, event["path"][1:])
        if status != 200:
            return {
                "statusCode": status,
                "body": message,
                "headers": {"Content-Type": "text/html"},
            }
        else:
            print("generated signed urls")
            upload_urls = message
            print(upload_urls)
            print(status)
            return {
                "statusCode": status,
                "body": json.dumps(upload_urls),
                "headers": {"Content-Type": "application/json"},
            }
    if event["httpMethod"] == "DELETE":
        print("delete")
        for file in ["front.jpg", "back.jpg", "json"]:
            delete_file_name = f"{event['path'][1:]}.{file}"
            print(f"delete_file_name: {delete_file_name}")
            s3.delete_object(Bucket=BUCKET_NAME, Key=delete_file_name)
        return {
        "statusCode": 200,
        "body": json.dumps({"message": "Delete request received"}),
        "headers": {"Content-Type": "application/json"},
    }
    else:
        if template_name != "index.html":
            if s3_object and object_exists(s3, BUCKET_NAME, s3_object):
                template_name = "200.html"
            else:
                template_name = "404.html"
    print(template_name)

    image_url_base = "https://s3.us-east-2.amazonaws.com/thehirschhorn.com"
    if path:
        barcode = path[1:]
    else:
        barcode = ""
    front_image_url = f"{image_url_base}/{barcode}.front.jpg"
    back_image_url = f"{image_url_base}/{barcode}.back.jpg"
    json_full_url = f"{image_url_base}/{barcode}.json"
    response = requests.get(json_full_url)
    print(f"json_full_url: {json_full_url}")
    print(f"response: {response}")
    if response.status_code == 200:
        try:
            json_data = response.json()
            dimensions = json_data.get("dimensions", "foo")
            price = json_data.get("price", "")
            notes = json_data.get("notes", "")
        except ValueError:
            dimensions = ""
            price = ""
            notes = ""
    else:
        dimensions = "foo"
        price = ""
        notes = ""
    redirect_uri = urllib.parse.quote_plus(
        "http://localhost:8080"
        if os.environ.get("LOCAL_LAMBDA")
        else "https://thehirschhorn.com"
    )
    login_url = (
        "https://us-east-15r30jfnck.auth.us-east-1.amazoncognito.com/login/continue?"
        + "client_id=7ci7n0p7ol4eoeep96gpkndbsp&"
        + f"redirect_uri={redirect_uri}&"
        + "response_type=token&"
        + "scope=aws.cognito.signin.user.admin+email+openid+phone+profile&"
        + (f"state={path}" if path else "")
    )
    print(f"login_url: {login_url}")

    # Set up the Jinja2 environment to load templates from the 'html' directory
    env = Environment(loader=FileSystemLoader("./html"))

    # Load the template file (200.html)
    template = env.get_template(template_name)

    # Render the template with the desired context variable
    rendered_html = template.render(
        barcode=barcode,
        upload_urls=upload_urls,
        dumped_event=dumped_event,
        path=path,
        front_image_url=front_image_url,
        back_image_url=back_image_url,
        user=user,
        dimensions=dimensions,
        price=price,
        notes=notes,
        login_url=login_url,
    )

    headers = {"Content-Type": "text/html"}

    if clear_cookie:
        headers["Set-Cookie"] = (
            "keene_jwt=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        )
    return {
        "statusCode": 200,
        "body": rendered_html,
        "headers": headers,
    }
