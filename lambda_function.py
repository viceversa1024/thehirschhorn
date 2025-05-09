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


def do_upload(s3, event, barcode):
    body = event["body"]
    if event.get("isBase64Encoded", False):
        body = base64.b64decode(body).decode()

    form_data = urllib.parse.parse_qs(body)

    # Extract values
    front = form_data.get("frontpicture", [""])[0]
    back = form_data.get("backpicture", [""])[0]

    # Now you can use `password`, `front`, `back` safely
    print("Front:", front)
    print("Back:", back)

    front_key = f"{barcode}.front.jpg"
    back_key = f"{barcode}.back.jpg"

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
    return {"front_url": front_url, "back_url": back_url}, 200


def lambda_handler(event, context):
    upload_urls = None
    print("Event: ", event)
    jwt_token = event.get("headers", {}).get("Cookie", None)
    if jwt_token:
        user = jwt_decode(jwt_token.split("=")[1])["email"]
    else:
        user = None
    print(user)
    s3 = boto3.client(
        "s3", region_name="us-east-2", config=Config(s3={"addressing_style": "virtual"})
    )
    if "path" in event and event["path"] == "/":
        template_name = "index.html"
        path = None
        s3_object = None
    elif "path" in event and len(event["path"]) > 1:
        s3_object = f"{event['path'][1:]}.front.jpg"
        path = event["path"]
        template_name = None
    else:
        template_name = "index.html"
        s3_object = None
        path = None

    dumped_event = json.dumps(event)
    print(template_name)
    if event["httpMethod"] == "POST":
        message, status = do_upload(s3, event, event["path"][1:])
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
    )

    return {
        "statusCode": 200,
        "body": rendered_html,
        "headers": {
            "Content-Type": "text/html",
            "Cookie": "keene_jwt=eyJraWQiOiJ3RmJUMElVdVdadk9BMkdNODBrOWYyUVhvdnFrXC81YUt1NWNVN1p6TmpJVT0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoicGdPeGpjRGRKcjk3T0RNRFNiMEotUSIsInN1YiI6Ijg0YjhjNDg4LWMwOTEtNzA3Yy1lMGFkLWRhNTY4N2NlNjA5MiIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV81cjMwSkZuQ2siLCJjb2duaXRvOnVzZXJuYW1lIjoiODRiOGM0ODgtYzA5MS03MDdjLWUwYWQtZGE1Njg3Y2U2MDkyIiwiYXVkIjoiN2NpN24wcDdvbDRlb2VlcDk2Z3BrbmRic3AiLCJldmVudF9pZCI6IjBhMDIwN2M3LWRkYjYtNGUxMC1iYTllLTgyODBhMjg1MDI2MCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzQ2NzUyMDU0LCJleHAiOjE3NDY3NTU2NTQsImlhdCI6MTc0Njc1MjA1NCwianRpIjoiZmM3MzgwYmQtODQ5ZS00NTU3LWFlMjQtNDNjZjRlNThiNTc1IiwiZW1haWwiOiJ3YXRlcm1haEB1Y2kuZWR1In0.HmVTmSAT2XeiAgmDnOs33yl3l-2IF5qrahEg6oiz2_TZtCY0eOQrdXGqiyjlPTwY_jT9okWfhLRhwrPpIujn4Xigj8gOkItdhvtBkGRRBSuQKpLq8W_i3veyZh-h6Csg3O9slhURKbABV4SlnYsLO5y4BOsMY97QH2c2Sx78cC3-uItdLeJ6y3q9PgcV8IRcLBjM-ns7ZUKQm_InBEXPIHPkj1TVmxjDMW6WuvyBvkzpU2GsQviV7x0fKdbbdIwoMtjbQ7HoIiN-P5rfetQ6NbZCsfd1vrZfetyHHl_Avor-2ygApMYvFoKJU0rB5SW96jNi1z2Tcr9X_k_2oyFENA",
        },
    }


print(
    lambda_handler(
        {
            "httpMethod": "GET",
            "path": "/test",
            "headers": {
                "Cookie": "keene_jwt=eyJraWQiOiJ3RmJUMElVdVdadk9BMkdNODBrOWYyUVhvdnFrXC81YUt1NWNVN1p6TmpJVT0iLCJhbGciOiJSUzI1NiJ9.eyJhdF9oYXNoIjoicGdPeGpjRGRKcjk3T0RNRFNiMEotUSIsInN1YiI6Ijg0YjhjNDg4LWMwOTEtNzA3Yy1lMGFkLWRhNTY4N2NlNjA5MiIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV81cjMwSkZuQ2siLCJjb2duaXRvOnVzZXJuYW1lIjoiODRiOGM0ODgtYzA5MS03MDdjLWUwYWQtZGE1Njg3Y2U2MDkyIiwiYXVkIjoiN2NpN24wcDdvbDRlb2VlcDk2Z3BrbmRic3AiLCJldmVudF9pZCI6IjBhMDIwN2M3LWRkYjYtNGUxMC1iYTllLTgyODBhMjg1MDI2MCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzQ2NzUyMDU0LCJleHAiOjE3NDY3NTU2NTQsImlhdCI6MTc0Njc1MjA1NCwianRpIjoiZmM3MzgwYmQtODQ5ZS00NTU3LWFlMjQtNDNjZjRlNThiNTc1IiwiZW1haWwiOiJ3YXRlcm1haEB1Y2kuZWR1In0.HmVTmSAT2XeiAgmDnOs33yl3l-2IF5qrahEg6oiz2_TZtCY0eOQrdXGqiyjlPTwY_jT9okWfhLRhwrPpIujn4Xigj8gOkItdhvtBkGRRBSuQKpLq8W_i3veyZh-h6Csg3O9slhURKbABV4SlnYsLO5y4BOsMY97QH2c2Sx78cC3-uItdLeJ6y3q9PgcV8IRcLBjM-ns7ZUKQm_InBEXPIHPkj1TVmxjDMW6WuvyBvkzpU2GsQviV7x0fKdbbdIwoMtjbQ7HoIiN-P5rfetQ6NbZCsfd1vrZfetyHHl_Avor-2ygApMYvFoKJU0rB5SW96jNi1z2Tcr9X_k_2oyFENA"
            },
        },
        None,
    )
)
