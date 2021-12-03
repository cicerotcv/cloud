from typing import List

from controller.constants import DEFAULT_TAG, DEFAULT_TAG_FILTER

from .filesystem import filesystem as fs
from .key_pair import KeyPair
from .logger import logger
from .models import Config, InstanceSchema

from .machine_image import MachineImage


class InstanceManager():
    boto3_client = None
    config: Config = None
    key_pair: KeyPair = None

    def __init__(self, boto3_client, config: Config, debug: str = False):
        self.boto3_client = boto3_client
        self.config = config
        self._debug = debug
        self.instances: List[InstanceSchema] = []

    def wait_until_running(self, InstanceIds: List[str]):
        # https://stackoverflow.com/a/47226579
        logger.log(f'Waiting for instance(s) to run: {InstanceIds}')
        client = self.boto3_client
        waiter = client.get_waiter('instance_running')
        waiter.wait(InstanceIds=InstanceIds)
        logger.log(f'Instance(s) running: {InstanceIds}')

    def wait_until_terminated(self, InstanceIds: List[str]):
        logger.log(f'Waiting for instance(s) to terminate: {InstanceIds}')
        client = self.boto3_client
        waiter = client.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=InstanceIds)
        logger.log(f'Instance(s) terminated: {InstanceIds}')

    def create_instance(self, GroupId: str, KeyName: str, UserData: str = '', wait: bool = False) -> InstanceSchema:
        instance_config = self.config.instance_config.dict()
        logger.info("Creating Instance")

        response = self.boto3_client.run_instances(
            **instance_config,
            KeyName=KeyName,
            SecurityGroupIds=[GroupId],
            UserData=UserData,
            DryRun=self._debug,
            TagSpecifications=[{"ResourceType": "instance",
                                "Tags": [DEFAULT_TAG]}])

        created_instance = response['Instances'][0]
        instance = InstanceSchema(
            **created_instance, ReservationId=response["ReservationId"])

        logger.log(f"Instance '{instance.InstanceId}' created")

        if wait:
            self.wait_until_running(InstanceIds=[instance.InstanceId])

        content = instance.dict()
        fs.save_file('instance_response.json', content=content, tmp=True)

        self.instances.append(instance)
        return instance

    def get_instances(self):
        filters = [DEFAULT_TAG_FILTER, {
            'Name': 'instance-state-name',
            'Values': ['pending', 'running', 'terminating', 'stopping', 'stopped']
        }]
        response = self.boto3_client.describe_instances(Filters=filters)

        allocated_reservations = [reservation
                                  for reservation in response['Reservations']]

        instances: List[InstanceSchema] = []

        for reservation in allocated_reservations:
            instances += [InstanceSchema(**instance)
                          for instance in reservation["Instances"]]

        return instances

    def refresh(self, data: List[InstanceSchema] = None):
        if not data:
            data = self.get_instances()
        for instance in self.instances:
            for fresh_data in data:
                if instance.InstanceId == fresh_data.InstanceId:
                    instance.State = fresh_data.State
                    instance.PublicIpAddress = fresh_data.PublicIpAddress

    def describe_instances(self):
        self.refresh()
        return self.instances

    def terminate_instances(self, InstanceIds: List[str], wait: bool = True):
        logger.log(f"Terminating instance(s): {InstanceIds}")

        terminate = self.boto3_client.terminate_instances
        response = terminate(InstanceIds=InstanceIds)

        if wait:
            self.wait_until_terminated(InstanceIds)

        return response

    def wipe(self):
        self.refresh()
        instances = self.get_instances()
        instanceIds = [instance.InstanceId for instance in instances]
        print(instanceIds)
        if len(instanceIds):
            self.terminate_instances(instanceIds, wait=True)
