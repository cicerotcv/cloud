from typing import List

import boto3
from botocore import exceptions

from .constants import DEFAULT_TAG
from .logger import logger
from .utils import make_availability_zones


class LoadBalancer():
    def __init__(self, region_name: str, credentials: dict) -> None:
        self.region_name = region_name
        self.name = 'lb-' + region_name
        self.client = self.init_client(region_name, credentials)

    def init_client(self, region_name: str, credentials: dict):
        return boto3.client('elb', region_name=region_name, **credentials)

    def create(self, groupIds: List[str], lb_port=80, i_port=8080):
        self.destroy_if_exists()
        logger.log(f"Creating LoadBalancer '{self.name}'")
        response = self.client.create_load_balancer(
            LoadBalancerName=self.name,
            Listeners=[{
                'Protocol': 'HTTP',
                'LoadBalancerPort': lb_port,
                'InstancePort': i_port
            }],
            AvailabilityZones=make_availability_zones(self.region_name),
            SecurityGroups=groupIds,
            Tags=[DEFAULT_TAG]
        )
        dns_name = response["DNSName"]
        logger.log(f"  LoadBalancer '{self.name}' created")
        logger.log(f"  LoadBalancer DNSName: {dns_name}")

    def get_load_balancers(self):
        try:
            describe = self.client.describe_load_balancers
            response = describe(LoadBalancerNames=[self.name])
            return response.get("LoadBalancerDescriptions", [])
        except exceptions.ClientError:
            return []

    def exists(self):
        return len(self.get_load_balancers()) > 0

    def delete(self):
        logger.log(f"Deleting LoadBalancer '{self.name}'")
        delete = self.client.delete_load_balancer
        delete(LoadBalancerName=self.name)
        logger.log(f"  LoadBalancer '{self.name}' deleted")

    def destroy_if_exists(self):
        if self.exists():
            logger.log(f"LoadBalancer '{self.name}' already exists")
            self.delete()

    def wipe(self):
        self.destroy_if_exists()
