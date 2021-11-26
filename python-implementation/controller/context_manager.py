from .filesystem import filesystem as fs
from .logger import logger
from .session import Session


class ContextManager():
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self.session

    def __exit__(self, type, value, traceback):
        logger.success("Successfully exiting context manager")
        self.session.wipe()
        fs.wipe_files()
        return type is KeyboardInterrupt
