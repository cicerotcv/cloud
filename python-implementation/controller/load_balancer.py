from time import sleep
from typing import List
import boto3
from botocore import exceptions

from .constants import DEFAULT_TAG
from .listener import Listener
from .logger import logger
from .target_group import TargetGroup


class LoadBalancerWaiter():
    def __init__(self, load_balancer) -> None:
        self.load_balancer = load_balancer

    def wait_until_available(self):
        client = self.load_balancer.client
        Name = self.load_balancer.name

        logger.log(f"Waiting for LoadBalancer '{Name}' to be available")
        waiter = client.get_waiter('load_balancer_available')
        waiter.wait(Names=[Name])
        logger.log(f"LoadBalancer '{Name}' is available")

    def wait_until_deleted(self):
        client = self.load_balancer.client
        Name = self.load_balancer.name

        logger.log(f"Waiting for LoadBalancer '{Name}' to be deleted")
        waiter = client.get_waiter('load_balancers_deleted')
        waiter.wait(Names=[Name])
        logger.log(f"LoadBalancer '{Name}' is deleted")


class LoadBalancer():
    def __init__(self, region_name: str, vpc_id: str, credentials: dict) -> None:
        self.region_name = region_name
        self.name = 'lb-' + region_name
        self.vpc_id = vpc_id
        self.client = self.init_client(region_name, credentials)
        self.waiter = LoadBalancerWaiter(self)
        self.target_group = TargetGroup(self.client, 'tg-' + self.region_name)
        self.listener = Listener(self)
        self.ARN = None
        self.DNSName = None

    def init_client(self, region_name: str, credentials: dict):
        return boto3.client('elbv2', region_name=region_name, **credentials)

    def create(self, groupIds: List[str], subnet_ids: List['str'], wait=True):
        self.destroy_if_exists()

        logger.log(f"Creating LoadBalancer '{self.name}'")
        response = self.client.create_load_balancer(
            Name=self.name,
            Subnets=subnet_ids,
            SecurityGroups=groupIds,
            Scheme="internet-facing",
            IpAddressType="ipv4",
            Type="application",
            Tags=[DEFAULT_TAG])
        lb = response['LoadBalancers'][0]
        self.ARN = lb['LoadBalancerArn']
        self.DNSName = lb['DNSName']

        self.target_group.create(self.vpc_id)
        self.listener.create()

        if wait:
            self.waiter.wait_until_available()

        logger.log(f"  LoadBalancer '{self.name}' created")
        logger.log(f"  LoadBalancer ARN '{self.ARN}' created")
        logger.log(f"  LoadBalancer DNSName '{self.DNSName}' created")

    def get_load_balancers(self):
        try:
            describe = self.client.describe_load_balancers
            response = describe(Names=[self.name])
            return response.get("LoadBalancers", [])
        except exceptions.ClientError:
            return []

    def exists(self):
        lbs = self.get_load_balancers()
        for lb in lbs:
            if lb['LoadBalancerName'] == self.name:
                self.ARN = lb['LoadBalancerArn']
                self.DNSName = lb['DNSName']
                return True
        return False

    def delete(self, wait=True):
        logger.log(f"Deleting LoadBalancer '{self.name}'")
        delete = self.client.delete_load_balancer
        delete(LoadBalancerArn=self.ARN)
        if wait:
            self.waiter.wait_until_deleted()
        logger.log(f"  LoadBalancer '{self.name}' deleted")

    def destroy_if_exists(self):
        if self.exists():
            logger.log(f"LoadBalancer '{self.name}' already exists")
            self.delete()
            sleep(30)
            self.target_group.destroy_if_exists()

    def wipe(self):
        self.destroy_if_exists()
