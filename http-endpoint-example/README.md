# How to download Met Office model data using an HTTP endpoint
A demonstration code example of downloading objects in response to SNS messages via an HTTP endpoint.

By using the following you will be able to subscribe to an Amazon Web Services (AWS) Simple Notification Service (SNS) topic and start downloading objects.
The running python script will accept notifications from the SNS topic and download the objects according to the input parameters.


## Prerequisites:

  * A service API key
  * A Python 3 environment containing the [Flask](http://flask.pocoo.org/docs/0.12/ "Flask library") and [Requests](http://docs.python-requests.org/en/master/ "Requests library") libraries
  * A server with a Public IP or DNS address with an open port. Ports other than standard http/https are [not recommended](https://aws.amazon.com/sns/faqs/ "AWS documentation")
  * A method of [verifying the messages are from AWS](http://docs.aws.amazon.com/sns/latest/dg/SendMessageToHttp.verify.signature.html "AWS documentation")

# Actions:
1. ### Clone the repository onto the server

2. ### Listen for notifications
   Start polling the SNS topic by running host.py with the following command
````
  python host.py <port> <api_key> <start_time> <end_time> <comma_separated_diagnostic_names>
````
  * The port argument is the port you want the service to listen on
  * Note that the start and end times are the forecast times (i.e. T+ times), in hours e.g. 0 to 24, up to a maximum of 144 hours (6 days).
    * The *start_time* is the start of the forecast period
    * The *end_time* is the end of the forecast period
  * The *comma_separated_diagnostic_names* argument should be a comma separated, no white spaces list of the diagnostics you want to download. The *temperature* argument returns the diagnostic **_surface_temperature_**,
   *pressure* returns **_surface_air_pressure_** and *humidity* returns **_relative_humidity_**.
   All diagnostic name strings other than *temperature*, *pressure* and *humidity* are ignored.
  * The -v flag is set for verbose output.
  * The example below will download all *surface_temperature* and *surface_air_pressure* diagnostics for time periods between T+6 and T+24 with verbose output that will listen on port 8080
````
    $ python host.py -v 8080 <api_key> 6 24 temperature,pressure
      * Running on http://0.0.0.0:8080/

    Press CTRL+C to quit
````

3. ### Subscribe to the SNS topic
   Inform the Met Office of the domain name or IP address of the server and the port the application is listening on. The Met Office will subscribe the endpoint to the SNS topic.

4. ### Automatically confirm the subscription
   After subscription to a service the application will automatically confirm the subscription.

5. ### Receive the downloads in the objects folder
   Downloaded files will collect in the "objects" folder.
   Files will be in [NetCDF](http://www.unidata.ucar.edu/software/netcdf/docs/netcdf_introduction.html "UCAR Netcdf documentation") format and have diagnostics
   that correspond to the arguments supplied in step 2.
