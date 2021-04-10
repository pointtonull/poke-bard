#!/usr/bin/env python

from copy import copy
from decimal import Decimal
from functools import wraps, lru_cache
from time import time
import hashlib
import os
import logging

from doglessdata import DataDogMetrics
import boto3

metrics = DataDogMetrics(global_tags=["dynamodb:cache"])
logger = logging.getLogger(__name__)


def format_dynamo_record(raw_record):
    record = copy(raw_record)
    if isinstance(record, str):  # field can't be an empty string
        if record == "":
            record = "."
    elif isinstance(record, dict):
        for key, value in record.items():
            if isinstance(value, dict):
                value = format_dynamo_record(value)
            elif isinstance(value, list):
                value = [format_dynamo_record(item) for item in value]
            elif isinstance(value, float):
                value = Decimal(str(value))
            elif value == "":
                value = "."
            else:
                continue
            record[key] = value
    else:
        raise ValueError(
            f"Invalid record, {record}, {type(record)} not suported"
        )
    return record

def _hash_args(args):
    try:
        hash(args)
        return args
    except TypeError:
        try:
            ahash = hashlib.sha1(args).hexdigest()
            return ahash
        except TypeError:
            values = tuple((_hash_args(arg) for arg in args))
            return values


def _hash_kwargs(kwargs):
    try:
        hash(kwargs)
        return kwargs
    except TypeError:
        try:
            ahash = hashlib.sha1(kwargs).hexdigest()
            return ahash
        except TypeError:
            values = tuple((_hash_args(kwarg) for kwarg in kwargs))
            return values


def make_hasheable(args, kwargs):
    hasheable_args = _hash_args(args)
    hasheable_kwargs = _hash_kwargs(kwargs)
    return str((hasheable_args, hasheable_kwargs))


class Cache:
    def __init__(self, *, table_name=None, ttl=3600, dummy=False):
        self.ttl = ttl
        self.table = boto3.resource("dynamodb").Table(table_name)
        self.writer = self.table.batch_writer()
        self.dummy = dummy

    @metrics.timeit
    def get(self, key):
        if self.dummy:
            logger.debug("Dummy get")
            raise KeyError("Item not found")
        response = self.table.get_item(Key={"key": key})
        item = response.get("Item")
        if item:
            metrics.increment("cache_hit")
            return item["value"]
        else:
            metrics.increment("cache_miss")
            raise KeyError("Item not found")

    @metrics.timeit
    def put(self, key, value):
        if self.dummy:
            logger.debug("Dummy put")
            return False
        ttl = time() + self.ttl
        item = {
            "key": key,
            "value": value,
            "ttl": ttl,
        }
        item = format_dynamo_record(item)
        return self.writer.put_item(Item=item)

    @lru_cache()
    def __call__(self, function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            hasheable = make_hasheable(args, kwargs)
            try:
                result = self.get(hasheable)
            except KeyError:
                result = function(*args, **kwargs)
                self.put(hasheable, result)
            return result

        return wrapped
