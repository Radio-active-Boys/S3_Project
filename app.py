import os
import uuid
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

load_dotenv()

S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL")
PUBLIC_S3_URL = os.getenv("PUBLIC_S3_URL", S3_ENDPOINT)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "uploads")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seaweed-flask")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
    verify=False,
    config=Config(
        s3={"addressing_style": "path"},
        signature_version="s3v4",
    ),
)

def ensure_bucket():
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except ClientError:
        logger.info("Creating bucket %s", S3_BUCKET)
        s3.create_bucket(Bucket=S3_BUCKET)

ensure_bucket()

def build_key(user_id: str, filename: str) -> str:
    return f"{user_id}/{uuid.uuid4().hex}_{filename}"

def public_url(key: str) -> str:
    return f"{PUBLIC_S3_URL}/{S3_BUCKET}/{key}"


@app.route("/upload", methods=["POST"])
def upload_file():
    user_id = request.form.get("user_id")
    file = request.files.get("file")

    if not user_id or not file:
        return {"error": "user_id and file required"}, 400

    key = build_key(user_id, file.filename)

    try:
        s3.upload_fileobj(
            file.stream,
            S3_BUCKET,
            key,
            ExtraArgs={"ContentType": file.mimetype},
        )
    except Exception as e:
        logger.exception("Upload failed")
        return {"error": str(e)}, 500

    return {
        "key": key,
        "fileUrl": public_url(key)
    }, 201


@app.route("/presign-upload", methods=["POST"])
def presign_upload():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    filename = data.get("filename")
    content_type = data.get("content_type", "application/octet-stream")

    if not user_id or not filename:
        return {"error": "user_id and filename required"}, 400

    key = build_key(user_id, filename)

    upload_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=900,
    )

    return {
        "uploadUrl": upload_url,
        "key": key,
        "fileUrl": public_url(key)
    }


@app.route("/files")
def list_files():
    user_id = request.args.get("user_id")
    if not user_id:
        return {"error": "user_id required"}, 400

    prefix = f"{user_id}/"
    files = []

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            files.append({
                "key": key,
                "fileUrl": public_url(key),
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat()
            })

    return {
        "count": len(files),
        "files": files
    }


@app.route("/download", methods=["POST"])
def download():
    key = request.json.get("key")
    if not key:
        return {"error": "key required"}, 400

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=300,
    )
    return {"downloadUrl": url}

@app.route("/delete", methods=["POST"])
def delete_file():
    key = request.json.get("key")
    if not key:
        return {"error": "key required"}, 400

    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
    except Exception as e:
        logger.exception("Delete failed")
        return {"error": str(e)}, 500

    return {"message": "Deleted"}

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=True)