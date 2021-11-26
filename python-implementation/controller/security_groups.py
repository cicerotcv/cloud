import json

from .filesystem import filesystem as fs
from .logger import logger as console


def make_rule(port: int, CidrIp: str = "0.0.0.0/0"):
    return {
        'IpProtocol': 'tcp',
        'FromPort': port,
        'ToPort': port,
        'IpRanges': [{"CidrIp": CidrIp}]
    }


RULES = {
    'ssh': {
        'ingress': [make_rule(22)],
        'egress': []
    },
    'http': {
        'ingress': [make_rule(80), make_rule(8080)],
        'egress': []
    },
    'mongodb': {
        'ingress': [make_rule(27017)],
        'egress': []
    },
    'software_update': {
        'ingress': [],
        'egress': [make_rule(80), make_rule(8080), make_rule(443)]
    }
}


class SecurityGroup():
    GroupId: str = None
    GroupName: str = None

    def __init__(self, ec2_client, group_name: str, description: str):
        self.client = ec2_client
        self.GroupName = group_name
        self.Description = description
        self.ingress = []
        self.egress = []

    def enable_ingress(self, *rules: str):
        """options: `ssh`, `http`, `mongodb`, `software_update`"""
        for rule in rules:
            inbound_rules: list = RULES.get(rule)['ingress']
            self.ingress.extend(inbound_rules)

    def enable_egress(self, *rules: str):
        """options: `ssh`, `http`, `mongodb`, `software_update`"""
        for rule in rules:
            outbount_rules: list = RULES.get(rule)['egress']
            self.egress.extend(outbount_rules)

    def create(self):
        console.info(f"Creating Security Group '{self.GroupName}'")
        
        if self.exists():
            self.delete()


        client = self.client
        create = client.create_security_group
        authorize_ingress = client.authorize_security_group_ingress
        authorize_egress = client.authorize_security_group_egress

        response = create(GroupName=self.GroupName,
                          Description=self.Description)

        self.GroupId = response["GroupId"]
        console.success(f"SecurityGroup '{self.GroupName}' with GroupId='{self.GroupId}' created.")

        fs.save_file('sg-response.json', response, tmp=True)

        if len(self.ingress) > 0:
            authorize_ingress(GroupId=self.GroupId, IpPermissions=self.ingress)

        if len(self.egress) > 0:
            authorize_egress(GroupId=self.GroupId, IpPermissions=self.egress)

    def fetch(self):
        describe = self.client.describe_security_groups
        response = describe()
        groups = response["SecurityGroups"]

        for sg in groups:
            if sg["GroupName"] == self.GroupName:
                return sg

    def describe(self):
        description = self.fetch()

        if description:
            return console.info(json.dumps(description, indent=2))

        console.warn(f"Group '{self.GroupName}' doesn't exist.")

    def refresh(self):
        group = self.fetch()
        if group:
            self.GroupId = group["GroupId"]

    def delete(self):

        if not self.GroupId:
            self.refresh()

        if  not self.GroupId:
            return console.warn(f"Group '{self.GroupName}' doesn't exist.")

        console.info(f"Deleting Security Group '{self.GroupId}'")

        self.client.delete_security_group(GroupId=self.GroupId)
        console.success(f"SecurityGroup '{self.GroupId}' deleted.")
        self.GroupId = None

    def exists(self):
        self.refresh()
        group_exists = self.GroupId != None
        if group_exists:
            console.warn(f"Security Group with name '{self.GroupName}' already exists.")
        return group_exists


    def wipe(self):
        if self.GroupId:
            self.delete()
