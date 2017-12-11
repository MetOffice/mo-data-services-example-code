import argparse
import json
import os.path
# pprint used to make the output easier to read
import pprint

from flask import Flask, request
import requests


# Iniatilise global variables so they can be used in the handled messages
DOWNLOAD_DIR = 'objects'
CHUNK_SIZE = 10 * 1024 * 1024
app = Flask(__name__)
args = []
checked_diagnostics = ()
start_time = 0
end_time = 0


def get_object(url):
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    target_path = os.path.join(DOWNLOAD_DIR, url.split('/')[-1])
    headers = {'x-api-key': args.api_key}
    print('Beginning download of {} to {}'.format(url, target_path))
    r = requests.get(url, headers=headers, stream=True)
    with open(target_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            fd.write(chunk)
    print('Completed download of {} to {}'.format(url, target_path))


def handle_message(message):
    message = json.loads(message['metadata']['name'])
    if message['metadata']['name'] in checked_diagnostics:
        forecast_period = int(message['metadata']['forecast_period'])
        if start_time <= forecast_period <= end_time:
            get_object(message['url'])


@app.route('/', methods=['GET', 'POST', 'PUT'])
def sns():
    # AWS sends JSON with text/plain mimetype
    js = json.loads(request.data)
    if args.verbose:
        pprint.pprint(js)
    message_type = request.headers.get('x-amz-sns-message-type')

    '''
    If being used in production there should be a step here to
    verify that the message is coming from Amazon. The step to
    do this can be found here:
    http://docs.aws.amazon.com/sns/latest/dg/SendMessageToHttp.verify.signature.html
    '''

    # Confirm the subscription to the SNS topic
    if message_type == 'SubscriptionConfirmation':
        requests.get(js['SubscribeURL'])
    # Handle the actual message
    elif message_type == 'Notification':
        handle_message(js['Message'])

    return 'OK\n'


def check_times(start_time, end_time):
    if (start_time > end_time):
        raise ValueError('End time should be greater \
            than or equal to start time')
    return (start_time * 60 * 60, end_time * 60 * 60)


def check_diagnostics(diagnostics):
    '''
    Takes a list of command line arguments, and returns corresponding
    file metadata names, filtering unneeded and unrecognised items
    '''
    return_list = []
    if 'temperature' in diagnostics:
        return_list.append('surface_temperature')
    if 'pressure' in diagnostics:
        return_list.append('surface_air_pressure')
    if 'humidity' in diagnostics:
        return_list.append('relative_humidity')
    return return_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download objects identified in S3 events delivered'
                    ' to an SQS queue.')
    parser.add_argument('port', type=int)
    parser.add_argument('api_key', help='Please input your authentication key')
    parser.add_argument('start_time', type=int)
    parser.add_argument('end_time', type=int)
    parser.add_argument('diagnostic')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on verbose output.')
    args = parser.parse_args()
    (start_time, end_time) = check_times(args.start_time, args.end_time)

    checked_diagnostics = check_diagnostics(args.diagnostic.split(','))

    app.run(
        host="0.0.0.0",
        port=args.port,
        debug=False
    )
