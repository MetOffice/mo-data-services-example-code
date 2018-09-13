# (C) British Crown Copyright 2017, Met Office
"""
A command-line utility to poll an SQS queue for notifications delivered via
SNS, and download the corresponding objects.

"""
import argparse
import json
import os.path
import requests
import sys

import boto3


DOWNLOAD_DIR = 'objects'
CHUNK_SIZE = 10 * 1024 * 1024


def download_object(url, api_key):
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    target_path = os.path.join(DOWNLOAD_DIR, url.split('/')[-1])
    headers = {'x-api-key': api_key}
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


def download_from_queue(api_key, queue_name, min_fp, max_fp, diagnostics,
                        keep_messages, verbose):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    while True:
        print("Checking queue for messages...")

        for message in queue.receive_messages(WaitTimeSeconds=2):
            message_body = json.loads(message.body)
            sns_notification = json.loads(message_body['Message'])

            # Production code should verify the SNS signature before
            # proceeding.

            if verbose:
                print(sns_notification)

            metadata = sns_notification['metadata']
            if metadata_matches(metadata, min_fp, max_fp, diagnostics):
                download_object(sns_notification['url'], api_key)

            if not keep_messages:
                message.delete()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download files in response to messages on an SQS queue.')
    parser.add_argument('queue_name', help='name of SQS queue in your account')
    parser.add_argument('api_key', help='your API key'),
    parser.add_argument('--min-fp', type=int, metavar='FORECAST_PERIOD',
                        help='minimum forecast_period')
    parser.add_argument('--max-fp', type=int, metavar='FORECAST_PERIOD',
                        help='maximum forecast_period')
    parser.add_argument('-d', '--diagnostic', nargs='+', dest='diagnostics',
                        metavar='DIAGNOSTIC',
                        help='name(s) of diagnostic parameters,'
                             ' e.g. air_temperature')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='retain messages in SQS queue after processing'
                             ' (useful when debugging)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='turn on verbose output.')
    args = parser.parse_args()
    if (args.min_fp is not None and args.max_fp is not None
            and args.max_fp < args.min_fp):
        parser.error('Maximum forecast_period must not be less than minimum'
                     ' forecast_period.')

    download_from_queue(args.api_key, args.queue_name, args.min_fp, args.max_fp,
                        args.diagnostics, args.keep, args.verbose)
