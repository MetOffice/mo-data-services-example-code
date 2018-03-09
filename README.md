# Notification and download of Met Office atmospheric model data
### Timely access to forecast data at a granular level
  This API provides access to UK and Global atmospheric model data to customers who have signed up for a service.

### Services available:

   - Global Model
   - MOGREPS-G Ensemble
   - UKV Model
   - MOGREPS-UK Ensemble

# Prerequisites:

  * Sign up to one or more of the Atmospheric Model data services.
  * Receive one or more API keys.
  * Receive one or more SNS topic Amazon Resource Names (ARNs) if using an AWS account.

# Actions:

   1. Set up an endpoint to receive SNS messages: either via [AWS SQS](aws-example/README.md) or [HTTP](http-endpoint-example/README.md).

   2. During model output periods, receive notifications of newly available files on the endpoint in a format similar to the following:
   ```
   {
     "Type" : "Notification",
     "MessageId" : "4f3a4169-21d7-55d4-b427-1333c7f84113",
     "TopicArn" : "arn:aws:sns:eu-west-2:271253003023:mo-atmospheric-global",
     "Message" : "{\"metadata\":{\"forecast_reference_time\":\"2017-10-07T23:00:00Z\",\"forecast_period\":\"0\",\"created_time\":\"2018-03-06T06:30:25Z\",\"name\":\"deprecated_precipitation_rate\",\"forecast_period_units\":\"seconds\"},\"url\":\"https://<service-url-supplied-by-Met-Office/id-and-version-information-of-item-requested>\"}",
     "Timestamp" : "2017-10-13T16:03:59.095Z",
     "SignatureVersion" : "1",
     "Signature" : "af0SnkRbIxaZ1P721XkkSqPdCLaIh+/Bri1uonK8n02rnjXQ6fNXJQ4HEbu0bjUB3Wm/CSHAlLc2sVWU5aFFCYABr2UBQfsrutj07dR2OmcF6WX/MHaXodWApBFrXemqpOLJ6e+KRzfGfr+rKczlpLwc9d4CQgPhA5a1eVuKlKWhoLJNuwdxcjA5FhXT/ABx3pmd+GRJ6Zk5uh/2xxV7Kt+TZ7oom/mKIOGU0YV35ki3R+t52aKEXZ43m5J/6LF8G/o1pXeMl9BJWtgdtHA9luLfN1ryNs4TmkSQxFuWXrrHTAL2iYSyxzNKB+a0gg2DfLqS9shsxAqD2HWH4/spyg==",
     "SigningCertURL" : "https://sns.eu-west-2.amazonaws.com/SimpleNotificationService-433026a4050d206028891664da859041.pem",
     "UnsubscribeURL" : "https://sns.eu-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-2:271253003023:mo-atmospheric-global:bb3b1a84-728a-452a-807f-e92bd3b7d285"
   }
   ```
   Where the "message" value returned will be similar to the following example:

###### Global Model (Air Temperature):
   ```
   {
      "metadata":{
      "forecast_reference_time":"2017-10-15T00:00:00Z",
      "forecast_period":"0",
      "created_time":"2018-03-06T06:30:25Z",
      "name":"air_temperature",
      "forecast_period_units":"seconds",
      "height_units":"m",
      "height":"5.0 10.0 20.0 30.0 50.0 75.0 100.0 150.0 200.0 250.0 300.0 400.0 500.0 600.0 700.0 800.0 1000.0 1250.0 1500.0 1750.0 2000.0 2250.0 2500.0 2750.0 3000.0 3250.0 3500.0 3750.0 4000.0 4500.0 5000.0 5500.0 6000.0"
      },
      "url":"https://<service-url-supplied-by-Met-Office/id-and-version-information-of-item-requested>"
   }
```


   3.  Decide by examining the metadata section in each notification which items you would like to download.


   4.  Using the url in the notification and the **API key** (see [Prerequisites](#prerequisites)) as a header called "x-api-key" request the object for download.


   5.  Receive the requested object as a file download.
