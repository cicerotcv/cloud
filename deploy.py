# -*- encoding utf-8 -*-
from time import sleep

import boto3

from Controller import Environment, KeyPairSchema
from Controller.KeyPair import KeyPair
import Controller.Logger

# def signal_handler(sig, frame):
#     print(strsignal(sig))
#     exit(0)


# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)

# credentials = Credential()
env = Environment()

ec2_params = {**env.config.dict(), **env.secret.dict()}

client = boto3.client('ec2', **ec2_params)


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
    Controller.Logger.enable_colors = False

    keypair = KeyPair(client, debug=False)

    # keypair.create('TestBoto3')
    # sleep(3)

    # keypair.describe()
    # sleep(3)
    keypair.delete()
    # sleep(3)
