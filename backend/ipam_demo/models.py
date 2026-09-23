"""HTTP response contract; all large address counts are decimal strings."""

from typing import Annotated, Any, Generic, Literal, TypeVar, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, StrictBool, StrictInt, model_validator


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


class TicketRouteAssignment(StrictResponse):
    assignment_version: int
    configuration_revision: str
    route_revision: str
    team: str | None
    reason: str | None
    assigned_at: str
    assigned_by: str | None


class TicketAttempt(StrictResponse):
    id: str
    ordinal: int
    route_assignment_version: int
    synthetic_scenario: Literal["success", "definitive_failure", "committed_response_lost", "no_effect_response_lost"]
    started_at: str
    observation_deadline_at: str
    ended_at: str | None
    result: Literal["pending", "unknown", "delivered", "failed"]
    reason: str | None
    observed_ticket_id: str | None
    observed_effect_id: str | None


class TicketHandoffEvent(StrictResponse):
    id: str
    event_type: Literal["readback", "recipient_acknowledgement"]
    outcome: str
    resolution: str | None
    attempt_id: str | None
    effect_id: str | None
    returned_ticket_id: str | None
    error_code: str | None
    acknowledgement_mode: str | None
    occurred_at: str
    actor_id: str | None


class TicketHandoffSummary(StrictResponse):
    id: str
    domain: str
    source_request_id: str
    source_request_state: str
    action: Literal["allocation.request"]
    correlation: str
    business_payload_digest: str
    business_payload: dict[str, str | int]
    contract_version: Literal["internal-ticket-simulator/v1"]
    mode: Literal["simulated"]
    state: Literal["pending", "routing_blocked", "unknown", "delivered", "failed"]
    version: int
    created_at: str
    current_route_assignment_version: int
    route: TicketRouteAssignment
    attempt_limit: int
    attempts_used: int
    attempts_remaining: int
    observation_budget_seconds: int
    latest_attempt: TicketAttempt | None
    readback_required: bool
    resolution_reason: str | None
    recipient_acknowledged: bool
    provisioning_status: Literal["not_requested"]
    label: str
    simulated: bool
    synthetic: bool
    availability_evaluated: bool
    attempt_allowed: bool | None
    attempt_block_reason: str | None
    reassignment_allowed: bool | None


class TicketHandoffDetail(TicketHandoffSummary):
    route_history: list[TicketRouteAssignment]
    attempts: list[TicketAttempt]
    events: list[TicketHandoffEvent]


class TicketAttemptOperation(StrictResponse):
    phase: Literal["reserve", "effect", "observe"]
    attempt: TicketAttempt
    effect_phase_recorded: bool | None = None


class TicketAssignmentOperation(StrictResponse):
    phase: Literal["reassign"]
    assignment: TicketRouteAssignment


class TicketEventOperation(StrictResponse):
    phase: Literal["readback", "acknowledge"]
    event: TicketHandoffEvent


class TicketHandoffMutation(StrictResponse):
    handoff: TicketHandoffDetail
    operation: TicketAttemptOperation | TicketAssignmentOperation | TicketEventOperation


class TicketHandoffOriginalOperation(StrictResponse):
    phase: Literal["reserve", "reassign", "readback", "acknowledge"]
    attempt: TicketAttempt | None = None
    assignment: TicketRouteAssignment | None = None
    event: TicketHandoffEvent | None = None


class TicketHandoffOperationReadback(StrictResponse):
    found: bool
    action: Literal["ticket.attempt", "ticket.reassign", "ticket.readback", "ticket.acknowledge"]
    original_operation: TicketHandoffOriginalOperation | None
    current_handoff: TicketHandoffDetail | None


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


class ReservationOperationReadback(StrictResponse):
    """Exact-key recovery readback; a missing own-key record returns found=false and null outcomes."""

    found: bool
    action: Literal["reservation.create", "reservation.extend",
                    "reservation.release.propose", "reservation.release.decision"]
    original_outcome: ReservationSummary | ReservationReleaseRequest | None
    current_reservation: ReservationSummary | None
    current_release_request: ReservationReleaseRequest | None


NoticeDeliveryStatus = Literal["awaiting_receipt", "unassigned", "recipient_unavailable", "legacy_unbound",
                               "acknowledged"]
NoticeAcknowledgementKind = Literal["recipient_in_app", "legacy_operator"]


class AssignedNoticeNotification(StrictResponse):
    """Immutable binding to the reviewed Operator recipient for one notification version.

    recipient_id/acknowledged_by/acknowledgement_reason are visible only to that recipient; others get None.
    An in-app receipt is the recipient's explicit acknowledgement, never owner signoff or external delivery.
    """

    notice_id: str
    notification_version: int
    recipient_id: str | None
    configuration_revision: int
    configuration_digest: str
    routing_status: Literal["assigned"]
    routing_reason: None
    issued_at: str
    acknowledged_by: str | None
    acknowledged_at: str | None
    acknowledgement_reason: str | None
    delivery_status: Literal["awaiting_receipt", "recipient_unavailable", "acknowledged"]
    is_current_recipient: bool
    acknowledgement_kind: Literal["recipient_in_app"] | None
    owner_signoff: Literal[False]
    in_app_receipt: bool

    @model_validator(mode="after")
    def _receipt_consistent(self):
        received = self.acknowledged_at is not None
        if (received != (self.delivery_status == "acknowledged")
                or received != (self.acknowledgement_kind == "recipient_in_app")
                or received != self.in_app_receipt):
            raise ValueError("assigned notification receipt fields disagree")
        if (self.acknowledged_by is None) != (self.acknowledgement_reason is None):
            raise ValueError("own receipt identity and reason must be disclosed together")
        if not received and self.acknowledged_by is not None:
            raise ValueError("an unacknowledged notification cannot carry a receipt actor")
        if self.acknowledged_by is not None and self.acknowledged_by != self.recipient_id:
            raise ValueError("a recipient receipt must belong to the bound recipient")
        if self.is_current_recipient and self.recipient_id is None:
            raise ValueError("the current recipient must see its own binding")
        return self


class UnassignedNoticeNotification(StrictResponse):
    """No reviewed recipient mapping existed for the domain/scope when this version was bound."""

    notice_id: str
    notification_version: int
    recipient_id: None
    configuration_revision: int
    configuration_digest: str
    routing_status: Literal["unassigned"]
    routing_reason: Literal["missing_mapping"]
    issued_at: str
    acknowledged_by: None
    acknowledged_at: None
    acknowledgement_reason: None
    delivery_status: Literal["unassigned"]
    is_current_recipient: Literal[False]
    acknowledgement_kind: None
    owner_signoff: Literal[False]
    in_app_receipt: Literal[False]


class UnroutableNoticeNotification(StrictResponse):
    """A configured recipient was ineligible; only an allowlisted reason is disclosed, never credentials."""

    notice_id: str
    notification_version: int
    recipient_id: str | None
    configuration_revision: int
    configuration_digest: str
    routing_status: Literal["unroutable"]
    routing_reason: Literal["unknown_principal", "disabled", "expired", "not_operator", "wrong_domain"]
    issued_at: str
    acknowledged_by: None
    acknowledged_at: None
    acknowledgement_reason: None
    delivery_status: Literal["recipient_unavailable"]
    is_current_recipient: Literal[False]
    acknowledgement_kind: None
    owner_signoff: Literal[False]
    in_app_receipt: Literal[False]


class LegacyNoticeNotification(StrictResponse):
    """Schema6 version preserved by migration without an invented recipient, configuration or issue time.

    A retained acknowledgement is a legacy Operator acknowledgement, never a recipient in-app receipt.
    """

    notice_id: str
    notification_version: int
    recipient_id: None
    configuration_revision: None
    configuration_digest: None
    routing_status: Literal["legacy_unbound"]
    routing_reason: Literal["legacy_unbound"]
    issued_at: None
    acknowledged_by: str | None
    acknowledged_at: str | None
    acknowledgement_reason: str | None
    delivery_status: Literal["legacy_unbound"]
    is_current_recipient: Literal[False]
    acknowledgement_kind: Literal["legacy_operator"] | None
    owner_signoff: Literal[False]
    in_app_receipt: Literal[False]

    @model_validator(mode="after")
    def _legacy_consistent(self):
        received = self.acknowledged_at is not None
        if received != (self.acknowledgement_kind == "legacy_operator"):
            raise ValueError("legacy acknowledgement fields disagree")
        if (self.acknowledged_by is None) != (self.acknowledgement_reason is None):
            raise ValueError("own legacy identity and reason must be disclosed together")
        if not received and self.acknowledged_by is not None:
            raise ValueError("an unacknowledged legacy version cannot carry an actor")
        return self


ReservationNoticeNotification = Annotated[
    Union[AssignedNoticeNotification, UnassignedNoticeNotification,
          UnroutableNoticeNotification, LegacyNoticeNotification],
    Field(discriminator="routing_status")]


class ReservationNotice(StrictResponse):
    """Local reservation notice episode with its immutable per-version recipient binding history.

    Top-level delivery/receipt fields mirror current_notification. A configured recipient is not a proven
    business owner: owner_signoff is always false and resolution never implies delivery or acknowledgement.
    Parent acknowledged_by/acknowledgement_reason are visible only to that principal.
    """

    id: str
    reservation_id: str
    episode_number: int
    policy_revision: str
    first_due_at: str
    alert_level: Literal["alert", "alarm"]
    owner_reference: str
    state: Literal["open", "acknowledged", "resolved"]
    acknowledgement_version: int
    notification_version: int
    acknowledged_at: str | None
    acknowledged_by: str | None
    acknowledgement_reason: str | None
    acknowledgement_current: bool
    current_notification: ReservationNoticeNotification | None
    notification_history: list[ReservationNoticeNotification]
    notification_history_coverage: Literal["complete", "partial", "partial_legacy", "missing_child"]
    delivery_status: NoticeDeliveryStatus | None
    is_current_recipient: bool
    acknowledgement_kind: NoticeAcknowledgementKind | None
    owner_signoff: Literal[False]
    in_app_receipt: bool
    resolved_at: str | None
    resolution_reason: Literal["reservation_extended", "reservation_converted", "approved_local_release"] | None
    synthetic: Literal[True]

    @model_validator(mode="after")
    def _history_consistent(self):
        current = self.current_notification
        versions = [item.notification_version for item in self.notification_history]
        if any(item.notice_id != self.id for item in self.notification_history):
            raise ValueError("notification history belongs to another notice")
        if any(later <= earlier for earlier, later in zip(versions, versions[1:])):
            raise ValueError("notification history must be strictly ordered by version")
        if current is None:
            coverage = "missing_child"
            mirrored = (None, False, None, False)
        else:
            if current.notice_id != self.id or current.notification_version != self.notification_version:
                raise ValueError("current notification is not the notice's current version")
            if not any(item == current for item in self.notification_history):
                raise ValueError("current notification is missing from its retained history")
            if any(item.routing_status == "legacy_unbound" for item in self.notification_history):
                coverage = "partial_legacy"
            elif versions != list(range(1, self.notification_version + 1)):
                coverage = "partial"
            else:
                coverage = "complete"
            mirrored = (current.delivery_status, current.is_current_recipient,
                        current.acknowledgement_kind, current.in_app_receipt)
        if self.notification_history_coverage != coverage:
            raise ValueError("notification history coverage disagrees with retained versions")
        if (self.delivery_status, self.is_current_recipient, self.acknowledgement_kind,
                self.in_app_receipt) != mirrored:
            raise ValueError("notice receipt summary disagrees with its current notification")
        expected_current = (current is not None and self.state == "acknowledged"
                            and current.acknowledgement_kind == "recipient_in_app"
                            and current.delivery_status == "acknowledged")
        if self.acknowledgement_current != expected_current:
            raise ValueError("acknowledgement_current disagrees with the current recipient receipt")
        if (self.acknowledged_by is None) != (self.acknowledgement_reason is None):
            raise ValueError("own parent acknowledgement identity and reason must be disclosed together")
        return self


class _NoticeNotificationParent(StrictResponse):
    reservation_id: str
    episode_number: int


class AssignedNoticeNotificationVersion(AssignedNoticeNotification, _NoticeNotificationParent):
    pass


class UnassignedNoticeNotificationVersion(UnassignedNoticeNotification, _NoticeNotificationParent):
    pass


class UnroutableNoticeNotificationVersion(UnroutableNoticeNotification, _NoticeNotificationParent):
    pass


class LegacyNoticeNotificationVersion(LegacyNoticeNotification, _NoticeNotificationParent):
    pass


class ReservationNoticeNotificationVersion(RootModel[Annotated[
        Union[AssignedNoticeNotificationVersion, UnassignedNoticeNotificationVersion,
              UnroutableNoticeNotificationVersion, LegacyNoticeNotificationVersion],
        Field(discriminator="routing_status")]]):
    """Exact immutable notification version for recovery; current authorization and own-receipt redaction apply."""


class ReservationNoticeEvaluation(StrictResponse):
    """Server-UTC evaluation result; notices is the selected-domain canonical notice list."""

    evaluated_at: str
    created_count: int
    renewed_count: int
    alarm_upgrade_count: int
    notices: list[ReservationNotice]
    synthetic: Literal[True]

    @model_validator(mode="after")
    def _counts_consistent(self):
        if min(self.created_count, self.renewed_count, self.alarm_upgrade_count) < 0:
            raise ValueError("evaluation counts cannot be negative")
        if self.alarm_upgrade_count > self.renewed_count:
            raise ValueError("every alarm upgrade is also one renewed notification version")
        return self


class StaticOccupancyCount(StrictResponse):
    count: int
    unit: Literal["IPv4 addresses"]


class StaticReservedHolds(StaticOccupancyCount):
    includes_expired: Literal[True]


class StaticOccupancyComponents(StrictResponse):
    active_allocations: StaticOccupancyCount
    reserved_holds: StaticReservedHolds
    occupied_total: StaticOccupancyCount
    assignable_capacity: StaticOccupancyCount
    remaining_assignable: StaticOccupancyCount


class StaticOccupancyProvenance(StrictResponse):
    source: Literal["current local intended ledger"]
    capacity: str
    allocations: str
    reservations: str
    saved_runs_modified: Literal[False]
    synthetic: Literal[True]


class CurrentStaticOccupancy(StrictResponse):
    """Current local-static ledger occupancy; independent of immutable saved DHCP run metrics."""

    metric: Literal["current_static_ipv4_occupancy"]
    pool_id: str
    scope_id: str
    domain: str
    family: Literal[4]
    unit: Literal["IPv4 addresses"]
    as_of: str
    components: StaticOccupancyComponents
    provenance: StaticOccupancyProvenance
    synthetic: Literal[True]
