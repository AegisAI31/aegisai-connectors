from sqlalchemy import Column, String, Text, Integer, ForeignKey, TIMESTAMP, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class ReportStatus(str, enum.Enum):
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportType(str, enum.Enum):
    COMPLIANCE = "compliance"
    RISK = "risk"
    BIAS = "bias"
    MODEL_EVAL = "model_eval"


class ActionType(str, enum.Enum):
    CREATE_REPORT = "CREATE_REPORT"
    DELETE_REPORT = "DELETE_REPORT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE_API_KEY = "CREATE_API_KEY"
    REVOKE_API_KEY = "REVOKE_API_KEY"
    TRUST_EVALUATION = "TRUST_EVALUATION"


class TrustReport(Base):
    __tablename__ = "trust_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255))
    description = Column(Text)
    report_type = Column(Enum(ReportType, name="report_type"), nullable=False, index=True)
    status = Column(Enum(ReportStatus, name="report_status"), default=ReportStatus.GENERATING, index=True)
    input_payload = Column(JSONB)
    output_summary = Column(Text)
    output_full_report = Column(JSONB)
    storage_path = Column(Text)
    checksum_hash = Column(Text)
    version = Column(Integer, default=1)
    deleted_at = Column(TIMESTAMP, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="trust_reports")


class AuditTrail(Base):
    __tablename__ = "audit_trails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action_type = Column(Enum(ActionType, name="action_type"), nullable=False, index=True)
    entity_type = Column(String(100), index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    metadata = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_trails")


class DeletionLog(Base):
    __tablename__ = "deletion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    deletion_type = Column(String(20), CheckConstraint("deletion_type IN ('soft', 'hard')"))
    reason = Column(Text)
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="deletion_logs")
