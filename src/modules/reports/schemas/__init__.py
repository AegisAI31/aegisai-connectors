from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from src.modules.reports.models import ReportType, ReportStatus


class GenerateReportRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    report_type: ReportType
    input_payload: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class ReportResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    description: Optional[str]
    report_type: ReportType
    status: ReportStatus
    storage_path: Optional[str]
    checksum_hash: Optional[str]
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SignedUrlResponse(BaseModel):
    report_id: str
    signed_url: str
    expires_in: int = 3600
