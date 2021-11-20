from typing import List
from pydantic import BaseModel
from enum import Enum


class InstanceTypeOptions(Enum):
    T2_MICRO = "t2.micro"


class RegionNameOptions(Enum):
    US_EAST_1 = "us-east-1"  # US East (Ohio)
    US_EAST_2 = "us-east-2"  # US East (N. Virginia)
    US_WEST_1 = "us-west-1"  # US West (N. California)
    US_WEST_2 = "us-west-2"  # US West (Oregon)


class ImageIdOptions(Enum):
    UBUNTU_1804 = "ami-0279c3b3186e54acd"  # (64-bit x86)


class InstanceConfig(BaseModel):
    ImageId: str
    MinCount: int
    MaxCount: int
    InstanceType: str


class Config(BaseModel):
    client_type: str
    region_name: str
    instance_config: InstanceConfig


class InstanceSchema(BaseModel):
    InstanceId: str
    InstanceType: str
    KeyName: str
