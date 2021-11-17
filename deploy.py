# -*- encoding utf-8 -*-

from dotenv import dotenv_values, main
import boto3
import json

config = dotenv_values()
try:
    AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
    AWS_REGION = config["AWS_REGION"]
    AWS_KEY_NAME = config["AWS_KEY_NAME"]
except:
    raise Exception("Error loading credentials")


def create_ec2_instance(instance_config: dict = {}, UserData: str = None):
    try:
        print("Configuring EC2 Credentials")
        client = boto3.client('ec2',
                              region_name=AWS_REGION,
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        print("Launching Instance")
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type, (64-bit Arm)
        client.run_instances(
            **instance_config,
            KeyName=AWS_KEY_NAME,
            # security group
            UserData=UserData
        )
        print(client.__dict__)
    except Exception as e:
        print(e)


def load_file(filename: str) -> str:
    file = open(filename, mode='r', encoding='utf-8')
    content = file.read()
    file.close()
    return content


def load_instance_settings(config_file: str = "config.json") -> str:
    config = load_file(config_file)
    instance_settings = json.loads(config)
    return instance_settings


def main():
    settings = load_instance_settings()
    user_data = load_file("setup_server.sh")
    print(f"config: {settings}")
    # create_ec2_instance(instance_config=settings, UserData=user_data)


if __name__ == "__main__":
    main()
