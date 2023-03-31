import json
import boto3
import time
import requests
import io
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

host = "search-photos-u3tc7hbdv2jps6i3mjfq5tiaiq.us-east-1.es.amazonaws.com"
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
)

def getImageLabels(bucket, imageKey): 
    client = boto3.client('rekognition')
    response = client.detect_labels(Image = {'S3Object':{'Bucket':bucket,'Name': imageKey}}, MaxLabels=10, MinConfidence=90)
    print(response)
    print(response['Labels'])
    labels = []

    for label in response['Labels']: 
        labels.append(label['Name'])
    
    return labels

def fetchMetaData(bucket, imageKey): 
    client = boto3.client('s3')
    response = client.head_object(Bucket = bucket, Key = imageKey)
    print("Show me head object response: ", response)
    headObjLabels = response["ResponseMetadata"]["HTTPHeaders"].get("x-amz-meta-customlabels", "")
    print("Show me HTTPHeaders: ", response["ResponseMetadata"]["HTTPHeaders"])
    print("show me response metadata: ", response["ResponseMetadata"])

    if headObjLabels:
        print("head object labels: ", headObjLabels)
        headObjLabels = headObjLabels.split(",")
    else: 
        headObjLabels = []
    return headObjLabels

def indexPhoto(index, photoDoc): 
    response = client.index(
        index = 'photos',
        body = photoDoc,
        id = photoDoc['objectKey'],
        refresh = True
    )   
    print(response)

def lambda_handler(event, context):

    # print('Codebuild test! :)')
    print('Pipeline test!')

    for record in event['Records']: 
        #get bucket and photo object
        bucket = record['s3']['bucket']['name']
        imageKey = record['s3']['object']['key']
        print(bucket, imageKey)
    
        labels = getImageLabels(bucket, imageKey)
        print("rekognition labels: ", labels)

        customLabels = fetchMetaData(bucket, imageKey)
        print("custom labels: ", customLabels)
        labels += customLabels
        print("all labels: ", labels)

        #create json object for es index
        photoDoc = {
            "objectKey" : imageKey,
            "bucket" : bucket, 
            "createdTimeStamp" : time.strftime("%Y%m%d-%H%M%S"),
            "labels" : labels
        }

        print("object key is ", photoDoc['objectKey'])

        #index photo to es
        indexPhoto('photos', photoDoc)

    return{
        'statusCode' : 200, 
        'body' : json.dumps('Hello from Lambda!')
    }


