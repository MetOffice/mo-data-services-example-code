# (C) British Crown Copyright 2017, Met Office
"""
A command-line utility to poll an SQS queue for notifications delivered via
SNS, and download the corresponding objects.

"""
import argparse
import json
import os.path
import requests
import csv
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

    with open('./output/{}-diagnostics.csv'.format(queue_name), 'w', newline='') as csv_file:
        fieldnames = ['object_url', 'diagnostic', 'forectast_reference_time', \
                      'forecast_period', 'realization', \
                      'height', 'height_units', \
                      'pressure', 'pressure_units']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames,
                                    quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writeheader()

        while True:
            print("Checking queue for messages...")

            try:
                for message in queue.receive_messages(WaitTimeSeconds=20):
                    message_body = json.loads(message.body)
                    sns_notification = json.loads(message_body['Message'])

                    # Production code should verify the SNS signature before
                    # proceeding.

                    if verbose:
                        print(sns_notification)

                    metadata = sns_notification['metadata']
                    csv_writer.writerow({'object_url': sns_notification['url'],
                                         'diagnostic': metadata['name'],
                                         'forectast_reference_time': metadata['forecast_reference_time'],
                                         'forecast_period': metadata['forecast_period'],
                                         'realization': metadata.get('realization', ''),
                                         'height': metadata.get('height',''),
                                         'height_units': metadata.get('height_units',''),
                                         'pressure': metadata.get('pressure',''),
                                         'pressure_units': metadata.get('pressure_units','')})

                    #if sns_notification['metadata']['name'] in diagnostics:
                    #    if int(sns_notification['metadata']['forecast_period']) >= start_time:
                    #        if int(sns_notification['metadata']['forecast_period']) <= end_time:
                    #            download_object(sns_notification['url'], api_key, verbose)

                    if not keep_messages:
                        message.delete()
            except:
                print("Exception processing SQS messages:", sys.exc_info()[0])


def check_times(start_time, end_time):
    if (start_time > end_time):
        raise ValueError('End time should be greater than or equal to start time')
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
    parser.add_argument('api_key', help='Please input your authentication key'),
    parser.add_argument('queue_name')
    parser.add_argument('start_time', type=int)
    parser.add_argument('end_time', type=int)
    parser.add_argument('diagnostic')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='Retain messages in SQS queue after processing.'
                             ' (Useful when debugging.)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on verbose output.')
    args = parser.parse_args()

    (start_time, end_time) = check_times(args.start_time, args.end_time)

    valid_diagnostics = check_diagnostics(args.diagnostic.split(','))


    download_from_queue(args.api_key, args.queue_name, start_time, end_time,
                        valid_diagnostics, args.keep, args.verbose)
