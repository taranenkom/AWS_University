import boto3

s3 = boto3.client('s3')
bucket_name = 'lab2-inmyuni'
filename = 'exchange_2022.csv'

s3.upload_file(filename, bucket_name, filename)
print("Uploaded to S3")
