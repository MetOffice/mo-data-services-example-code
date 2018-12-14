# How to download data using an HTTP endpoint
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
   Start listening for messages from the SNS topic by running `host.py`
   with the TCP port to listen on and your API key as arguments.

  * Additional arguments are available to restrict which files are
    downloaded, based on the diagnostic name or forecast period.
    Execute the script with the `-h` flag for details.
  * The -v flag is set for verbose output.
  * The example below will listen on port 8080 and download all
    *air_temperature* and *surface_air_pressure* diagnostics, producing
    verbose output.
````
    $ python host.py -v 8080 <api_key> -d air_temperature surface_air_pressure
      * Running on http://0.0.0.0:8080/

    Press CTRL+C to quit
````

3. ### Subscribe to the SNS topic
   Inform the Met Office of the domain name or IP address of the server and the port the application is listening on. The Met Office will subscribe the endpoint to the SNS topic.

4. ### Automatically confirm the subscription
   After subscription to a service the application will automatically confirm the subscription.

5. ### Receive the downloads in the objects folder
   Downloaded files will collect in the "objects" folder.
   Files will be in [NetCDF](http://www.unidata.ucar.edu/software/netcdf/docs/netcdf_introduction.html "UCAR Netcdf documentation")  format and have diagnostics that correspond to the arguments supplied in step 2.  Note that the filenames will be entirely random, i.e. details of a file's content cannot be inferred from its name.
