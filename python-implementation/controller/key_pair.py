import json
from typing import Any

from .filesystem import filesystem as fs
from .logger import Logger
from .utils import attr_guard, client_guard, random_str

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
    def create(self):
        if self.exists():
            self.delete()

        content = self._client.create_key_pair(KeyName=self.KeyName, DryRun=self._debug)

        self.KeyName = content['KeyName']
        self.ResponseMetadata = content['ResponseMetadata']
        self.KeyFingerprint = content['KeyFingerprint']
        self.KeyPairId = content['KeyPairId']

        console.success(f"KeyPair '{self.KeyName}' with KeyPairId='{self.KeyPairId}' created.")

        # local variable
        KeyMaterial: str = content["KeyMaterial"]

        del content['ResponseMetadata']
        del content["KeyMaterial"]

        fs.save_file(f'{self.KeyName}.key', KeyMaterial, tmp=True)
        fs.save_file(f'{self.KeyName}.key.json', KeyMaterial, tmp=True)

        return content

    @client_guard
    def exists(self):
        response = self._client.describe_key_pairs(DryRun=self._debug)

        KeyPairs = response["KeyPairs"]
        for key in KeyPairs:
            if key["KeyName"] == self.KeyName:
                console.warn(f"KeyPair with name '{self.KeyName}' already exists.")
                return True
        return False

    @client_guard
    @attr_guard('KeyName')
    def delete(self):
        response = self._client.delete_key_pair(KeyName=self.KeyName, DryRun=self._debug)
        console.success(f"KeyPair '{self.KeyName}' deleted.")
        return response

    @client_guard
    @attr_guard('KeyName', 'KeyPairId')
    def describe(self):
        response = self._client.describe_key_pairs(DryRun=self._debug)
        KeyPairs = response["KeyPairs"]

        this_key = [
            key_pair for key_pair in KeyPairs if key_pair["KeyPairId"] == self.KeyPairId]

        dumped = json.dumps(this_key, indent=2)
        console.info(f'\n{dumped}\n')

        return this_key
