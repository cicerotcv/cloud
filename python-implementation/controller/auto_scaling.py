from typing import List

import boto3

from controller.utils import make_availability_zones

from .logger import logger
from .models import InstanceSchema

from .constants import DEFAULT_TAG


class AutoScaling():
    def __init__(self, region_name: str, secret: dict) -> None:
        self.secret = secret
        self.region_name = region_name
        self.name = 'as_' + region_name
        self.client = self.__boto3()
        self.attached_lb = None

    def __boto3(self):
        rn = self.region_name
        secret = self.secret
        return boto3.client('autoscaling', region_name=rn, **secret)

    def create_auto_scalling(self, lc_name: str, lb_name: str, min_size=1, max_size=3):
        self.attached_lb = lb_name
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
            LoadBalancerNames=[lb_name],
            CapacityRebalance=True,
            Tags=[{
                'ResourceType': 'auto-scaling-group',
                'Key': DEFAULT_TAG['Key'],
                'Value': DEFAULT_TAG['Value'],
                'PropagateAtLaunch': True
            }]
        )
        logger.log(f"AutoScaling '{self.name}' created")

        self.attach_load_balancer(lb_name)

    def attach_load_balancer(self, lb_name: str):
        attach = self.client.attach_load_balancers
        response = attach(AutoScalingGroupName=self.name,
                          LoadBalancerNames=[lb_name])
        return response

    def dettach_load_balancer(self, lb_name: str):
        detach = self.client.detach_load_balancers
        response = detach(AutoScalingGroupName=self.name,
                          LoadBalancerNames=[lb_name])
        return response

    def get_auto_scaling_groups(self):
        describe = self.client.describe_auto_scaling_groups
        response = describe(AutoScalingGroupNames=[self.name])
        return response.get("AutoScalingGroups", [])

    def exists(self):
        as_groups = self.get_auto_scaling_groups()
        return len(as_groups) > 0

    def delete(self):
        logger.log(f"Deleting AutoScaling '{self.name}'")
        delete = self.client.delete_auto_scaling_group
        response = delete(AutoScalingGroupName=self.name, ForceDelete=True)
        logger.log(f"AutoScaling '{self.name}' deleted")
        return response

    def destroy_if_exists(self):
        if self.exists():
            if self.attached_lb:
                self.dettach_load_balancer(self.attached_lb)
            self.delete()

    def wipe(self):
        self.destroy_if_exists()
