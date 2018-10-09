import json
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError
from random import *

#Function to create support cases
def create_support_case(subject, serviceCode, severityCode, categoryCode, communicationBody, issueType):
    try:
        client = boto3.client('support')
        #Invoke boto3 create_case api
        responseCreateSupportCase = client.create_case(
            subject=subject,
            serviceCode=serviceCode,
            severityCode=severityCode,
            categoryCode=categoryCode,
            communicationBody=communicationBody,
            issueType=issueType,
            language='en')
        caseReport = responseCreateSupportCase['caseId']
    #Error Handling
    except (ClientError) as e:
        if (e.response['Error']['Code'] == 'InvalidParameterValueException'):
         caseReport = "Error Occured " + e.response['Error']['Message']
        elif (e.response['Error']['Code'] == 'CaseCreationLimitExceeded'):
         caseReport = "Error Occured " + e.response['Error']['Message']
        elif (e.response['Error']['Code'] == 'InternalServerError'):
         caseReport = "Error Occured " + e.response['Error']['Message']
    except (ParamValidationError) as p:
         caseReport = "Error Occured " + p.__dict__['kwargs']['report']
    return caseReport
    
    
#Function get display Id by caseId
def getDisplayId(caseId):
    try:
        client = boto3.client('support')
        #Invoke boto3 client to get the case status
        caseInfo = client.describe_cases(caseIdList=[
        caseId])
        displayId = caseInfo['cases'][0]['displayId']
    except ClientError as e:
        if e.response['Error']['Code'] == 'CaseIdNotFound':
            displayId = "CaseIdNotFound"
    return displayId