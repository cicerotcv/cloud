import json
from typing import List

import boto3

from controller.utils import make_availability_zones

from .logger import logger
import time
from .models import InstanceSchema

from .constants import DEFAULT_TAG


class AutoScalingWaiter():
    def __init__(self, auto_scaling) -> None:
        self.auto_scaling = auto_scaling

    def wait_until_terminated(self):
        as_name = self.auto_scaling.name
        logger.warn(f"Waiting for AutoScaling '{as_name}' to terminate")

        while self.auto_scaling.exists():
            time.sleep(10)
        time.sleep(10)
        logger.warn(f"AutoScaling '{as_name}' terminated")


class AutoScaling():
    def __init__(self, region_name: str, secret: dict) -> None:
        self.secret = secret
        self.region_name = region_name
        self.name = 'as_' + region_name
        self.client = self.__boto3()
        self.waiter = AutoScalingWaiter(self)

    def __boto3(self):
        rn = self.region_name
        secret = self.secret
        return boto3.client('autoscaling', region_name=rn, **secret)

    def create_auto_scalling(self, lc_name: str, tg_arn: str, min_size=1, max_size=3):
        self.destroy_if_exists()
        client = self.client

        logger.log(f"Creating AutoScaling '{self.name}'")
        client.create_auto_scaling_group(
            AutoScalingGroupName=self.name,
            LaunchConfigurationName=lc_name,
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=min_size,
            AvailabilityZones=make_availability_zones(self.region_name),
            TargetGroupARNs=[tg_arn],
            Tags=[{'ResourceType': 'auto-scaling-group',
                   'Key': DEFAULT_TAG['Key'],
                   'Value': DEFAULT_TAG['Value'],
                   'PropagateAtLaunch': True}]
        )
        logger.log(f"AutoScaling '{self.name}' created")

    def get_auto_scaling_groups(self):
        describe = self.client.describe_auto_scaling_groups
        response = describe(AutoScalingGroupNames=[self.name])
        return response.get("AutoScalingGroups", [])

    def exists(self):
        as_groups = self.get_auto_scaling_groups()
        for as_group in as_groups:
            if as_group['AutoScalingGroupName'] == self.name:
                return True
        return False

    def delete(self, wait=True):
        logger.log(f"Deleting AutoScaling '{self.name}'")
        delete = self.client.delete_auto_scaling_group
        response = delete(AutoScalingGroupName=self.name, ForceDelete=True)

        if wait:
            self.waiter.wait_until_terminated()

        logger.log(f"AutoScaling '{self.name}' deleted")
        return response

    def detach_target_groups(self, tg_name: str):
        detach = self.client.detach_load_balancer_target_groups
        as_name = self.name
        if self.exists():
            logger.log(f"Dettaching TargetGroups [{tg_name}]")
            detach(AutoScalingGroupName=as_name, TargetGroupARNs=[tg_name])
            logger.log(f"TargetGroups [{tg_name}] detached")

    def get_instances(self):
        describe = self.client.describe_auto_scaling_groups
        response = describe(AutoScalingGroupNames=[self.name])

        as_groups = response['AutoScalingGroups']
        if len(as_groups) > 0:
            instances = as_groups[0]['Instances']
            return instances
        return []

    def destroy_if_exists(self):
        if self.exists():
            self.delete()

    def wipe(self):
        self.destroy_if_exists()
