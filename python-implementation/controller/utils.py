import json
import os
import random
import re
import string
import sys
import traceback
import unicodedata
from typing import Callable, List

from botocore import exceptions

from .logger import logger
from .models import InstanceSchema


def hide(string: str, digits: int = 10) -> str:
    return min(len(string), digits)*"*"


def ensure_dir_exists(relative_path: str) -> None:
    if not os.path.exists(relative_path):
        os.makedirs(relative_path)
        logger.warn(f"Path '{relative_path}' created.")


def random_str(length: int = 6) -> str:
    lower = string.ascii_lowercase
    digits = string.digits
    options = lower + digits
    return ''.join((random.choice(options)) for _ in range(length))


def slugify(value: str) -> str:
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.

    source: https://stackoverflow.com/a/27264385
    """
    value = unicodedata.normalize('NFKD', value).encode(
        'ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value).strip('-')


def all_ready(instances: List[InstanceSchema]):
    def is_running(i): return i.State.Name == "running"
    return all([is_running(instance) for instance in instances])


def all_terminated(instances: List[InstanceSchema]):
    def is_terminated(i): return i.State.Name == "terminated"
    return all([is_terminated(instance) for instance in instances])


def print_status(instance: InstanceSchema, indent: int = 2):
    spaces = ' '*indent
    logger.log(f'{spaces}{instance.InstanceId} => {instance.State.Name}')


def print_public_ip(instance: InstanceSchema, indent: int = 2):
    spaces = ' '*indent
    if (instance.PublicIpAddress):
        logger.log(
            f'{spaces}$ ssh -i ./tmp/{instance.KeyName}.key ubuntu@{instance.PublicIpAddress}')


def print_json(dict):
    print(json.dumps(dict, indent=2, default=str))


def replace(file: str, credentials: dict):
    for (key, value) in credentials.items():
        key = "{" + key + "}"
        file = file.replace(f'${key}', str(value))
    return file


def make_kp_name(region_name: str) -> str:
    return f"key-{region_name}"


def make_rule(port: int, CidrIp: str = "0.0.0.0/0"):
    return {
        'IpProtocol': 'tcp',
        'FromPort': port,
        'ToPort': port,
        'IpRanges': [{"CidrIp": CidrIp}]
    }


def make_sg_name(region_name: str) -> str:
    return f'group-{region_name}'


def make_sg_description(region_name: str) -> str:
    return f'::{region_name} Security Group::'


def make_availability_zones(region_name: str):
    return [f'{region_name}{sfx}' for sfx in list('abcd')]


def full_stack() -> str:
    exc = sys.exc_info()[0]

    stack = traceback.extract_stack()[:-1]

    trc = '\nTraceback (most recent call last):\n'
    stacklist = traceback.format_list(stack)
    del stacklist[-1]

    stackstr = trc + ''.join(stacklist)

    return stackstr


def attr_guard(*attrs: List[str]) -> Callable:
    def decorator(function: Callable):
        def wrapper(*args, **kwargs):
            self = args[0]
            null_attrs = [attr for attr in attrs
                          if getattr(self, attr) == None]
            if len(null_attrs) == 0:
                return function(*args, **kwargs)
            stack = full_stack()
            logger.error(stack)
            logger.error(
                f"Error calling {self.__class__.__name__}.{function.__name__}")
            to_be = 'is' if len(null_attrs) == 1 else 'are'
            logger.error(f"{', '.join(null_attrs)} {to_be} None")
            exit(1)
        return wrapper
    return decorator


def client_guard(class_method: Callable):
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return class_method(*args, **kwargs)
        except exceptions.ClientError as e:
            stack = full_stack()
            error = e.response["Error"]

            operation = e.operation_name
            code = error["Code"]
            message = error["Message"]

            logger.error(stack)
            logger.error(
                f"Error calling {self.__class__.__name__}.{class_method.__name__}")
            logger.info(f"{operation} {code} {message}")
            exit(1)
    return wrapper
