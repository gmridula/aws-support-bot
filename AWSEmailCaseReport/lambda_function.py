import boto3
from prettytable import PrettyTable
import support_api
import json
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError
import os
import re
import s3_utilities


ses = boto3.client('ses')

bucketKeyword = os.environ['bucketKeyword']
verifyEmailFileName = os.environ['verifyEmailFileName']
bucketName = s3_utilities.filterBucketNameByKeyWord(bucketKeyword)
emailJSONData = s3_utilities.readEmailListFromS3(bucketName, verifyEmailFileName)
email_from = emailJSONData['fromEmail']
email_to = s3_utilities.getToEmailAddressArray(emailJSONData['toEmail'])
#email_to = 'grandhi.mridula@gmail.com'
#email_from = 'grandhi.mridula@gmail.com'
#email_cc = 'grandhi.mridula@gmail.com'

email_cc = emailJSONData['fromEmail']
emaiL_subject = 'AWS Support Cases Notification'
count = ''

# --------------- Main handler ------------------
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
   
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    
    
    

    
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the AWS Notify Support Center! " \
                    "Please tell me your filter criteria. " \
                    "You have three options. " \
                    "Open Cases From the Last 7 or 14 Days. " \
                    "All Cases From the Last 7 or 14 Days. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your case type."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa! " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
        
# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "FilterCriteriaIntent":
        return set_filter_in_session(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def set_filter_in_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    # Set Default Count of days to 14
    count = 14
    status = False
    
    if 'status' in intent['slots']:
        case_status = intent['slots']['status']['value']
        
    if 'count' in intent['slots']:
        count = intent['slots']['count']['value']
        
    if case_status == "open" or case_status == "opened":
        status = False
    else:
        status = True
        
    session_attributes = create_case_attributes(status)
    caseDetail = support_api.getCaseInfoByAfterTime(int(count), status)
    send_email(caseDetail)
    speech_output = "Thanks. Your case report has been emailed to " + ','.join(email_to)
    reprompt_text = "Thanks."
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def create_case_attributes(case_detail):
    return {"case_detail": case_detail}

def send_email(caseDetail):
    case_report_table = PrettyTable(['Case ID', 'Case Description', 'Created Date', 'Status', 'Case Severity'])
    # Align content to the left side
    case_report_table.align = 'l'
    if len(caseDetail['cases']) > 0:
        for i in range(0, len(caseDetail['cases'])-1):
            case_report_table.add_row([caseDetail['cases'][i]['displayId'], 
            caseDetail['cases'][i]['subject'], caseDetail['cases'][i]['timeCreated'].split("T")[0], 
            caseDetail['cases'][i]['status'], caseDetail['cases'][i]['severityCode']])
        email_body = 'AWS Case Report\n'
        email_body += str(case_report_table)
        email_body += '\n\n'
    else:
        email_body = "No cases found\n"
    emailTo = email_to
    response = ses.send_email(
        Source = email_from,
        Destination={
            'ToAddresses': emailTo,
            'CcAddresses': [
                email_cc,
            ]
        },
        Message={
            'Subject': {
                'Data': emaiL_subject
            },
            'Body': {
                'Text': {
                    'Data': email_body
                }
            }
        }
)


