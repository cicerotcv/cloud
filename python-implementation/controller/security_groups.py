
from .constants import DEFAULT_TAG, DEFAULT_TAG_FILTER, RULES
from .filesystem import filesystem as fs
from .logger import logger


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
        self.delete_duplicate()

        logger.log(f"Creating Security Group '{self.GroupName}'")

        client = self.client
        create = client.create_security_group

        response = create(GroupName=self.GroupName,
                          Description=self.Description,
                          TagSpecifications=[{
                              "ResourceType": "security-group",
                              "Tags": [DEFAULT_TAG]
                          }])

        self.GroupId = response["GroupId"]
        logger.log(
            f"  SecurityGroup '{self.GroupName}::{self.GroupId}' created")

        fs.save_file('sg-response.json', response, tmp=True)

        self.authorize_ingress()
        self.authorize_egress()

    def authorize_ingress(self):
        if len(self.ingress) > 0:
            authorize_ingress = self.client.authorize_security_group_ingress
            authorize_ingress(GroupId=self.GroupId, IpPermissions=self.ingress)

    def authorize_egress(self):
        if len(self.egress) > 0:
            authorize_egress = self.client.authorize_security_group_egress
            authorize_egress(GroupId=self.GroupId, IpPermissions=self.egress)

    def get_security_groups(self):
        describe = self.client.describe_security_groups
        response = describe(Filters=[DEFAULT_TAG_FILTER])
        return response.get("SecurityGroups", [])

    def delete(self, group_id=None):
        if not group_id:
            group_id = self.GroupId
        if group_id:
            logger.log(f"Deleting SecurityGroup '{group_id}'")
            self.client.delete_security_group(GroupId=group_id)
            logger.log(f"  SecurityGroup '{group_id}' deleted.")

    def delete_duplicate(self):
        if self.exists():
            logger.log(f"SecurityGroup '{self.GroupName}' already exists")
            self.delete()

    def exists(self):
        security_groups = self.get_security_groups()
        for group in security_groups:
            if group["GroupName"] == self.GroupName:
                self.GroupId = group["GroupId"]
                return True
        return False

    def wipe(self):
        if self.GroupId:
            self.delete()
