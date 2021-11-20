import json
from typing import List
from .models import Config, InstanceSchema
from .utils import attr_guard, save_file, slugify
from .key_pair import KeyPair
from .logger import Logger

console = Logger()

class Client():
    boto3_client = None
    config: Config = None
    key_pair: KeyPair = None

    def __init__(self, boto3_client, config: Config, debug: str = False):
        self.boto3_client = boto3_client
        self.config = config
        self._debug = debug
        self.instances: List[InstanceSchema] = []


    @attr_guard('key_pair')
    def create_instance(self, UserData: str = '') -> InstanceSchema:
        instance_config = self.config.instance_config.dict()
        console.info("Creating Instance")
        response = self.boto3_client.run_instances(
            **instance_config,
            KeyName=self.key_pair.KeyName,
            # security group = default
            UserData=UserData,
            DryRun=self._debug
        )
        instance = InstanceSchema(**response['Instances'][0])
        instance_response = response["Instances"][0]
        save_file('instance_response.json', json.dumps(instance_response, indent=2, default=str), ephemeral=True)
        self.instances.append(instance)
        return instance


    def describe_instances(self):
        response = self.boto3_client.describe_instances()
        save_file('instance_description.json', json.dumps(response, indent=2, default=str), ephemeral=False)


    def terminate_instance(self, instance_id):
        console.info("Terminating instance")
        try:
            response = self.boto3_client.terminate_instances(InstanceIds=[instance_id])
            save_file('terminating_instance.json', json.dumps(response, indent=2, default=str), ephemeral=True)
        except Exception as e:
            console.error(e)


    def create_key_pair(self, KeyName: str):
        KeyName = slugify(KeyName)

        key_pair = KeyPair(KeyName=KeyName, client=self.boto3_client, debug=self._debug)

        if key_pair.exists():
            key_pair.delete()

        key_pair.create()

        self.key_pair = key_pair
        return self.key_pair
