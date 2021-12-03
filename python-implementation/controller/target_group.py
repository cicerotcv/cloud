
import json
from .constants import DEFAULT_TAG
from .logger import logger
from botocore import exceptions


class TargetGroup():
    def __init__(self, client, name) -> None:
        self.name = name
        self.client = client
        self.ARN = None

    def create(self, vpc_id: str):
        self.destroy_if_exists()
        create = self.client.create_target_group
        logger.log(f"Creating TargetGroup '{self.name}'")
        response = create(Name=self.name,
                          Protocol='HTTP',
                          Port=8080,
                          HealthCheckEnabled=True,
                          HealthCheckProtocol='HTTP',
                          HealthCheckPort='8080',
                          HealthCheckPath='/',
                          TargetType='instance',
                          Tags=[DEFAULT_TAG],
                          VpcId=vpc_id)
        tg = response['TargetGroups'][0]
        self.ARN = tg['TargetGroupArn']
        logger.log(f"TargetGroup '{self.name}' created")

    def get_target_groups(self):
        try:
            describe = self.client.describe_target_groups
            response = describe(Names=[self.name])
            return response['TargetGroups']
        except exceptions.ClientError:
            return []

    def exists(self):
        tgs = self.get_target_groups()
        for tg in tgs:
            if tg['TargetGroupName'] == self.name:
                print(json.dumps(tg, indent=2, default=str))
                self.ARN = tg['TargetGroupArn']
                return True
        return False

    def deregister(self, InstanceIds):
        if self.exists() and len(InstanceIds):
            print(f"deregistering {InstanceIds}")
            self.client.deregister_targets(
                TargetGroupArn=self.ARN,
                Targets=[{"Id": instanceId for instanceId in InstanceIds}])

    def delete(self, ARN: str):
        logger.log(f"Deleting TargetGroup '{self.name}'")
        delete = self.client.delete_target_group
        delete(TargetGroupArn=ARN)
        logger.log(f"TargetGroup '{self.name}' deleted")

    def destroy_if_exists(self):
        if self.exists():
            self.delete(self.ARN)

    def wipe(self):
        self.destroy_if_exists()
