import logging
from lightapi import LightApi
from dataclasses import dataclass
from typing import Optional

from lightapi.handlers import BaseModel


@dataclass
class PersonEndpoint(BaseModel):
    name: str
    age: int
    email: Optional[str] = None


@dataclass
class CompanyEndpoint(BaseModel):
    name: str
    address: str
    phone: str
    email: Optional[str] = None


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    app = LightApi()
    app.endpoint(PersonEndpoint)
    app.endpoint(CompanyEndpoint)
    app.run(host='0.0.0.0', port=8000)
