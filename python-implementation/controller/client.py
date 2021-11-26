from typing import List

from .filesystem import filesystem as fs
from .key_pair import KeyPair
from .logger import logger
from .models import Config, InstanceSchema


class InstanceManager():
    boto3_client = None
    config: Config = None
    key_pair: KeyPair = None

    def __init__(self, boto3_client, config: Config, debug: str = False):
        self.boto3_client = boto3_client
        self.config = config
        self._debug = debug
        self.instances: List[InstanceSchema] = []
        self.imageIds: List[str] = []

    def wait_until_running(self, InstanceIds: List[str]):
        # https://stackoverflow.com/a/47226579
        logger.log(f'Waiting for instance(s) to run: {InstanceIds}')
        client = self.boto3_client
        waiter = client.get_waiter('instance_running')
        waiter.wait(InstanceIds=InstanceIds)

    def create_image(self, InstanceId: str, ImageName: str):
        client = self.boto3_client

        self.wait_until_running(InstanceIds=[InstanceId])

        logger.log(f"Creating image '{ImageName}' " +
                   f"from instace with id '{InstanceId}'")

        waiter = client.get_waiter('image_available')

        image = client.create_image(InstanceId=InstanceId,
                                    NoReboot=True, Name=ImageName)
        imageId = image["ImageId"]

        waiter.wait(ImageIds=[imageId])

        self.imageIds.append(imageId)
        return imageId

    def delete_image(self, ImageId: str):
        try:
            self.boto3_client.deregister_image(ImageId=ImageId)
        except Exception as e:
            print(e)

    def create_instance(self, GroupId: str, KeyName: str, UserData: str = '') -> InstanceSchema:
        instance_config = self.config.instance_config.dict()
        logger.info("Creating Instance")

        response = self.boto3_client.run_instances(
            **instance_config,
            KeyName=KeyName,
            SecurityGroupIds=[GroupId],
            UserData=UserData,
            DryRun=self._debug,
            TagSpecifications=[{"ResourceType": "instance",
                                "Tags": [{
                                    "Key": "CreatedBy",
                                    "Value": "cicerotcv-boto3"
                                }]}])
        instance = InstanceSchema(**response['Instances'][0],
                                  ReservationId=response["ReservationId"])
        logger.success(
            f"Instance {instance.InstanceType} '{instance.InstanceId}' created.")
        fs.save_file('instance_response.json',
                     content=instance.dict(), tmp=True)
        self.instances.append(instance)
        return instance

    def fetch(self):
        filters = [{'Name': 'tag:CreatedBy', 'Values': ["cicerotcv-boto3"]}]
        response = self.boto3_client.describe_instances(Filters=filters)

        reservationIds = [i.ReservationId for i in self.instances]

        allocated_reservations = [reservation for reservation in response['Reservations']
                                  if reservation["ReservationId"] in reservationIds]

        instances: List[InstanceSchema] = []

        for reservation in allocated_reservations:
            instances += [InstanceSchema(**instance)
                          for instance in reservation["Instances"]]

        return instances

    def refresh(self, data: List[InstanceSchema] = None):
        if not data:
            data = self.fetch()
        for instance in self.instances:
            for fresh_data in data:
                if instance.InstanceId == fresh_data.InstanceId:
                    instance.State = fresh_data.State
                    instance.PublicIpAddress = fresh_data.PublicIpAddress

    def describe_instances(self):
        self.refresh()
        # fs.save_file('instance_description.json', response, tmp=True)
        return self.instances

    def terminate_instances(self):
        try:
            instanceIds = [instance.InstanceId for instance in self.instances]
            logger.info(f"Terminating instances: {instanceIds}")
            response = self.boto3_client.terminate_instances(
                InstanceIds=instanceIds)
            fs.save_file('termianting_instance.json', response, tmp=True)
        except Exception as e:
            logger.error(e)
