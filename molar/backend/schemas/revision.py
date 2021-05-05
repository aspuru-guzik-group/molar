from typing import List, Optional

from pydantic import BaseModel


class Revision(BaseModel):
    revision: str
    log_entry: str
    branch_labels: List[Optional[str]]
