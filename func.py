#
# oci-sumologic 1.0
#
# Copyright (c) 2022, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.

import io
import json
import logging
import os
import base64
import requests
from fdk import response


# Function banner giving configuration, payload details
banner = "oci function : {} / event payload bytes : {} / sending to sumologic: {} / batch size: {} / logging level: {}"

# Sumologic environment variables (set in OCI Application Configuration)
sumologic_endpoint = os.getenv('SUMOLOGIC_ENDPOINT', 'not-configured')
max_records_per_post = int(os.getenv('MAX_RECORDS_PER_POST', '1000'))
is_sending = eval(os.getenv('SEND_TO_SUMOLOGIC', "True"))
send_as_multiline = eval(os.getenv('SEND_AS_MULT_LINE', "True"))

# Enable if the function will be processing events or logs passing through OCI Streaming
is_oci_streaming_conversion_enabled = eval(os.getenv('OCI_STREAMING_CONVERSION_ENABLED', "True"))

# Set all registered loggers to the configured log_level
logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
loggers = [logging.getLogger()] + [logging.getLogger(name) for name in logging.root.manager.loggerDict]
[logger.setLevel(logging.getLevelName(logging_level)) for logger in loggers]

# --------------------------------------------
# Functions
# --------------------------------------------


def handler(ctx, data: io.BytesIO = None):
    """
    OCI Function Entrypoint
    :param ctx: OCI Function context
    :param data: message payload bytes object
    :return: None
    """

    try:

        log_body = data.getvalue()
        logging.info(banner.format(ctx.FnName(), len(log_body), is_sending, max_records_per_post, logging_level))

        if is_oci_streaming_conversion_enabled:
            log_body = convert_oci_streaming_format(log_body)

        records_posted = post_to_sumologic(log_body)
        logging.info(f'records posted / {records_posted}')

        return response.Response(ctx, response_data=json.dumps({"status": "Success", "records_posted": records_posted}),
                                 headers={"Content-Type": "application/json"})

    except Exception as err:
        logging.error("Error in handler: {}".format(str(err)))
        raise err


def post_to_sumologic(body_bytes: bytes):
    """
    Sends each event to Sumologic
    """

    session = requests.Session()
    records_posted = 0

    try:
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
        session.mount('https://', adapter)

        http_headers = {'Content-type': 'application/json'}

        event_list = json.loads(body_bytes)
        if not isinstance(event_list, list):
            event_list = [event_list]

        #  divide the incoming payload into batches

        batch = []
        batches = [batch]

        for event in event_list:
            batch.append(event)
            if len(batch) >= max_records_per_post:
                batch = []
                batches.append(batch)

        for batch in batches:
            if len(batch) == 0 or is_sending is False:
                continue

            post_response = session.post(sumologic_endpoint, data=serialize(batch), headers=http_headers)
            if post_response.status_code != 200:
                raise Exception('error posting to API endpoint', post_response.text, post_response.reason)

            records_posted += len(batch)

    finally:
        session.close()

    return records_posted


def serialize(batch):
    """
    Serialize the event payload as either multiline or JSON array.
    """

    if send_as_multiline is True:
        converted = ''
        for record in batch:
            json_string = json.dumps(record)
            converted += json_string + '\n'
        return converted

    else:
        return json.dumps(batch)


def convert_oci_streaming_format(body_bytes: bytes):
    """
    This function detects if the body is OCI Streaming format and converts it as needed to remove OCI
    Streaming preamble / wrapper JSON if that is the case.  Otherwise, it returns the original argument value.

    :param body_bytes: fn message body
    :return: converted / original payload
    """

    converted = list()
    event_list = json.loads(body_bytes)

    # The presence of 'stream', 'partition' and 'value' attributes per message indicate
    # that the list of events are in Streaming format.

    for event in event_list:
        stream = event.get('stream')
        partition = event.get('partition')
        value = event.get('value')

        if stream and partition and value:
            bytes_value = base64.b64decode(value)
            utf8_value = bytes_value.decode('utf-8')
            converted.append(json.loads(utf8_value))

        else:
            logging.debug('OCI Streaming format not detected')
            return body_bytes

    converted_bytes = bytes(json.dumps(converted), 'ascii')
    logging.debug('OCI Streaming format detected, conversion complete')

    return converted_bytes


def local_test_mode(filename):
    """
    Test routine
    """

    logging.info("testing {}".format(filename))

    with open(filename, 'r') as f:
        data = json.load(f)
        converted_bytes = bytes(json.dumps(data), 'ascii')
        records_posted = post_to_sumologic(body_bytes=converted_bytes)
        logging.info(f'records posted / {records_posted}')


"""
Local Testing 
"""

if __name__ == "__main__":
    # local_test_mode('test_data/test.json')
    local_test_mode('test_data/test-list.json')
