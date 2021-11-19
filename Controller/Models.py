from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import UUID4


class ResponseMetadata(BaseModel):
    RequestId: UUID4
    HTTPStatusCode: int


class KeyPairSchema(BaseModel):
    KeyMaterial: str
    KeyName: str
    KeyFingerprint: str
    KeyPairId: str
    ResponseMetadata: ResponseMetadata
