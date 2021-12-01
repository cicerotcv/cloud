from time import sleep
from typing import List

from .environment import Secret
from .filesystem import filesystem as fs
from .logger import logger
from .region import Region
from .utils import all_terminated, print_public_ip, print_status

CONFIG_REGIONS_FILENAME = 'config.regions.json'


class Session():
    _secret: Secret = None
    regions: List[Region]

    def __init__(self) -> None:
        self._secret = Secret('.env')
        self.regions = []

    def load_region(self, region_name):
        """options: `n_virginia`, `oregon`, `n_california`, `ohio`"""
        regions: dict = fs.load_config(CONFIG_REGIONS_FILENAME)
        region_config = regions.get(region_name)

        if not region_config:
            return None
        region = Region(**region_config, secret=self._secret)
        logger.log(f"Loaded region '{region.region_name}'")
        self.regions.append(region)
        return region

    def wipe(self):
        for region in self.regions:
            region.wipe()
