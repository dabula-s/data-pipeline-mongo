from datetime import datetime
from typing import Any, Annotated

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator


class OpenPort(BaseModel):
    service_name: str | None = None
    port: int
    protocol: str

    def __hash__(self):
        return hash((self.service_name, self.port, self.protocol))


class Software(BaseModel):
    name: str
    version: str | None = None


# https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/
PyObjectId = Annotated[str, BeforeValidator(str)]


# TODO: create DTOs models separately from entities
class HostNormalizedData(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    hostname: str
    local_ip: str
    external_ip: str | None = None
    mac_address: str | None = None
    provider: str | None = None
    os_version: str | None = None
    platform: str | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    open_ports_count: int | None = None
    open_ports: list[OpenPort] | None = Field(default_factory=list)
    software: list[Software] | None = Field(default_factory=list)
    vuln_count: int | None = None
    sources: list[str] | None = Field(default_factory=list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class HostRawData(BaseModel):
    source: str
    data: dict


class HostUnmergedDataGroup(BaseModel):
    group_id: dict[str, Any]
    group_docs: list[HostNormalizedData]
