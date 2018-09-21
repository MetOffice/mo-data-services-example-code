# How to download data using Amazon Web Services
A demonstration code example of downloading objects in response to SNS messages via an SQS queue.

By following these instructions you will subscribe an Amazon Web Services (AWS) Simple Queue Service (SQS) queue in your
AWS account to a Met Office Simple Notification Service (SNS) topic. You will then run
a Python script to monitor the SQS queue for notifications and download the
corresponding objects from the service using an authenticating API key.

## Prerequisites

* A Met Office AWS SNS topic ARN.
* A service API key.
* An AWS account where you can create a new [SQS queue](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-create-queue.html) and [IAM policies for SQS queues](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-authentication-and-access-control.html).
* A Python 3 environment containing the [Boto3](https://boto3.readthedocs.io/en/latest/) and [Requests](http://docs.python-requests.org/en/master/ "Requests library") libraries.

## Getting started

1. ### Create an SQS queue in your account

   For an example of an AWS CloudFormation implementation, please see the AWS CloudFormation template
   included in the aws-example folder, available in JSON (cloudformation_sqs.json)
   or in YAML (cloudformation_sqs.yaml) format.
    .

   This can be built using the [AWS command line interface](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-cli-creating-stack.html).

   Substitute the place holders in the template with an [SQS queue name](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-message-identifiers.html) of your choice and the
   ARN received from the Met Office as part of your service access request.

   The template will create an SQS queue with **send-message** permissions from the service.

   The new SQS queue ARN will be visible in the **Output** section of the console.


2. ### Create an SQS Queue Policy

   The created SQS queue needs a policy (included as part of the example CloudFormation template)
   that allows the service (ARN sent in step 1) to [send messages](http://docs.aws.amazon.com/sns/latest/dg/SendMessageToSQS.html#SendMessageToSQS.sqs.permissions) to it.

   Ensure your SQS queue access policy includes the following statement:

JSON:
```
{
   "Type":"AWS::SQS::QueuePolicy",
   "Properties":{
      "PolicyDocument":{
         "Version":"2012-10-17",
         "Statement":[
            {
               "Effect":"Allow",
               "Action":["sqs:SendMessage"],
               "Resource":{
                  "Fn::GetAtt":["<your-queue-name>", "Arn"]
               },
               "Condition":{
                  "ArnEquals":{
                     "aws:SourceArn":"<insert-service-arn-supplied-by-Met-Office>"
                  }
               }
            }
         ]
      },
      "Queues":["<your-queue-name>"]
   }
}
```

YAML:
```
  SQSQueuePolicy:
    Type: AWS::SQS::QueuePolicy
    Properties:
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
        - Effect: Allow
          Principal: "*"
          Action:
          - sqs:SendMessage
          Resource: !GetAtt <your-queue-name>.Arn
          Condition:
            ArnEquals:
              aws:SourceArn: <insert-service-arn-supplied-by-Met-Office>
      Queues:
      - <your-queue-name>
```


3. ### Configure access credentials and permissions for your AWS account.

   [Configure boto3](http://boto3.readthedocs.io/en/latest/guide/configuration.html)
   for your AWS account.

   Set the AWS managed policy `AmazonSQSFullAccess` on your IAM role, or allow the specific permissions
   `sqs:DeleteMessage` and  `sqs:ReceiveMessage` for the SQS queue:

JSON:
```
{
   "Version": "2012-10-17",
   "Statement": [
      {
           "Action": [
               "sqs:DeleteMessage",
               "sqs:ReceiveMessage"
           ],
           "Effect": "Allow",
           "Resource": "arn:aws:sqs:*:<name-of-your-sqs-queue>"
      }
   ]
}
```

YAML:
```
Version: '2012-10-17'
Statement:
- Effect: Allow
  Action:
  - sqs:DeleteMessage
  - sqs:ReceiveMessage
  Resource: arn:aws:sqs:*:<name-of-your-sqs-queue>
```


4. ### Subscribe the SQS queue to the SNS topic.

   Inform the Met Office of the [SQS ARN](http://docs.aws.amazon.com/sns/latest/dg/SendMessageToSQS.html#SendMessageToSQS.arn).
   The Met Office will subscribe the queue to the service. The queue should then receive a [subscription notification](http://docs.aws.amazon.com/sns/latest/dg/SendMessageToSQS.cross.account.html#SendMessageToSQS.cross.account.notqueueowner).
   Enter the subscription confirmation URL into a browser to confirm the subscription.



5. ### Start polling the SQS queue.

   * Clone this repository and ensure it is the current directory.

   * To begin polling, execute the `download.py` script with the name of
     your SQS queue and your API key as arguments.

   * Additional arguments are available to restrict which files are
     downloaded, based on the diagnostic name or forecast period.
     Execute the script with the `-h` flag for details.

     * NB. Appropriate values for the minimum/maximum forecast period
       depend on the units declared in the files. Typically it will be
       expressed in seconds, e.g. data for T+4 hours will have a
       forecast period of 14400 seconds.

   * The `-v` flag is set for verbose output.

   * The `-k` flag set keeps messages until deleted by the user.

   Example:

   ```
   $ python download.py -d relative_humidity -k -v <queue_name> <api_key>
   Using: https://eu-west-2.queue.amazonaws.com/<subscribing-account-ID>/<queue-name>

   Checking queue for messages...
   {'metadata': {'forecast_reference_time': '2017-10-24T06:00:00Z', 'forecast_period': '0', 'created_time':'2018-03-06T06:30:25Z', 'name': 'surface_temperature', 'forecast_period_units': 'seconds'}, 'url':  'https://<service-url-supplied-by-Met-Office/id-and-version-information-of-item-requested>'}
   Checking queue for messages...
   {'metadata': {'forecast_reference_time': '2017-10-24T06:00:00Z', 'forecast_period': '0', 'created_time':'2018-03-06T06:30:26Z', 'name': 'dew_point_temperature', 'forecast_period_units': 'seconds'}, 'url':  'https://<service-url-supplied-by-Met-Office/id-and-version-information-of-item-requested>'}
   Checking queue for messages...
   ...
   ```


6. ### Receive downloads in the objects folder

   Downloaded files will collect in the "objects" folder.
   Files will be in [NetCDF](http://www.unidata.ucar.edu/software/netcdf/docs/netcdf_introduction.html) format and have diagnostics
   that correspond to the arguments supplied in step 5.

   [Back to main page](../README.md)
