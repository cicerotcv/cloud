from enum import Enum

from pydantic import BaseModel


class InstanceTypeOptions(str, Enum):
    T2_MICRO = "t2.micro"
    # add more options here


class RegionNameOptions(str, Enum):
    N_VIRGINIA = "us-east-1"  # US East (N. Virginia)
    OHIO = "us-east-2"  # US East (Ohio)
    N_CALIFORNIA = "us-west-1"  # US West (N. California)
    OREGON = "us-west-2"  # US West (Oregon)
    # add more options here


class InstanceConfig(BaseModel):
    ImageId: str
    MinCount: int
    MaxCount: int
    InstanceType: str

    class Config:
        use_enum_values = True


class Config(BaseModel):
    client_type: str
    region_name: RegionNameOptions
    instance_config: InstanceConfig = None


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


class TagSchema(BaseModel):
    Key: str
    Value: str
