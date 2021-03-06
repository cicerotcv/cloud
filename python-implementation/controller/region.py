
from typing import List
import boto3

from .auto_scaling import AutoScaling
from .client import InstanceManager
from .constants import CONFIG_CLIENTS_FILENAME,  DEFAULT_TAG_FILTER
from .environment import Secret
from .filesystem import filesystem as fs
from .key_pair import KeyPair
from .launch_configuration import LaunchConfiguration
from .load_balancer import LoadBalancer
from .logger import logger
from .machine_image import MachineImage
from .models import Config, RegionNameOptions
from .security_groups import SecurityGroup
from .utils import make_kp_name, make_sg_description, make_sg_name


class Region():
    region_name: str = None
    secret: Secret
    key_pair: KeyPair
    security_group: SecurityGroup
    client: InstanceManager
    boto3_client = None

    def __init__(self, region_name: RegionNameOptions, secret: Secret) -> None:
        self.secret = secret
        self.client: InstanceManager = None
        self.region_name = region_name

        self.boto3_client = self.__init_boto3()
        self.vpc_id: str = self.get_vpc_id()
        self.key_pair = self.__init_kp()
        self.security_group = self.__init_sg()
        self.launch_configuration = self.__init_lc()
        self.load_balancer = self.__init_lb()
        self.images = self.__init_ami()
        self.auto_scaling = self.__init_as()

    def __init_boto3(self) -> boto3.client:
        rn = self.region_name
        secret = self.secret.dict()
        return boto3.client('ec2', region_name=rn, **secret)

    def __init_kp(self) -> KeyPair:
        key_name = make_kp_name(self.region_name)
        return KeyPair(KeyName=key_name, client=self.boto3_client)

    def __init_sg(self) -> SecurityGroup:
        group_name = make_sg_name(self.region_name)
        description = make_sg_description(self.region_name)
        return SecurityGroup(self.boto3_client, group_name, description)

    def __init_lc(self) -> LaunchConfiguration:
        rn = self.region_name
        secret = self.secret.dict()
        return LaunchConfiguration(rn, secret)

    def __init_ami(self) -> MachineImage:
        client = self.boto3_client
        return MachineImage(client=client)

    def __init_lb(self) -> LoadBalancer:
        rn = self.region_name
        secret = self.secret.dict()
        return LoadBalancer(rn, self.vpc_id, secret)

    def __init_as(self) -> AutoScaling:
        rn = self.region_name
        secret = self.secret.dict()
        return AutoScaling(rn, secret)

    def get_vpc_id(self):
        response = self.boto3_client.describe_vpcs()
        vpc = response["Vpcs"][0]
        vpc_id = vpc["VpcId"]
        logger.log(f"VPC ID: {vpc_id}")
        return vpc_id

    def init_client(self, client_model):
        models: dict = fs.load_config(CONFIG_CLIENTS_FILENAME)
        params = models.get(client_model)
        config = Config(**params, region_name=self.region_name)
        self.client = InstanceManager(self.boto3_client, config)
        return self.client

    def create_instance(self, UserData: str = '', wait: bool = False):
        client = self.client
        group = self.security_group

        if not client or not group:
            return logger.error('You must first create a security group and load a client model')

        instance = client.create_instance(
            group.GroupId,
            self.key_pair.KeyName,
            UserData=UserData,
            wait=wait)

        return instance

    def get_instances(self):
        client = self.client
        my_instances = client.describe_instances()

        return my_instances

    def __wait_until_terminated(self, InstanceIds: List[str]):
        logger.log(f'Waiting for instance(s) to terminate: {InstanceIds}')
        client = self.boto3_client
        waiter = client.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=InstanceIds)
        logger.log(f'Instance(s) terminated: {InstanceIds}')

    def __terminate_instances(self):
        filters = [DEFAULT_TAG_FILTER, {
            'Name': 'instance-state-name',
            'Values': ['pending', 'running', 'terminating', 'stopping', 'stopped']
        }]
        response = self.boto3_client.describe_instances(Filters=filters)
        allocated_reservations = [reservation
                                  for reservation in response['Reservations']]
        instanceIds: List[str] = []
        for reservation in allocated_reservations:
            instanceIds += [instance["InstanceId"]
                            for instance in reservation["Instances"]]
        if len(instanceIds) > 0:
            terminate = self.boto3_client.terminate_instances
            response = terminate(InstanceIds=instanceIds)
            self.__wait_until_terminated(instanceIds)

    def create_image(self, InstanceId: str, ImageName: str) -> str:
        self.wait_until_running(InstanceIds=[InstanceId])
        logger.log(f"Creating image '{ImageName}' from '{InstanceId}'")
        return self.images.create(InstanceId, ImageName)

    def delete_image(self, ImageId: str):
        logger.log(f"Deregistering image '{ImageId}'")
        self.images.deregister(ImageId)

    def get_subnets(self):
        response = self.boto3_client.describe_subnets()
        subnets = response["Subnets"]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]
        return subnet_ids

    def wipe(self):
        logger.info("Wiping AutoScaling")
        instances = self.auto_scaling.get_instances()
        self.auto_scaling.wipe()

        logger.info("Wiping LaunchConfigurations")
        self.launch_configuration.wipe()

        logger.info("Wiping LoadBalancers")
        instanceIds = [instance['InstanceId'] for instance in instances]
        self.load_balancer.target_group.deregister(instanceIds)
        self.load_balancer.wipe()

        logger.info("Wiping AMIs")
        self.images.wipe()

        logger.info("Wiping Instances")
        if self.client:
            self.client.wipe()
        else:
            self.__terminate_instances()

        logger.info("Wiping SecurityGroups")
        self.security_group.delete()
        logger.info("Wiping KeyPairs")
        self.key_pair.delete()
