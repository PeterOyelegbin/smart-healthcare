from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    organisation: Optional[str]
    # cac_document: Required[str]
    email: Optional[str]
    password: Optional[str]
