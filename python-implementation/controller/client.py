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
        instance = InstanceSchema(**response['Instances'][0], ReservationId=response["ReservationId"])
        save_file('instance_response.json', json.dumps(instance.dict(), indent=2, default=str), ephemeral=True)
        self.instances.append(instance)
        return instance


    def describe_instances(self):
        response = self.boto3_client.describe_instances()
        save_file('instance_description.json', json.dumps(response, indent=2, default=str), ephemeral=True)
        reservationIds = [instance.ReservationId for instance in self.instances]
        allocated_reservations = [ reservation for reservation in response['Reservations'] 
                                   if reservation["ReservationId"] in reservationIds ]
        instances:List[InstanceSchema] = []
        for reservation in allocated_reservations:
            instances += [ InstanceSchema(**instance) for instance in reservation["Instances"]]
        
        for instance in instances:
            print()
            console.log(f'  InstanceId: {instance.InstanceId} => {instance.State.Name}')
            if (instance.PublicIpAddress):
                console.log(f"  $ ssh -i ./tmp/{instance.KeyName}.key ubuntu@{instance.PublicIpAddress}")


    def terminate_instances(self):
        try:
            instanceIds = [instance.InstanceId for instance in self.instances]
            console.info(f"Terminating instances: {instanceIds}")
            response = self.boto3_client.terminate_instances(InstanceIds=instanceIds)
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
