import boto3
import json
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import random

region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

host = 'search-photos-u3tc7hbdv2jps6i3mjfq5tiaiq.us-east-1.es.amazonaws.com' # The OpenSearch domain endpoint with https:// and without a trailing slash
index = 'photos'
url = host + '/' + index + '/_search'

lex = boto3.client('lex-runtime', region_name = region)

def getQueryLabels(query): #send input to amazon lex, get labels to query es
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    userId = ''.join(random.choice(alpha) for x in range(8)) #generate random user id
    
    #send input to amazon lex
    response = lex.post_text(
        botName = 'searchPhotos',                 
        botAlias = 'searchPhotos_first',
        userId = userId,           
        inputText = query
    )

    # print("Bot response: ", response)
    queryLabels = []

    if 'slots' not in response:
        print("Photos not found.")
    else:
        print ("Slots: ", response['slots'])
        #get labels from slots and add to array of labels
        slots = response['slots']
        for key, value in slots.items():
            if value != None:
                queryLabels.append(value)
    print("Query Labels: ", queryLabels)
    return queryLabels

def getPhotos(labels):
    os = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        pool_maxsize = 20
    )

    r = []
    for label in labels:
        if (label is not None) and label != '':
            data = os.search({"query": {"match": {"labels": label}}})
            r.append(data)
    print("Show me r: ", r)

    result = []
    for res in r: 
        if 'hits' in res:
            for value in res['hits']['hits']:
                key = value['_source']['objectKey']
                if key not in result: 
                    result.append(key)

    print("Show me result: ", result)
    return result

# Lambda execution starts here
def lambda_handler(event, context):
    # print('Codebuild test! :)')
    print('Pipeline test!')
    print("Event: ", event)
    query = event['queryStringParameters']['q']
    print("Query: ", query)

    queryLabels = getQueryLabels(query)
    
    if len(queryLabels) != 0:
        images = getPhotos(queryLabels)
        
        responseBody = {
            'images': images,
            'userQuery': query,
            'labels': queryLabels
        }

    if not images: 
        return{
            'statusCode' : 200,
            'headers': {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps('No photos matching your query.'),
            'isBase64Encoded': False
        }
    else: 
        return{
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin":"*"},
            'body': json.dumps(responseBody),
            'isBase64Encoded': False
        }