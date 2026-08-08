from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IncidentStage = Literal[
    "detection",
    "diagnosis",
    "prescription",
    "treatment",
    "evaluation",
    "closed",
]

ClosureOutcome = Literal["resolved", "crop_lost"]


class IncidentCreate(BaseModel):
    scan_id: int


class IncidentAdvance(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class IncidentPrescribe(BaseModel):
    registry_no: str = Field(min_length=1, max_length=40)
    surface_m2: float = Field(gt=0)
    notes: str | None = Field(default=None, max_length=2000)


class IncidentApplyTreatment(BaseModel):
    ack_unverified: bool = False
    notes: str | None = Field(default=None, max_length=500)


class IncidentAttachEvaluation(BaseModel):
    evaluation_scan_id: int


class IncidentEvaluate(BaseModel):
    improved: bool
    evaluation_scan_id: int | None = None
    notes: str | None = Field(default=None, max_length=2000)


class IncidentClose(BaseModel):
    outcome: ClosureOutcome
    notes: str | None = Field(default=None, max_length=2000)


class IncidentTreatmentSummary(BaseModel):
    id: int
    product_name: str
    safety_hours: int
    hours_remaining: float | None = None
    harvest_allowed: bool = False


class IncidentRead(BaseModel):
    id: int
    scan_id: int
    farm_id: int | None
    farm_name: str | None = None
    zone_id: int
    zone_name: str | None = None
    outbreak_event_id: int | None
    plague: str
    crop: str
    severity: int
    stage: IncidentStage
    closure_outcome: ClosureOutcome | None = None
    notes: str | None = None
    prescription_product_name: str | None = None
    prescription_registry_number: str | None = None
    prescription_dose_ml: float | None = None
    prescription_safety_hours: int | None = None
    treatment: IncidentTreatmentSummary | None = None
    evaluation_scan_id: int | None = None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
