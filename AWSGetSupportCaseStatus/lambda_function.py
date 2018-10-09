import boto3
from prettytable import PrettyTable
import supportcase
import s3_utilities
import os

#caseInfoByAfterTime = supportcase.getCaseInfoByAfterTime(7)
ses = boto3.client('ses')

bucketKeyword = os.environ['bucketKeyword']
verifyEmailFileName = os.environ['verifyEmailFileName']
bucketName = s3_utilities.filterBucketNameByKeyWord(bucketKeyword)
emailJSONData = s3_utilities.readEmailListFromS3(bucketName, verifyEmailFileName)

email_from = emailJSONData['fromEmail']
email_to = s3_utilities.getToEmailAddressArray(emailJSONData['toEmail'])
email_cc = emailJSONData['fromEmail']


#email_from = 'gmridula@amazon.com'
#email_to = 'grandhi.mridula@gmail.com'
#email_cc = 'gmridula@amazon.com'
emaiL_subject = 'Need TAM Help Case Id '
email_body = 'We need your assistance with this case. Could you please check further with your team and get back to me on the details ?'

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
    
def spellDigitOutput(number):
    return (" ".join(number))

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
    speech_output = "Hello ! I am your AWS Case Status Bot! You can get the status of a case by saying. " \
                    "Case ID is 1 2 3 4 5. " \
                    
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
    if intent_name == "CaseIdIntent":
        return get_case_status(intent, session)
    elif intent_name == "EmailIsIntent":
        return send_tam_email(intent, session)
    elif intent_name == "NoEmailIsIntent":
        return good_day_message(intent, session)
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


def get_case_status(intent, session):
    card_title = intent['name']
    session_attributes = {}
    caseId = intent['slots']['caseId']['value']
    session_attributes = create_case_attributes(caseId)
    supportcase.caseId = caseId
    case_status = supportcase.getCaseInfoByDisplayId(caseId)
    if case_status == "CaseIdNotFound":
        speech_output = "The case ID " + spellDigitOutput(supportcase.caseId) + " that you provided does not exist. "
    elif case_status == "resolved":
        speech_output = "Thanks. Your case " + spellDigitOutput(supportcase.caseId) + " is in  " + case_status + \
                        " status. Have a great day!"
    else:
        speech_output = "Thanks. Your case " + spellDigitOutput(supportcase.caseId) + " is in  " + case_status + \
                        " status. Do you want your tam to look into this case ?"
    reprompt_text = "Thanks."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def create_case_attributes(case_detail):
    return {"case_detail": case_detail}

def good_day_message(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    speech_output = "Sure. Have a great day!" 
    reprompt_text = "Sure. Have a great day!" 
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 

def send_tam_email(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    session_attributes = create_case_attributes('sendemail')
    send_email()
    speech_output = "Sure. I have notified your tam to look into this case. " \
                        "Have a great day!"
    reprompt_text = "I'm not sure what your filter criteria is. " 
    send_email()
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 
def send_email():
     #response = ses.verify_email_identity(email_to)
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
                'Data': emaiL_subject + ": " + supportcase.caseId
            },
            'Body': {
                'Text': {
                    'Data': email_body
                }
            }
        }
)

