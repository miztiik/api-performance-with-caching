# -*- coding: utf-8 -*-


import datetime
import json
import logging
import os
import random
import time

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


_ddb_client = boto3.client("dynamodb")


class GlobalArgs:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "greeter_lambda"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    RANDOM_SLEEP_SECS = int(os.getenv("RANDOM_SLEEP_SECS", 2))
    ANDON_CORD_PULLED = os.getenv("ANDON_CORD_PULLED", False)


def set_logging(lv=GlobalArgs.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


# Initial some defaults in global context to reduce lambda start time, when re-using container
logger = set_logging()


def random_sleep(max_seconds=10):
    if bool(random.getrandbits(1)):
        logger.info(f"sleep_start_time:{str(datetime.datetime.now())}")
        time.sleep(random.randint(0, max_seconds))
        logger.info(f"sleep_end_time:{str(datetime.datetime.now())}")


def _get_item(table_name, _hash_key, _hash_val):
    # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
    _r = ""
    try:
        res = _ddb_client.get_item(
            TableName=table_name,
            Key={
                _hash_key: {"S": _hash_val}
            }
        )
        _r = res["Item"]
    except ClientError as e:
        _r = e.response["Error"]["Message"]
        logger.error(str(e))
    return _r


def lambda_handler(event, context):
    items = ""
    logger.info(f"rcvd_event:{event}")

    table_name = os.environ.get("DDB_TABLE_NAME")

    if event.get("id"):
        m_id = str(event.get("id"))
    else:
        m_id = str(random.randint(0, 9))

    if int(m_id) < 10:
        item = _get_item(table_name, "id", m_id)
    else:
        item = "BackEnd-Lambda Response: Choose Movie id between 0 and 9"

    # random_sleep(GlobalArgs.RANDOM_SLEEP_SECS)
    return {
        "statusCode": 200,
        "body": (f'{{"message": "Hello Miztiikal World, How is it going?",'
                 f'"movie": {json.dumps(item)},'
                 f'"ts": "{str(datetime.datetime.now())}"'
                 f'}}')
    }
