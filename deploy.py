# -*- encoding utf-8 -*-
from time import sleep
from typing import Any

import boto3

from controller import Environment, KeyPair
from controller.utils import attr_guard, random_str, slugify

# def signal_handler(sig, frame):
#     print(strsignal(sig))
#     exit(0)
# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)


def create_ec2_instance(instance_config: dict = {}, UserData: str = None):
    try:
        print("Configuring EC2 Credentials")
        client = boto3.client('ec2',
                              region_name=env.config.region_name,
                              aws_access_key_id=env.secret.aws_access_key_id,
                              aws_secret_access_key=env.secret.aws_secret_access_key)
        print("Launching Instance")
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type, (64-bit Arm)
        client.run_instances(
            **instance_config,
            KeyName=env.config.region_name,
            # security group
            UserData=UserData
        )
        print(client.__dict__)
    except Exception as e:
        print(e)


class Client():
    keyPair: KeyPair = None
    client: Any = None

    def __init__(self, instance_name=str):
        self.name: str = instance_name
        self.env: Environment = Environment()

    def init(self):
        self.client = boto3.client(
            'ec2',
            region_name=self.env.settings.region_name,
            aws_access_key_id=self.env.secret.aws_access_key_id,
            aws_secret_access_key=self.env.secret.aws_secret_access_key
        )

    @attr_guard('client')
    def generate_keypair(self, KeyName=None):
        if KeyName is None:
            KeyName = slugify(self.name) + "_" + random_str()

        key_pair = KeyPair(self.client)
        return KeyName, key_pair

# def create_security_group():
#     securitygroup = client.create_security_group(
#         GroupName='SSH-ONLY', Description='only allow SSH traffic')
#     securitygroup.authorize_ingress(
#         CidrIp='0.0.0.0/0', IpProtocol='tcp', FromPort=22, ToPort=22)


# def load_instance_settings(config_file: str = "config.json") -> str:
#     config = load_file(config_file)
#     instance_settings = json.loads(config)
#     return instance_settings


# def main():
#     settings = load_instance_settings()
#     user_data = load_file("setup_server.sh")
#     print(f"config: {settings}")
#     # create_ec2_instance(instance_config=settings, UserData=user_data)


if __name__ == "__main__":
    client = Client('webserver')
    client.init()
    kn, kp = client.generate_keypair()  # redundante
    kp.create(kn)
    sleep(10)
    kp.describe()
    sleep(10)
    kp.delete()
