# -*- coding: utf-8 -*-

import json
import logging as log
import os


import boto3

import cfnresponse

log.getLogger().setLevel(log.INFO)

_ddb_res = boto3.resource("dynamodb")


def _ddb_load_data(table_name):
    _res = 400
    table = _ddb_res.Table(table_name)
    movie_list = [
        {
            "year": "2013",
            "title": "Rush",
            "rating": "8.3",
        },
        {
            "year": "2013",
            "title": "Prisoners",
            "rating": "8.2"
        },
        {
            "year": "2013",
            "title": "The Hunger Games: Catching Fire",
        },
        {
            "year": "2013",
            "title": "Thor: The Dark World",
        },
        {
            "year": "2013",
            "title": "This Is the End",
            "rating": "7.2",
        },
        {
            "year": "2013",
            "title": "Insidious: Chapter 2",
            "rating": "7.1",
        },
        {
            "year": "2013",
            "title": "World War Z",
            "rating": "7.1"
        },
        {
            "year": "2014",
            "title": "X-Men: Days of Future Past",
        },
        {
            "year": "2014",
            "title": "Transformers: Age of Extinction",
        },
        {
            "year": "2013",
            "title": "Now You See Me",
            "rating": "7.3",
        }
    ]
    try:
        for idx, val in enumerate(movie_list):
            val["id"] = str(idx)
            r = table.put_item(Item=val)
            log.debug(json.dumps(r, indent=2))
        _res = 200
    except Exception as e:
        log.error(f"DataLoadStatus: {str(e)}")
    return _res


def lambda_handler(event, context):
    log.info(f"event: {event}")
    physical_id = 'MystiqueAutomationCustomRes'

    try:
        # MINE
        cfn_stack_name = event.get("StackId").split("/")[-2]
        resource_id = event.get("LogicalResourceId")
        res = ""
        table_name = event.get("ResourceProperties").get("Ddb_table_name")

        if event["RequestType"] == "Create" and event["ResourceProperties"].get("FailCreate", False):
            log.info(f"FailCreate")
            raise RuntimeError("Create failure requested")
        if event["RequestType"] == "Create":
            res = _ddb_load_data(table_name)
        elif event["RequestType"] == "Update":
            res = "no_updates_made"
            pass
        elif event["RequestType"] == "Delete":
            res = "delete_triggered"
            pass
        else:
            log.error("FAILED!")
            return cfnresponse.send(event, context, cfnresponse.FAILED, attributes, physical_id)

        # MINE
        attributes = {
            "data_load_status": f"HTTPStatusCode-{res}"
        }
        cfnresponse.send(event, context, cfnresponse.SUCCESS,
                         attributes, physical_id)
    except Exception as e:
        log.exception(e)
        cfnresponse.send(event, context, cfnresponse.FAILED,
                         attributes, physical_id)
