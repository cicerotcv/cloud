
from .Logger import logger as console
from .utils import attr_guard, save_file, delete_file, save_file
import json


class KeyPair():
    KeyName: str = None
    ResponseMetadata: dict = None
    KeyFingerprint: str = None
    KeyPairId: str = None

    def __init__(self, client, debug=False) -> None:
        self._client = client
        self._debug = debug

    def create(self, KeyName: str):
        content = self._client.create_key_pair(
            KeyName=KeyName, DryRun=self._debug)

        self.KeyName = content['KeyName']
        self.ResponseMetadata = content['ResponseMetadata']
        self.KeyFingerprint = content['KeyFingerprint']
        self.KeyPairId = content['KeyPairId']

        console.info(
            f"KeyPair {self.KeyName} with id {self.KeyPairId} created")

        # local variable
        KeyMaterial = content["KeyMaterial"]

        del content['ResponseMetadata']
        del content["KeyMaterial"]

        save_file(f"{KeyName}.key", KeyMaterial)
        save_file(f"{KeyName}.key.json", content=json.dumps(content, indent=2))
        return content

    @attr_guard('KeyName')
    def delete(self):
        response = self._client.delete_key_pair(
            KeyName=self.KeyName, DryRun=self._debug)

        console.info(
            f"KeyPair {self.KeyName} with id {self.KeyPairId} deleted")

        delete_file(f"{self.KeyName}.key")
        delete_file(f"{self.KeyName}.key.json")

        return response

    @attr_guard('KeyName')
    def describe(self):
        response = self._client.describe_key_pairs(DryRun=self._debug)
        KeyPairs = response["KeyPairs"]

        this_key = [key_pair for key_pair in KeyPairs
                    if key_pair["KeyPairId"] == self.KeyPairId]
        dumped = json.dumps(this_key, indent=2)
        console.info(f'\n{dumped}\n')
        return this_key
