"""HTTP response contract; all large address counts are decimal strings."""

from typing import Generic, Literal, TypeVar
from pydantic import BaseModel


class Origin(BaseModel):
    source_id: str
    source_run_id: str
    source_record_id: str
    observed_at: str
    ingested_at: str
    synthetic: Literal[True]


class Scope(BaseModel):
    id: str
    name: str
    namespace: str
    domain: str
    region: str
    managed_cidrs: list[str]
    synthetic: Literal[True]


class Prefix(BaseModel):
    id: str
    scope_id: str
    scope_name: str
    family: Literal[4, 6]
    cidr: str
    parent_id: str | None
    owner: str
    purpose: str
    tags: list[str]
    custom_fields: dict[str, str]
    version: int
    address_count: str
    origin: Origin


class AddressRange(BaseModel):
    start: str
    end: str


class Pool(BaseModel):
    id: str
    scope_id: str
    prefix_id: str
    family: Literal[4, 6]
    name: str
    management_mode: Literal["dhcp", "static"]
    allocation_authority: Literal["local", "external"]
    ranges: list[AddressRange]
    exclusions: list[AddressRange]
    pool_version: int
    capacity: str
    origin: Origin


class Allocation(BaseModel):
    id: str
    scope_id: str
    prefix_id: str
    pool_id: str | None
    family: Literal[4, 6]
    address: str
    owner: str
    purpose: str
    origin: Origin


class PrefixDetail(Prefix):
    pools: list[Pool]
    allocations: list[Allocation]


Item = TypeVar("Item")


class Page(BaseModel, Generic[Item]):
    items: list[Item]
    total: int
    limit: int
    offset: int
