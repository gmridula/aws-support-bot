import json
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError
import datetime
from datetime import timedelta

#Function get open case info for last X days
def getCaseInfoByAfterTime(daysAfterTime, status):
    try:
        client = boto3.client('support')
        afterTime = datetime.datetime.now()
        afterTime = (datetime.datetime.now() - timedelta(days=daysAfterTime))
        caseInfoByAfterTime = client.describe_cases(
        afterTime = afterTime.isoformat(), includeResolvedCases = status)  
    except ClientError as e:
        if e.response['Error']['Code'] == 'CaseIdNotFound':
            caseInfoByAfterTime = e.response['Error']['Message']
        elif e.response['Error']['Code'] == 'InternalServerError':
            caseInfoByAfterTime = e.response['Error']['Message']
        elif (e.response['Error']['Code'] == 'InvalidParameterValueException'):
            caseInfoByAfterTime = e.response['Error']['Message']
    except (ParamValidationError) as p:
         caseInfoByAfterTime = p.__dict__['kwargs']['report']
    print (caseInfoByAfterTime)
    return caseInfoByAfterTime

def filterBucketNameByKeyWord(keyWord):
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        for i in range(0,len(buckets)):
            try:
                if (keyWord in buckets[i]):
                    bucketName = buckets[i]
                    break
                    #print (bucketName)
            except ClientError as ce:
                bucketName = ce.response['Error']['Message']
    except (ClientError) as e:
     if (e.response['Error']['Code'] == 'InvalidParameterValueException'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'AccessDenied'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'AccountProblem'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'InternalError'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'InvalidBucketName'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'InvalidRequest'):
         json_data = e.response['Error']['Message']
    except (ParamValidationError) as p:
         json_data = p.__dict__['kwargs']['report']
    return bucketName

def readEmailListFromS3(bucketName, verifyEmailFileName):
    try:
        #Create s3 object and access emailList.json from S3 bucket
        s3 = boto3.resource('s3')
        localverifyEmailFileName = '/tmp/'+verifyEmailFileName
        s3.meta.client.download_file(bucketName,verifyEmailFileName,localverifyEmailFileName)
        with open(localverifyEmailFileName) as json_file:  
            #json_data = json.load(json_file)
            try:
                json_data = json.load(json_file)
            except json.JSONDecodeError:
                raise ValueError('Error in decoding json:'+verifyEmailFileName)
    
    except (ClientError) as e:
     if (e.response['Error']['Code'] == 'InvalidParameterValueException'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'AccessDenied'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'AccountProblem'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'InternalError'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'InvalidBucketName'):
         json_data = e.response['Error']['Message']
     elif (e.response['Error']['Code'] == 'InvalidRequest'):
         json_data = e.response['Error']['Message']
    except (ParamValidationError) as p:
         json_data = p.__dict__['kwargs']['report']
    return json_data