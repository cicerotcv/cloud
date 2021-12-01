from typing import List

import boto3

from .logger import logger
from .models import InstanceSchema


class LaunchConfiguration():
    def __init__(self, region_name: str, secret: dict) -> None:
        self.secret = secret
        self.region_name = region_name
        self.name = "lc-" + region_name

        self.client = self.__boto3()

    def __boto3(self):
        rn = self.region_name
        secret = self.secret
        return boto3.client('autoscaling', region_name=rn, **secret)

    def create(self, imageId: str,  instanceType: str, keyName: str, groupIds: List[str], UserData: str = ''):
        self.delete_if_exist()
        logger.log(f"Creating LaunchConfiguration '{self.name}'")
        self.client.create_launch_configuration(
            LaunchConfigurationName=self.name,
            ImageId=imageId,
            KeyName=keyName,
            SecurityGroups=groupIds,
            InstanceType=instanceType,
            UserData=UserData)
        logger.log(f"  LaunchConfiguration '{self.name}' created")

    def create_from_instance(self, instance: InstanceSchema, ImageId: str, SecurityGroupId: str, UserData: str = ''):
        return self.create(
            imageId=ImageId,
            instanceType=instance.InstanceType,
            keyName=instance.KeyName,
            groupIds=[SecurityGroupId],
            UserData=UserData)

    def get_launch_configurations(self):
        describe = self.client.describe_launch_configurations
        response = describe(LaunchConfigurationNames=[self.name])
        return response.get("LaunchConfigurations", [])

    def exists(self):
        lcs = self.get_launch_configurations()
        for lc in lcs:
            if lc['LaunchConfigurationName'] == self.name:
                return True
        return False

    def delete_if_exist(self):
        if self.exists():
            logger.log(f"LaunchConfiguration '{self.name}' already exists")
            self.delete()

    def delete(self):
        logger.log(f"Deleting LaunchConfiguration '{self.name}'")
        delete = self.client.delete_launch_configuration
        delete(LaunchConfigurationName=self.name)
        logger.log(f"  LaunchConfiguration '{self.name}' deleted")

    def wipe(self):
        self.delete_if_exist()
