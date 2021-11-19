import os
import sys
import traceback
from typing import Callable, List
from botocore import exceptions

from .Logger import logger as console


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
