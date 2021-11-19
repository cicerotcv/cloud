import os
import random
import re
import string
import sys
import traceback
import unicodedata
from typing import Callable, List

from botocore import exceptions

from .logger import Logger

console = Logger()


def hide(string: str, digits: int = 10) -> str:
    return min(len(string), digits)*"*"


def load_file(filename: str) -> str:
    with open(filename, mode='r', encoding='utf-8') as file:
        content = file.read()
        return content


def save_file(filename: str, content: str, mode: str = 'w+'):
    with open(filename, mode=mode, encoding='utf-8') as file:
        file.write(content)


def delete_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError as e:
        console.warn(f"File '{path}' not found. Probably deleted or moved")


def random_str(length: int = 6):
    lower = string.ascii_lowercase
    digits = string.digits
    options = lower + digits
    return ''.join((random.choice(options)) for _ in range(length))


def slugify(value):
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


def full_stack():
    exc = sys.exc_info()[0]

    stack = traceback.extract_stack()[:-1]

    # if exc is not None:
    #     del stack[-1]

    trc = '\nTraceback (most recent call last):\n'
    stacklist = traceback.format_list(stack)
    del stacklist[-1]

    stackstr = trc + ''.join(stacklist)

    # if exc is not None:
    #     stackstr += '  ' + traceback.format_exc().lstrip(trc)

    return stackstr


def attr_guard(*attrs: List[str]):
    def decorator(function: Callable):
        def wrapper(*args, **kwargs):
            self = args[0]
            null_attrs = [attr for attr in attrs
                          if getattr(self, attr) == None]
            if len(null_attrs) == 0:
                return function(*args, **kwargs)
            stack = full_stack()
            console.error(stack)
            console.error(
                f"Error calling {self.__class__.__name__}.{function.__name__}")
            to_be = 'is' if len(null_attrs) == 1 else 'are'
            console.error(f"{', '.join(null_attrs)} {to_be} None")
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

            console.error(stack)
            console.error(
                f"Error calling {self.__class__.__name__}.{class_method.__name__}")
            console.info(f"{operation} {code} {message}")
            exit(1)
    return wrapper
