# -*- encoding utf-8 -*-
from time import sleep
from typing import Dict

import boto3

from controller.environment import Secret
from controller.logger import Logger
from controller.models import Config
from controller.client import Client
from controller.utils import attr_guard, from_json
from controller.utils import load_file, random_str, slugify, ephemerals, wipe_files

console = Logger()


class Session():
    # instances: List[str] = None
    _secret: Secret = None
    _config: Dict[str, Config] = None
    _clients: Dict[str, Client] = {}

    def __init__(self):
        self._secret = Secret('.env')
        self._config = {key: Config(**value)
                        for key, value in from_json('config.json').items()}

    def load_client(self, config_model: str):
        try:
            config = self._config[config_model]
        except KeyError:
            console.error(
                f"Config model '{config_model}' doesn't exist in config.json")
            exit(1)

        client = boto3.client(config.client_type,
                              region_name=config.region_name,
                              **self._secret.dict())

        custom_client = Client(client, config)
        self._clients[config_model] = custom_client
        return custom_client

    # def create_security_group(self):
    #     pass

    # def create_instance(self):
    #     pass

    # def create_iam(self):
    #     pass

    def wipe(self):
        for client_name, client in self._clients.items():
            console.info(f"Wiping client with name '{client_name}'")
            for instance in client.instances:
                client.terminate_instance(instance.InstanceId)
            client.key_pair.delete()


class ContextManager():
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self.session

    def __exit__(self, type, value, traceback):
        console.success("Successfully exiting context manager")
        self.session.wipe()
        wipe_files()


if __name__ == "__main__":

    with ContextManager() as session:

        webserver = session.load_client('webserver')
        key_pair = webserver.create_key_pair('webserver')

        ec2_instance = webserver.create_instance()
        sleep(5)
        webserver.describe_instances()

        # for instance in webserver.instances:
        #     webserver.terminate_instance(instance.InstanceId)
