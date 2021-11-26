# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Union

from .logger import logger
from .utils import ensure_dir_exists

TMP_DIR: str = 'tmp'
TMP_PREFIX: str = f'./{TMP_DIR}/'
CWD_PREFIX: str = './'


class File():
    def __init__(self, name: str, is_json: bool, ephemeral: bool = True):
        self.name = name
        self.is_ephemeral = ephemeral
        self.is_json = is_json
        self.relative_path = TMP_PREFIX

    @property
    def path(self):
        return self.relative_path + self.name

    def write(self, content: Union[str, dict, list], mode: str = "w+"):
        ensure_dir_exists(self.relative_path)
        with open(self.path, mode=mode, encoding='utf-8') as file:
            if self.is_json:
                content = json.dumps(content, indent=2, default=str)
            file.write(content)

    def read(self) -> Union[str, dict, list]:
        with open(self.path, encoding='utf-8') as file:
            content = file.read()
            return json.loads(content) if self.is_json else content

    def exist(self) -> bool:
        return os.path.exists(self.path)

    def delete(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            logger.warn(f"File '{self.name}' not found. Probably deleted or moved.")


class FileSystem():
    created_files: Dict[str, File] = {}
    session_id: str = None

    def save_file(self, filename: str, content: Union[list, str, dict], mode: str = 'w+', tmp: bool = True):
        is_json = filename.endswith('.json')
        file = File(filename, ephemeral=tmp, is_json=is_json)
        file.write(content, mode)
        self.created_files[file.name] = file

    def load_config(self, relative_path: str):
        as_json = relative_path.endswith('.json')
        try:
            with open(relative_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return json.loads(content) if as_json else content
        except FileNotFoundError:
            logger.warn(f"File '{self.name}' not found. Probably deleted or moved.")

    def load_file(self, filename: str) -> str:
        file = self.created_files.get(filename)
        if not file:
            logger.error(f"File '{self.name}' not found. Probably deleted or moved.")
        return file.read()

    def read(self,filename:str) -> str:
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            logger.error(f"File '{filename}' not found.")
            raise


    def load_json(self, filename: str):
        content = self.load_file(filename)
        return json.loads(content)

    def file_exists(self, filename: str) -> bool:
        file = self.created_files.get(filename)
        if not file:
            return False
        return file.exist()

    def wipe_files(self):
        for file in self.created_files.values():
            if file.is_ephemeral:
                file.delete()


filesystem = FileSystem()
