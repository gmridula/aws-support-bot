"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
from __future__ import print_function
import Support
import support_api_function
import lambda_utils

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
    speech_output = "Welcome to the Alexa AWS Support Center! " \
                    "Lets start with your Support case Creation. "\
                    "Please tell me your case type. " \
                    "You have two options to choose. " \
                    "Customer Service or Technical " 
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your case type."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_service_response():
    session_attributes = {}
    speech_output = "Now, please tell me what service you would like to create the case for " 
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your service."
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


def create_case_attributes(case_detail):
    return {"case_detail": case_detail}
    

def set_case_in_session(intent, session):
    """ Sets the case type in the session and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'CaseType' in intent['slots']:
        case_type = intent['slots']['CaseType']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        Support.caseType = case_type
        session_attributes = create_case_attributes(case_type)
        speech_output = "Next, tell me your service"
        reprompt_text = "Next, tell me your service"
    else:
        speech_output = "I'm not sure what your case type is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your case type is. " \
                        "You can tell me your case type by saying, " \
                        "my case type is Technical Support."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
        
def set_service_in_session(intent, session):
    """ Sets the service type in the session and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'ServiceType' in intent['slots']:
        service = intent['slots']['ServiceType']['value']
        Support.serviceType = intent['slots']['ServiceType']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        session_attributes = create_case_attributes(service)
        Support.categoryList = lambda_utils.getCategoryListByServiceCode(Support.serviceType)
        textOptions = ', '.join(Support.categoryList)
        speech_output = "For " + service + ", your category options are .  " + \
                        textOptions + \
                        ". You can select a category by saying. Category is General guidance"
        
        reprompt_text = "For " + service + " You have the following options to choose the Category from "
    else:
        speech_output = "I'm not sure what your category type is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your category type is. " 
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def set_category_in_session(intent, session):
    """ Sets the category in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Category' in intent['slots']:
        category = intent['slots']['Category']['value']
        Support.category = intent['slots']['Category']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        session_attributes = create_case_attributes(category)
        speech_output = "Next, select the severity by saying " \
        "Severity is General Guidance or System Impaired or Production System Impaired or Prod System Down."
                       
        reprompt_text = "You can tell me the severity by saying, " \
                        "Severity is General Guidance or System Impaired or Production System Impaired or Prod System Down."
    else:
        speech_output = "I'm not sure what your severity is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your severity is. " 
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def set_severity_in_session(intent, session):
    """ Sets the Severity and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'SeverityType' in intent['slots']:
        severity = intent['slots']['SeverityType']['value']
        Support.severityType = intent['slots']['SeverityType']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        session_attributes = create_case_attributes(severity)
        speech_output = "Next, tell me the subject."
                       
        reprompt_text = "Please tell me the subject. " 
    else:
        speech_output = "I'm not sure what your subject is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your subject is. " 
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_subject_in_session(intent, session):
    """ Sets the Subject and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Subject' in intent['slots']:
        subject = intent['slots']['Subject']['value']
        Support.subject = subject
        session_attributes = create_case_attributes(subject)
        speech_output = "Next, tell me more about the issue."
                       
        reprompt_text = "Please describe the issue. " 
    else:
        speech_output = "I'm not sure what your description is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your description is. " 
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

    
def set_description_in_session(intent, session):
    """ Sets the Description
    and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Description' in intent['slots']:
        description = intent['slots']['Description']['value']
        Support.description = description
        session_attributes = create_case_attributes(description)
        
        speech_output = "I now have your case details for case type. " + Support.caseType + \
        " Service is ." + Support.serviceType + " category is " + Support.category + \
        " Severity is " + Support.severityType + " Subject is " + Support.subject + \
        " And Case Description is " + Support.description + ". Can I go ahead and create a case with these details ?"
        reprompt_text = "Here are the case details. " 
    else:
        speech_output = "There has been an issue. " \
                        "Please try again."
        reprompt_text = "There is an issue. " 
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def spellDigitOutput(number):
    return (" ".join(number))

def set_confirm_intent(intent, session):
    """ Sets the Subject and prepares the speech to reply to the
    user.
    """
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    session_attributes = create_case_attributes("confirm")
    if 'Confirm' in intent['slots']:
        confirm = intent['slots']['Confirm']['value']
        if confirm.upper() == "YES":
            caseId = support_api_function.create_support_case(Support.subject, Support.serviceType, 
            Support.severityType, Support.category, Support.description, Support.caseType)
            if "Error" not in caseId:
                displayId = support_api_function.getDisplayId(caseId)
                speech_output = "Case Created successfully! Your Case ID is " + spellDigitOutput(displayId) + " Have a great day!"
                reprompt_text = "Have a great day!"
    else:
        speech_output = "I'm not sure if you want to submit the case " \
                        "Please try again."
        reprompt_text = "I'm not sure if you want to submit the case. "
   
     # deleter called
    del Support.caseType      
    del Support.serviceType
    del Support.category
    del Support.severityType
    del Support.subject
    del Support.description
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_case_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "case_detail" in session.get('attributes', {}):
        case_detail = session['attributes']['case_detail']
        speech_output = "Your case type is " +  \
        case_detail + ". Now tell me your service."
        should_end_session = False
    else:
        speech_output = "I'm not sure what your case type is. " \
                        "You can say, my case type is Technical Support."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
        
def get_service_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "service" in session.get('attributes', {}):
        service = session['attributes']['service']
        speech_output = "Your service type is " + service 
        should_end_session = False
    else:
        speech_output = "I'm not sure what your service type is. " \
                        "Please try again."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
        

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
    if intent_name == "MyCaseIsIntent":
        return set_case_in_session(intent, session)
    elif intent_name == "WhatsMyCaseIntent":
        return get_case_from_session(intent, session)
    elif intent_name == "MyServiceIsIntent":
        return set_service_in_session(intent, session)
    elif intent_name == "WhatsMyServiceIntent":
        return get_service_from_session(intent, session)
    elif intent_name == "MyCategoryIsIntent":
        return set_category_in_session(intent, session)
    elif intent_name == "MySeverityIsIntent":
        return set_severity_in_session(intent, session)
    elif intent_name == "MySubjectIsIntent":
        return set_subject_in_session(intent, session)
    elif intent_name == "MyDescriptionIsIntent":
        return set_description_in_session(intent, session)
    elif intent_name == "ConfirmIntent":
        return set_confirm_intent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
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


