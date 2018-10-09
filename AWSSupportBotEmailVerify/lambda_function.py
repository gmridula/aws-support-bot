import json
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError
import os
import re

def lambda_handler(event, context):
    
    #s3 = boto3.client('s3')
    #s3.upload_file('email.json','adwita','email.json')
    
    
    #boto3.resource('s3').ObjectAcl('adwita','email.json').put(ACL='public-read')
    #bucketName='test'
    #bucketKeyWord = 'verify-email-bucket'
    #customerEmailVerifyFileName = 'customeremail.json'
    #tamEmailVerifyFileName = 'tamemail.json'
    #bucketName = filterBucketNameByKeyWord(bucketKeyWord)
    #tamEmailVerifyResponse = emailVerify(bucketKeyWord,tamEmailVerifyFileName)
    #bucketName = filterBucketNameByKeyWord(keyWord)
    #emailJSONData = readEmailListFromS3(bucketName, verifyEmailFileName)
    #sesFromResponse = verifyFromEmailAddress(emailJSONData['fromEmail'])
    #sesToResponse = verifyToEmailAddress(emailJSONData['toEmail'])
    bucketName = event['Records'][0]['s3']['bucket']['name']
    verifyEmailFileName = event['Records'][0]['s3']['object']['key']
    customerEmailVerifyResponse = emailVerify(bucketName,verifyEmailFileName)
    return {
        "statusCode": 200,
        "customerEmailVerifyResponse": customerEmailVerifyResponse
    }

def emailVerify(bucketName, verifyEmailFileName):
    emailJSONData = readEmailListFromS3(bucketName, verifyEmailFileName)
    sesFromResponse = verifyFromEmailAddress(emailJSONData['fromEmail'])
    sesToResponse = verifyToEmailAddress(emailJSONData['toEmail'])
    return 1

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

def verifyFromEmailAddress(emailJSONData):
    ses = boto3.client('ses')
    try:
        validateEmailAddressSyntax(emailJSONData)
    except KeyError:
        raise ValueError('Value for key - email is empty')
    try:
        response = ses.verify_email_identity(EmailAddress = emailJSONData)
    except ClientError as ce:
        response = ce.response['Error']['Message']
    else:
        print ('Email verification sent to: '+ emailJSONData)
    return response

def verifyToEmailAddress(emailJSONData):
    ses = boto3.client('ses')
    for i in emailJSONData:
        try:
            validateEmailAddressSyntax(i['email'])
        except KeyError:
            raise ValueError('Value for key - email is empty')
        try:
            response = ses.verify_email_identity(EmailAddress = i['email'])
        except ClientError as ce:
            response = ce.response['Error']['Message']
        else:
            print ('Email verification sent to: '+ i['email'])
    return response

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

def validateEmailAddressSyntax(emailAddress):
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailAddress)
    if match == None:
	    print('Verify Email Syntax for:' + emailAddress)
	    raise ValueError('Verify Email Syntax for:' + emailAddress)
    return
    
