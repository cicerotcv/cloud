import json
import os
from typing import Any
from .logger import Logger
from .utils import attr_guard, client_guard, file_exists, save_file

console = Logger()


class KeyPair():
    KeyName: str = None
    ResponseMetadata: dict = None
    KeyFingerprint: str = None
    KeyPairId: str = None

    def __init__(self, KeyName: str, client: Any, debug: bool = False) -> None:
        self._client = client
        self._debug = debug
        self.KeyName = KeyName

    def __repr__(self) -> str:
        return str(json.dumps({key: value for key, value in self.__dict__.items() if not key.startswith('_')}))

    @client_guard
    @attr_guard('KeyName')
    def create(self):
        content = self._client.create_key_pair(KeyName=self.KeyName, DryRun=self._debug)

        self.KeyName = content['KeyName']
        self.ResponseMetadata = content['ResponseMetadata']
        self.KeyFingerprint = content['KeyFingerprint']
        self.KeyPairId = content['KeyPairId']

        console.success(f"KeyPair '{self.KeyName}' with KeyPairId='{self.KeyPairId}' created.")

        # local variable
        KeyMaterial = content["KeyMaterial"]

        del content['ResponseMetadata']
        del content["KeyMaterial"]

        save_file(f"{self.KeyName}.key", KeyMaterial, ephemeral=True)
        save_file(f"{self.KeyName}.key.json", content=json.dumps(content, indent=2), ephemeral=True)

        return content

    @client_guard
    def exists(self):
        response = self._client.describe_key_pairs(DryRun=self._debug)

        KeyPairs = response["KeyPairs"]
        for key in KeyPairs:
            if key["KeyName"] == self.KeyName:
                if not file_exists(f'{self.KeyName}.key'):
                    # key exists and you don't have the secret
                    console.error(f"KeyPair with name {self.KeyName} already exists and you don't have the private piece.")
                    return True
                # key exist and you have the secret.
                console.warn(f"KeyPair with name {self.KeyName} already exists and you have the private piece.")
                return True
        return False

    @client_guard
    @attr_guard('KeyName')
    def delete(self):
        response = self._client.delete_key_pair(KeyName=self.KeyName, DryRun=self._debug)

        # delete_file(f"{self.KeyName}.key")
        # delete_file(f"{self.KeyName}.key.json")

        console.success(
            f"KeyPair '{self.KeyName}' deleted.")

        # self.__dict__ = {}

        return response

    @client_guard
    @attr_guard('KeyName', 'KeyPairId')
    def describe(self):
        response = self._client.describe_key_pairs(DryRun=self._debug)
        KeyPairs = response["KeyPairs"]

        this_key = [key_pair for key_pair in KeyPairs if key_pair["KeyPairId"] == self.KeyPairId]

        dumped = json.dumps(this_key, indent=2)
        console.info(f'\n{dumped}\n')

        return this_key
