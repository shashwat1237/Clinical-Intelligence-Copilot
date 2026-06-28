from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID

class ConditionSchema(BaseModel):
    id: UUID
    name: str

class MedicationSchema(BaseModel):
    id: UUID
    name: str
    dosage: str
    frequency: str

class LabResultSchema(BaseModel):
    id: UUID
    parameter: str
    value: str
    unit: str
    is_abnormal: bool

class PatientProfileSchema(BaseModel):
    conditions: List[ConditionSchema]
    medications: List[MedicationSchema]
    labs: List[LabResultSchema]

class TimelineEventSchema(BaseModel):
    id: UUID
    date: str
    event_type: str
    description: str
    document_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)