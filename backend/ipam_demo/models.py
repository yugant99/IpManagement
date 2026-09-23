"""HTTP response contract; all large address counts are decimal strings."""

from typing import Any, Generic, Literal, TypeVar
from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt


AccessRole = Literal["viewer", "requester", "operator", "approver", "platform_admin"]


class AccessContext(BaseModel):
    """Trusted identity context with C-A Viewer inheritance and no credential material."""

    principal_id: str
    roles: list[AccessRole]
    domains: list[str]
    selected_domain: str | None
    configuration_revision: int
    configuration_digest: str
    policy_revision: str
    is_evidence_coordinator: bool


class ReadinessStatus(BaseModel):
    process_ready: bool
    schema_ready: bool
    data_ready: bool
    static_ready: bool
    configuration_ready: bool
    domain_state_compatible: bool
    reasons: list[str]


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


class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class StrictResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class MigrationAssessmentCreateRequest(StrictRequest):
    source_batch_id: str
    expected_baseline_version: StrictInt
    idempotency_key: str
    reason: str
    supersedes_id: str | None = None
    supersedes_reason: str | None = None


class MigrationAssessmentSignoffRequest(StrictRequest):
    expected_version: StrictInt
    expected_digest: str
    active_only_acknowledged: StrictBool
    idempotency_key: str
    reason: str


class MigrationAssessmentSource(StrictResponse):
    id: str
    source_id: str
    source_run_id: str
    source_kind: str
    envelope_hash: str
    ingested_at: str


class MigrationAssessmentSummary(StrictResponse):
    id: str
    source_batch_id: str
    source: MigrationAssessmentSource | None
    canonical_hash: str
    domain: str
    mapping_revision: str
    authority_revision: str
    policy_revision: str
    baseline_version: int
    input_count: int
    accepted_count: int
    rejected_count: int
    duplicate_count: int
    added_count: int
    changed_count: int
    unchanged_count: int
    conflicting_count: int
    active_only_acknowledged: bool
    active_only_count: int
    created_by: str | None
    created_by_current_principal: bool
    created_at: str
    version: int
    state: str
    signer_id: str | None
    signed_by_current_principal: bool
    signed_at: str | None
    signoff_reason: str | None
    supersedes_id: str | None
    supersedes_reason: str | None
    digest: str
    current: bool
    staleness_reasons: list[str]


class MigrationAssessmentRow(StrictResponse):
    source_record_id: str
    matching_key: str
    candidate: dict[str, Any]
    active: dict[str, Any] | None
    disposition: str
    reason: str


class MigrationAssessmentActiveOnly(StrictResponse):
    matching_key: str
    active: dict[str, Any]
    reason: str


class MigrationAssessmentDetail(MigrationAssessmentSummary):
    rows: list[MigrationAssessmentRow]
    active_only: list[MigrationAssessmentActiveOnly]


class MigrationAssessmentPage(StrictResponse):
    items: list[MigrationAssessmentSummary]
    total: int
    limit: int
    offset: int
    baseline_version: int


class MigrationAssessmentCreateOutcome(StrictResponse):
    assessment_id: str
    assessment_digest: str


class MigrationAssessmentSignoffOutcome(StrictResponse):
    assessment_id: str
    assessment_digest: str
    signer_id: str | None
    signed_by_current_principal: bool
    signed_at: str
    signed_version: int


class MigrationAssessmentMutation(StrictResponse):
    assessment: MigrationAssessmentSummary
    replayed: bool
    original_signoff: MigrationAssessmentSignoffOutcome | None


class MigrationOperationReadback(StrictResponse):
    found: bool
    action: Literal["assessment.create", "assessment.signoff"]
    assessment: MigrationAssessmentDetail | None
    original_outcome: MigrationAssessmentCreateOutcome | MigrationAssessmentSignoffOutcome | None


class ReservationHistoryEntry(StrictResponse):
    """Sanitized reservation history entry; raw before_json/after_json never leave the API."""

    id: str
    reservation_id: str
    version: int
    action: str
    actor_id: str | None
    occurred_at: str
    reason: str
    before: dict[str, Any] | None
    after: dict[str, Any]


class ReservationSummary(StrictResponse):
    """Sanitized reservation projection; foreign actor identity is redacted to None."""

    id: str
    scope_id: str
    prefix_id: str
    pool_id: str
    family: int
    address: str
    owner_reference: str
    service_reference: str
    created_by: str | None
    reason: str
    created_at: str
    expires_at: str
    version: int
    policy_revision: str
    state: str
    converted_allocation_id: str | None
    released_at: str | None
    synthetic: bool


class ReservationDetail(ReservationSummary):
    history: list[ReservationHistoryEntry]


class ReservationReleaseRequest(StrictResponse):
    """Sanitized release proposal/decision; idempotency keys and payload digests stay hidden."""

    id: str
    reservation_id: str
    reservation_version: int
    requester_id: str | None
    reason: str
    expected_pool_version: int
    expected_baseline_version: int
    state: str
    created_at: str
    decided_at: str | None
    approver_id: str | None
    decision_reason: str | None
    synthetic: bool
