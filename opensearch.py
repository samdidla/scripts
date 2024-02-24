import boto3
import requests
from requests_aws4auth import AWS4Auth
 
host = 'https://vpc-fhnprod-fhnprod-hx7aevccgr5w6iufotvq73yxz4.us-east-2.es.amazonaws.com/' # domain endpoint with trailing /
region = 'us-east-2' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
 
path = '_snapshot/my-snapshot-repo-name-1/my-snapshot/_restore'
url = host + path
 
 
r = requests.post(url, auth=awsauth, verify=False)
 
print(r.status_code)
print(r.text)