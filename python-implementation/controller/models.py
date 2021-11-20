from typing import List
from pydantic import BaseModel
from enum import Enum


class InstanceTypeOptions(str, Enum):
    T2_MICRO = "t2.micro"
    # add more options here


class RegionNameOptions(str, Enum):
    US_EAST_1 = "us-east-1"  # US East (Ohio)
    US_EAST_2 = "us-east-2"  # US East (N. Virginia)
    US_WEST_1 = "us-west-1"  # US West (N. California)
    US_WEST_2 = "us-west-2"  # US West (Oregon)
    # add more options here


class ImageIdOptions(str, Enum):
    UBUNTU_1804 = "ami-0279c3b3186e54acd"  # (64-bit x86)
    # add more options here


class InstanceConfig(BaseModel):
    ImageId: ImageIdOptions
    MinCount: int
    MaxCount: int
    InstanceType: str

    class Config:
        use_enum_values = True


class Config(BaseModel):
    client_type: str
    region_name: RegionNameOptions
    instance_config: InstanceConfig


class StateSchema(BaseModel):
    Code: int
    Name: str 


class InstanceSchema(BaseModel):
    InstanceId: str
    ReservationId: str = None
    PublicIpAddress: str = None
    InstanceType: InstanceTypeOptions
    KeyName: str
    State: StateSchema = None
