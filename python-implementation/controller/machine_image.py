from typing import List

from .constants import DEFAULT_TAG, DEFAULT_TAG_FILTER
from .logger import logger


class MachineImage():
    def __init__(self, client) -> None:
        self.client = client
        self.created_images: List[str] = []

    def create(self, instance_id: str, image_name: str) -> str:
        """Returns `ImageId`"""
        self.destroy_duplicate(image_name)

        create_image = self.client.create_image
        logger.log(f"Creating AMI '{image_name}'")
        response = create_image(InstanceId=instance_id,
                                NoReboot=True,
                                Name=image_name,
                                TagSpecifications=[{
                                    "ResourceType": "image",
                                    "Tags": [DEFAULT_TAG]
                                }])
        image_id = response["ImageId"]
        logger.log(f"  AMI '{image_name}' with id '{image_id}' created")
        self.created_images.append(image_id)

        logger.log(f"Waiting for AMI '{image_name}' to be available")
        waiter = self.client.get_waiter('image_available')
        waiter.wait(ImageIds=self.created_images)
        logger.log(f"  AMI '{image_name}' is available")

        return image_id

    def deregister(self, image_id: str):
        logger.log(f"Deregistering AMI '{image_id}'")
        self.client.deregister_image(ImageId=image_id)
        logger.log(f"  AMI '{image_id}' deregistered")

    def get_images(self):
        response = self.client.describe_images(Filters=[DEFAULT_TAG_FILTER])
        return response.get("Images", [])

    def destroy_duplicate(self, image_name: str):
        images = self.get_images()
        for image in images:
            if image["Name"] == image_name:
                image_id = image["ImageId"]
                return self.deregister(image_id)

    def wipe(self):
        images = self.get_images()
        for image in images:
            image_id = image["ImageId"]
            self.deregister(image_id)
