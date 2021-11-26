from dotenv import dotenv_values
from pydantic import BaseModel, Field, error_wrappers

from .logger import logger
from .utils import hide


class CustomBaseModel(BaseModel):
    def __init__(self, **data):
        super().__init__(**{key.lower(): value
                            for key, value in data.items()})


class Settings(CustomBaseModel):
    region_name: str


class Secret(CustomBaseModel):
    aws_access_key_id: str = Field(..., min_length=10)
    aws_secret_access_key: str = Field(..., min_length=10)

    def __init__(self, environment_path: str = '.env'):
        data = dict(dotenv_values(environment_path))
        try:
            super().__init__(**data)
        except error_wrappers.ValidationError as e:
            for error in e.errors():
                reason = error['loc'][0]
                message = error['msg']
                logger.error(f'{reason}: {message}')

            exit(1)

    def __str__(self):
        # prevent keys from being printed
        return ' '.join([f'{key}={hide(value, digits=20)}' for key, value in self.dict().items()])

    def __repr__(self) -> str:
        return f"Secret({self.__str__()})"
