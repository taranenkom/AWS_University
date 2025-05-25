import boto3
import os
import pandas as pd
import logging
from botocore.exceptions import ClientError

REGION = "eu-north-1"
KEY_NAME = "ec2-keypair"
KEY_PATH = "/tmp/aws_ec2_key.pem"
AMI_ID = "ami-00f34bf9aeacdf007"  # Free tier
INSTANCE_TYPE = "t3.micro"
LOG_FILE = "lab4.log"

logger = logging.getLogger("lab4")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)

# Console handler for errors only
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


def create_key_pair(key_name=KEY_NAME, key_path=KEY_PATH):
    ec2 = boto3.client("ec2", region_name=REGION)
    logger.info("Creating EC2 key pair...")
    try:
        key_pair = ec2.create_key_pair(KeyName=key_name)
        with open(key_path, "w") as f:
            f.write(key_pair["KeyMaterial"])
        os.chmod(key_path, 0o400)
        logger.info(f"Key pair created and saved to {key_path}")
    except ClientError as e:
        if "InvalidKeyPair.Duplicate" in str(e):
            logger.warning("Key pair already exists.")
        else:
            logger.error(f"Key pair creation error: {e}")

def create_instance(ami_id=AMI_ID, instance_type=INSTANCE_TYPE, key_name=KEY_NAME):
    ec2 = boto3.client("ec2", region_name=REGION)
    logger.info("Launching EC2 instance...")
    try:
        response = ec2.run_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            KeyName=key_name
        )
        instance_id = response["Instances"][0]["InstanceId"]
        logger.info(f"Instance launched: {instance_id}")
        return instance_id
    except ClientError as e:
        logger.error(f"Error launching instance: {e}")

def get_public_ip(instance_id):
    ec2 = boto3.client("ec2", region_name=REGION)
    logger.info(f"Getting public IP for instance {instance_id}...")
    try:
        reservations = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"]
        for r in reservations:
            for inst in r["Instances"]:
                ip = inst.get("PublicIpAddress")
                logger.info(f"Public IP: {ip}")
                return ip
    except ClientError as e:
        logger.error(f"Error getting public IP: {e}")

def terminate_instance(instance_id):
    ec2 = boto3.client("ec2", region_name=REGION)
    logger.info(f"Terminating instance {instance_id}...")
    try:
        ec2.terminate_instances(InstanceIds=[instance_id])
        logger.info("Instance terminated.")
    except ClientError as e:
        logger.error(f"Error terminating instance: {e}")

def create_bucket(bucket_name):
    s3 = boto3.client("s3", region_name=REGION)
    logger.info(f"Creating S3 bucket '{bucket_name}'...")
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": REGION}
        )
        logger.info("Bucket created.")
    except ClientError as e:
        if "BucketAlreadyOwnedByYou" in str(e) or "BucketAlreadyExists" in str(e):
            logger.warning("Bucket already exists.")
        else:
            logger.error(f"Bucket creation error: {e}")

def list_buckets():
    s3 = boto3.client("s3")
    logger.info("Listing buckets...")
    try:
        buckets = s3.list_buckets()
        for b in buckets["Buckets"]:
            logger.info(f" - {b['Name']}")
    except ClientError as e:
        logger.error(f"Error listing buckets: {e}")

def upload_file(file_name, bucket_name, s3_key):
    s3 = boto3.client("s3")
    logger.info(f"Uploading {file_name} to bucket {bucket_name} as {s3_key}...")
    try:
        s3.upload_file(file_name, bucket_name, s3_key)
        logger.info("Upload successful.")
    except ClientError as e:
        logger.error(f"Upload error: {e}")

def read_csv_from_s3(bucket_name, s3_key):
    s3 = boto3.client("s3")
    logger.info(f"Reading {s3_key} from bucket {bucket_name}...")
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
        df = pd.read_csv(obj["Body"])
        logger.info("Data preview:\n%s", df.head().to_string())
    except ClientError as e:
        if "NoSuchKey" in str(e):
            logger.warning("File does not exist in bucket.")
        else:
            logger.error(f"Error reading file from S3: {e}")

def delete_bucket(bucket_name):
    s3 = boto3.resource("s3")
    logger.info(f"Deleting bucket {bucket_name}...")

    try:
        # Delete all objects in the bucket
        bucket = s3.Bucket(bucket_name)
        object_summary_list = list(bucket.objects.all())
        if object_summary_list:
            logger.info(f"Bucket not empty, deleting {len(object_summary_list)} object(s)...")
            bucket.objects.all().delete()
            logger.info("All objects deleted.")

        # Now delete the bucket itself
        bucket.delete()
        logger.info("Bucket deleted.")
    except ClientError as e:
        logger.error(f"Error deleting bucket: {e}")

if __name__ == "__main__":
    create_key_pair()
    instance_id = create_instance()
    if instance_id:
        get_public_ip(instance_id)
        terminate_instance(instance_id)

    bucket_name = "lab4-pti-demo-bucket"
    create_bucket(bucket_name)
    list_buckets()
    upload_file("data.csv", bucket_name, "data.csv")
    read_csv_from_s3(bucket_name, "data.csv")
    delete_bucket(bucket_name)
    
    if os.path.exists(KEY_PATH):
        os.remove(KEY_PATH)
        logger.info(f"Key file {KEY_PATH} deleted.")