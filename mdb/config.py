from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ClientConfig:
    hostname: str
    database: str
    username: str
    password: str
    port: int = 5432

    return_pandas_dataframe: bool = True
    log_level: str = "INFO"
    user_dir: Optional[Path] = None

    @property
    def sql_url(self):
        return "postgresql://%s:%s@%s:%s/%s" % (
            self.username,
            self.password,
            self.hostname,
            self.port,
            self.database,
        )
