from dotenv import dotenv_values
from pydantic import BaseModel

from .utils import hide


class CustomBaseModel(BaseModel):
    def __init__(self, **data):
        super().__init__(**{key.lower(): value
                            for key, value in data.items()})


class Config(CustomBaseModel):
    region_name: str


class Secret(CustomBaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str

    def __str__(self):
        # prevent keys from being printed
        return ' '.join([f'{key}={hide(value)}' for key, value in self.dict().items()])

    def __repr__(self) -> str:
        return f"Secret({self.__str__()}"


class Environment(CustomBaseModel):
    secret: Secret
    config: Config

    def __init__(self):
        data = dict(dotenv_values())
        config = Config(**data)
        secret = Secret(**data)
        super().__init__(secret=secret, config=config)


# if __name__ == "__main__":
#     env = Environment()
#     print(env.dict())
#     print(env.secret)
#     print(env.secret.aws_access_key_id)
#     print(env.config)
