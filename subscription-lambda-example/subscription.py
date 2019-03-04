import json
import os

import boto3
import urllib.request

def lambda_handler(event, context):
    """
    Confirms lotus confirmation notifications.
    """
    try:
        records = event['Records']
        for record in Records:
            body = json.loads(record['body'])

            # handle any lotus subscription confirmations automatically
            if body['Type'] == 'SubscriptionConfirmation':
                confirm_lotus_subscription(body['SubscribeURL'])
            return
    except Exception as e:
        print('there was an error processing the event.')
    finally:
        print('done')


def confirm_lotus_subscription(confirmation_url):
    """Confirms Lotus subscription notifications otherwise throws an AssertionError"""
    response = urllib.request.urlopen(confirmation_url)
    assert (response.getcode() == 200), 'Lotus subscription confirmation returned {}'.format(response.getcode())
    print('Lotus subscription confirmation has been confirmed.')