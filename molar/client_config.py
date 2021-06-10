# std
import configparser
from dataclasses import asdict, dataclass
import os
from typing import Any, Dict, Optional


@dataclass
class ClientConfig:
    email: str
    password: str
    database_name: str
    log_level: str = "INFO"
    server_url: str = "http://localhost:8000"
    api_prefix: str = "/api/v1"

    @property
    def base_url(self):
        return self.server_url + self.api_prefix

    @staticmethod
    def from_config_file(config_file: str, section_name: str = None):
        parser = configparser.ConfigParser()
        parser.read(config_file)
        if not section_name:
            section_name = parser.sections()[0]

        if not (section_name in parser):
            raise ValueError(
                f"Section {section_name} could not be found in the config file."
            )

        return ClientConfig(**parser[section_name], database_name=section_name)

    def to_config_file(self, config_file: str):
        parser = configparser.ConfigParser()
        parser.read(config_file)
        parser.add_section(self.database_name)

        for key, value in asdict(self):
            parser.set(self.database_name, key, value)
        with open(config_file) as f:
            parser.write(f)
