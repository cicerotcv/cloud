
from .utils import make_rule

CONFIG_CLIENTS_FILENAME = 'config.clients.json'

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

DEFAULT_TAG = {
    "Key": "CreatedBy",
    "Value": "cicerotcv-boto3"
}

DEFAULT_TAG_FILTER = {
    'Name': f'tag:{DEFAULT_TAG["Key"]}',
    'Values': [DEFAULT_TAG["Value"]]
}
