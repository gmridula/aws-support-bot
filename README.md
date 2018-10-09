# aws-support-bot

## Skill Usage
> "Alexa, .."

> "..."

## Pre-Requisite
* Clone code from https://github.com/gmridula/aws-support-bot
* Valid AWS account

## Deploy from the AWS Serverless Application Repository
* Open the [AWS Console](https://console.aws.amazon.com), and navigate to Lambda
* Create a new lambda function using 'Create function' and select the option - 'AWS Serverless Application Repository'
* Search for 'aws-support-bot'
* Under the section - 'Configure application parameters'; application name will be defaulted as 'aws-support-bot'. Application name will be used by Serverless Application Repository to create a stack using cloudformation. User can change the application name if preferred
* Hit "Deploy". A new stack with naming convention as 'aws-serverless-repository-{application-name}' will be created and relevant resources will be deployed
* Currently for applications deployed through 'Serverless Application Repository'; there is a speciifc limitation where policies needed to be provided in form of policy templates. However policy templates for 'AWSSupport' are currently not available. Also generic policy templates for S3 and SES with no restriction to specific resource is also not available. To work-around this limitation, the stack needs to be updated manually (post deployment) as mentioned below

## Manual Update of CloudFormation Stack
* Navigate to CloudFormation and select the stack with naming convention as 'aws-serverless-repository-{application-name}'. In this case default application name is 'aws-support-bot' and so the stack will be as 'aws-serverless-repository-aws-support-bot'
* Select "Update Stack"
* Select option - "Upload a template to Amazon S3" and select template [AWS-Support-SAM.yaml]. Click Next (https://github.com/gmridula/aws-support-bot/blob/master/AWS-Support-SAM.yaml)
* Stack name will be displayed in read-only. Click Next
* Choose default options and click Next
* Acknolwedge options under 'Capabilities' section, click on "Create Change Set" and finally click on "Execute"
* This will initiate update of the cloudformation stack and the resources such as lambda functions will be updated with the specific policies that are needed for this application

## Trigger Email Validation
* Edit files ['notifytam.json'](https://github.com/gmridula/aws-support-bot/blob/master/email-verify-sample-formats/notifytam.json) and ['emailreport.json'] (https://github.com/gmridula/aws-support-bot/blob/master/email-verify-sample-formats/emailreport.json) to include relevant email address that need to be validated. 'notifytam.json' will be used for lambda function whose name contains 'AWSEmailCaseReport' and 'emailreport.json' will be used for lamda function whose name contains 'AWSGetSupportCaseStatus'
* Navigate to S3 and find bucket where bucketname contains 'supportbotemailverify'. The S3 bucket created by the stack using serverless application repository will follow the naming convention as 'aws-serverless-repository-a-supportbotemailverify-UID'. 'supportbotemailverify' is the bucket resource name used in the provided SAM template
* Upload the modified files - 'emailreport.json' and 'notifytam.json'. Make the files public
* Create / Update of these files against this speciifc bucket will trigger the lambda function that will perform email verification

## Alexa Setup
* Open the [AWS Console](https://console.aws.amazon.com), and navigate to your lambda, copy the ARN
  * Should be something like *arn:aws:lambda:us-west-2:000000000000:function:dev-alexa-anagram-username-anagram-XXXXXXXXXXXXX*
* Open the [Amazon Developer Console](https://developer.amazon.com/home.html)
  * Navigate to Alexa / Alexa Skills Kit/ Add a new Skill
  * Fill in skill information
  * Copy [abc.json](interaction-model.json) in for the interaction model
  * In Configuration, paste the copied ARN from Lambda
  * In test, enter utterance "for *apple*" and hit **Ask Anagram**

## Links
* [aws-support-bot](https://github.com/gmridula/aws-support-bot) on Github

