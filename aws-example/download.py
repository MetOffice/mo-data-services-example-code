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


def download_object(url, api_key, verbose):
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


def download_from_queue(api_key, queue_name, start_time, end_time, diagnostics,
                        keep_messages, verbose):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    while True:
        print("Checking queue for messages...")

        for message in queue.receive_messages(WaitTimeSeconds=2):

            message_body = json.loads(message.body)
            message_type = message_body['Type']

            # Confirm the subscription to the SNS topic
            if message_type == 'SubscriptionConfirmation':
                requests.get(message_body['SubscribeURL'])

            # Handle the actual message
            elif message_type == 'Notification':
                sns_notification = json.loads(message_body['Message'])

                # Production code should verify the SNS signature before
                # proceeding.

                if verbose:
                    print(sns_notification)

                if not diagnostics or sns_notification['metadata']['name'] in diagnostics:
                    if int(sns_notification['metadata']['forecast_period']) >= start_time:
                        if int(sns_notification['metadata']['forecast_period']) <= end_time:
                            download_object(sns_notification['url'], api_key, verbose)

            if not keep_messages:
                message.delete()


def check_times(start_time, end_time):
    if (start_time > end_time):
        raise ValueError('End time should be greater than or equal to start time')
    return (start_time * 60 * 60, end_time * 60 * 60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download objects identified in S3 events delivered'
                    ' to an SQS queue.')
    parser.add_argument('api_key', help='Please input your authentication key'),
    parser.add_argument('queue_name')
    parser.add_argument('start_time', type=int)
    parser.add_argument('end_time', type=int)
    parser.add_argument('diagnostic', nargs='?')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='Retain messages in SQS queue after processing.'
                             ' (Useful when debugging.)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on verbose output.')
    args = parser.parse_args()

    (start_time, end_time) = check_times(args.start_time, args.end_time)

    download_from_queue(args.api_key, args.queue_name, start_time, end_time,
                        args.diagnostic.split(','), args.keep, args.verbose)
