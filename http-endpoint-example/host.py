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
ARGS = None


def get_object(url):
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    target_path = os.path.join(DOWNLOAD_DIR, url.split('/')[-1])
    headers = {'x-api-key': ARGS.api_key}
    print('Beginning download of {} to {}'.format(url, target_path))
    r = requests.get(url, headers=headers, stream=True)
    with open(target_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            fd.write(chunk)
    print('Completed download of {} to {}'.format(url, target_path))


def metadata_matches(metadata, min_fp, max_fp, diagnostics):
    match = True
    if min_fp is not None:
        match &= ('forecast_period' in metadata
                     and int(metadata['forecast_period']) >= min_fp)
    if max_fp is not None:
        match &= ('forecast_period' in metadata
                     and int(metadata['forecast_period']) <= max_fp)
    if diagnostics:
        match &= metadata.get('name') in diagnostics
    return match


def handle_message(message):
    message = json.loads(message)
    metadata = message['metadata']
    if metadata_matches(metadata, ARGS.min_fp, ARGS.max_fp, ARGS.diagnostics):
        get_object(message['url'])


@app.route('/', methods=['GET', 'POST', 'PUT'])
def sns():
    # AWS sends JSON with text/plain mimetype
    js = json.loads(request.data)
    if ARGS.verbose:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download files in response to messages to a web server.')
    parser.add_argument('port', type=int, help='TCP port for web server')
    parser.add_argument('api_key', help='your API key'),
    parser.add_argument('--min-fp', type=int, metavar='FORECAST_PERIOD',
                        help='minimum forecast_period')
    parser.add_argument('--max-fp', type=int, metavar='FORECAST_PERIOD',
                        help='maximum forecast_period')
    parser.add_argument('-d', '--diagnostic', nargs='+', dest='diagnostics',
                        metavar='DIAGNOSTIC',
                        help='name(s) of diagnostic parameters,'
                             ' e.g. air_temperature')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='turn on verbose output.')
    ARGS = parser.parse_args()
    if (ARGS.min_fp is not None and ARGS.max_fp is not None
            and ARGS.max_fp < ARGS.min_fp):
        parser.error('Maximum forecast_period must not be less than minimum'
                     ' forecast_period.')

    app.run(host="0.0.0.0", port=ARGS.port, debug=False)
