import json
from typing import Any

from .filesystem import filesystem as fs
from .logger import logger
from .utils import attr_guard, client_guard, random_str
from .constants import DEFAULT_TAG, DEFAULT_TAG_FILTER


class KeyPair():
    KeyName: str = None
    ResponseMetadata: dict = None
    KeyFingerprint: str = None
    KeyPairId: str = None

    def __init__(self, KeyName: str, client: Any, debug: bool = False) -> None:
        self.client = client
        self.KeyName = KeyName

    def __repr__(self) -> str:
        return str(json.dumps({key: value for key, value in self.__dict__.items()
                               if not key.startswith('_')}))

    def create(self):
        self.delete_duplicate()

        logger.log(f"Creating KeyPair '{self.KeyName}'")
        create_kp = self.client.create_key_pair
        content = create_kp(KeyName=self.KeyName,
                            TagSpecifications=[{
                                "ResourceType": "key-pair",
                                "Tags": [DEFAULT_TAG]
                            }])

        self.ResponseMetadata = content['ResponseMetadata']
        self.KeyFingerprint = content['KeyFingerprint']
        self.KeyPairId = content['KeyPairId']

        logger.log(f"  KeyPair '{self.KeyName}::{self.KeyPairId}' created")

        KeyMaterial: str = content["KeyMaterial"]

        del content['ResponseMetadata']
        del content["KeyMaterial"]

        fs.save_file(f'{self.KeyName}.key', KeyMaterial, tmp=True)
        fs.save_file(f'{self.KeyName}.key.json', KeyMaterial, tmp=True)

        return content

    def get_keypairs(self):
        response = self.client.describe_key_pairs(Filters=[DEFAULT_TAG_FILTER])
        return response.get("KeyPairs", [])

    def delete_duplicate(self):
        if self.exists():
            logger.log(f"KeyPair '{self.KeyName}' already exists")
            self.delete()

    def exists(self):
        key_pairs = self.get_keypairs()
        for key in key_pairs:
            if key["KeyName"] == self.KeyName:
                self.KeyPairId = key["KeyPairId"]
                return True
        return False

    def delete(self, key_pair_id: str = None):
        if not key_pair_id:
            key_pair_id = self.KeyPairId
        if key_pair_id:
            delete_kp = self.client.delete_key_pair
            kn = self.KeyName
            logger.log(f"Deleting KeyPair '{key_pair_id}'.")
            response = delete_kp(KeyName=kn)
            logger.log(f"  KeyPair '{key_pair_id}' deleted.")
            return response
