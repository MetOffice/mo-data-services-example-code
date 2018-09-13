# Notification and download of data
### Timely access to data at a granular level
  This API provides whole-file access to customers who have signed up for a service.

# Prerequisites:

  * Sign up to one or more of the available data services.
  * Receive one or more API keys.
  * Receive one or more SNS topic Amazon Resource Names (ARNs) if using an AWS account.

# Actions:

   1. Set up an endpoint to receive SNS messages: either via [AWS SQS](aws-example/README.md) or [HTTP](http-endpoint-example/README.md).

   2. During model output periods, receive notifications of newly available files on the endpoint in a format similar to the following:
   ```
   {
     "Type" : "Notification",
     "MessageId" : "4f3a4169-21d7-55d4-b427-1333c7f84113",
     "TopicArn" : "arn:aws:sns:eu-west-2:123456789012:dataset-id",
     "Message" : "{\"metadata\":{\"forecast_reference_time\":\"2018-02-11T00:00:00Z\",\"forecast_period\":\"0\",\"created_time\":\"2018-02-11T04:30:25Z\",\"name\":\"air_temperature\",\"forecast_period_units\":\"seconds\"},\"url\":\"https://<service-url-supplied-by-Met-Office/id-and-version-information-of-item-requested>\"}",
     "Timestamp" : "2018-02-11T04:41:19.095Z",
     "SignatureVersion" : "1",
     "Signature" : "af0SnkRbIxaZ1P721XkkSqPdCLaIh+/Bri1uonK8n02rnjXQ6fNXJQ4HEbu0bjUB3Wm/CSHAlLc2sVWU5aFFCYABr2UBQfsrutj07dR2OmcF6WX/MHaXodWApBFrXemqpOLJ6e+KRzfGfr+rKczlpLwc9d4CQgPhA5a1eVuKlKWhoLJNuwdxcjA5FhXT/ABx3pmd+GRJ6Zk5uh/2xxV7Kt+TZ7oom/mKIOGU0YV35ki3R+t52aKEXZ43m5J/6LF8G/o1pXeMl9BJWtgdtHA9luLfN1ryNs4TmkSQxFuWXrrHTAL2iYSyxzNKB+a0gg2DfLqS9shsxAqD2HWH4/spyg==",
     "SigningCertURL" : "https://sns.eu-west-2.amazonaws.com/SimpleNotificationService-433026a4050d206028891664da859041.pem",
     "UnsubscribeURL" : "https://sns.eu-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-2:123456789012:dataset-id:bb3b1a84-728a-452a-807f-e92bd3b7d285"
   }
   ```
   Where the "message" value returned will be similar to the following example:

###### Global Model (Air Temperature):
   ```
   {
      "metadata":{
      "forecast_reference_time":"2018-02-11T00:00:00Z",
      "forecast_period":"0",
      "created_time":"2018-02-11T04:30:25Z",
      "name":"air_temperature",
      "forecast_period_units":"seconds",
      },
      "url":"https://<service-url-supplied-by-Met-Office/id-and-version-information-of-item-requested>"
   }
```


   3.  Decide by examining the metadata section in each notification which items you would like to download.


   4.  Using the url in the notification and the **API key** (see [Prerequisites](#prerequisites)) as a header called "x-api-key" request the object for download.


   5.  Receive the requested object as a file download.
