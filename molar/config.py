# std
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(params: Dict[str, Any]) -> "ClientConfig":
        return ClientConfig(**params)
