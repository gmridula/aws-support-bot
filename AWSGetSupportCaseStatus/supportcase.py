import json
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError
import datetime
from datetime import timedelta

class SupportCase(object):
    def __init__(self):
        self._caseId = None

    @property
    def caseId(self):
        print("getter of caseId called")
        return self._caseId

    @caseId.setter
    def caseId(self, value):
        print("setter of caseId called")
        self._caseId = value

    @caseId.deleter
    def caseId(self):
        print("deleter of caseId called")
        del self._caseId

#Function get case status by caseId
def getCaseInfoByDisplayId(displayId):
    try:
        client = boto3.client('support')
        #Invoke boto3 client to get the case status
        caseInfoByDisplayId = client.describe_cases(displayId=displayId)
        caseStatus = caseInfoByDisplayId['cases'][0]['status']
    except ClientError as e:
        if e.response['Error']['Code'] == 'CaseIdNotFound':
            caseStatus = "CaseIdNotFound"
    return caseStatus
    

#Function get open case info for last X days

def getCaseInfoByAfterTime(daysAfterTime):
    try:
        client = boto3.client('support')
        afterTime = datetime.datetime.now()
        afterTime = (datetime.datetime.now() - timedelta(days=daysAfterTime))
        caseInfoByAfterTime = client.describe_cases(
        afterTime = afterTime.isoformat(), includeResolvedCases = True)  
    except ClientError as e:
        if e.response['Error']['Code'] == 'CaseIdNotFound':
            caseInfoByAfterTime = e.response['Error']['Message']
        elif e.response['Error']['Code'] == 'InternalServerError':
            caseInfoByAfterTime = e.response['Error']['Message']
        elif (e.response['Error']['Code'] == 'InvalidParameterValueException'):
            caseInfoByAfterTime = e.response['Error']['Message']
    except (ParamValidationError) as p:
         caseInfoByAfterTime = p.__dict__['kwargs']['report']
    return caseInfoByAfterTime