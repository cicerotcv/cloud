from time import sleep

import boto3

from .client import InstanceManager
from .environment import Secret
from .filesystem import filesystem as fs
from .key_pair import KeyPair
from .logger import logger
from .models import Config, RegionNameOptions
from .security_groups import SecurityGroup
from .utils import all_terminated, print_public_ip, print_status

CONFIG_CLIENTS_FILENAME = 'config.clients.json'


class Region():
    region_name: str = None
    secret: Secret
    key_pair: KeyPair
    security_group: SecurityGroup
    client: InstanceManager
    boto3_client = None

    def __init__(self, region_name: RegionNameOptions, secret: Secret) -> None:
        self.secret = secret
        self.security_group = None
        self.key_pair = None
        self.client: InstanceManager = None
        self.region_name = region_name
        self.boto3_client = boto3.client('ec2', **secret.dict(),
                                         region_name=region_name)
        self.load_balancers = None

    def create_key_pair(self, KeyName: str):
        self.key_pair = KeyPair(KeyName=KeyName, client=self.boto3_client)
        self.key_pair.create()
        return self.key_pair

    def init_security_group(self, group_name: str, description: str):
        self.security_group = SecurityGroup(self.boto3_client,
                                            group_name, description)
        return self.security_group

    def init_client(self, client_model):
        models: dict = fs.load_config(CONFIG_CLIENTS_FILENAME)
        params = models.get(client_model)
        config = Config(**params, region_name=self.region_name)
        self.client = InstanceManager(self.boto3_client, config)
        return self.client

    def create_instance(self, UserData: str = ''):
        client = self.client
        group = self.security_group

        if not client or not group:
            return logger.error('You must first create a security group and load a client model')

        return client.create_instance(group.GroupId, self.key_pair.KeyName, UserData=UserData)

    def get_instances(self):
        client = self.client
        my_instances = client.describe_instances()

        return my_instances

    def wipe(self):
        self.client.terminate_instances()
        logger.log("Waiting for all instances to terminate")

        done = False
        while not done:
            sleep(10)
            instances = self.get_instances()
            for instance in instances:
                print_status(instance)
                print_public_ip(instance)
            done = all_terminated(instances)

        self.security_group.delete()
        self.key_pair.delete()
