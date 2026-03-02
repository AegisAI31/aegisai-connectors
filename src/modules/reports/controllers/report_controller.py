from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from src.modules.reports.schemas import GenerateReportRequest, ReportResponse, SignedUrlResponse
from src.modules.reports.services.report_service import ReportService
from src.core.middleware.auth import get_current_user
from src.db.base import get_db
from uuid import UUID

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate", response_model=ReportResponse, status_code=201)
async def generate_report(
    request_data: GenerateReportRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new trust report
    
    - Validates input
    - Generates PDF
    - Uploads to S3
    - Stores metadata in PostgreSQL
    - Logs audit trail
    
    Requires JWT authentication.
    """
    user_id = UUID(current_user["id"])
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    service = ReportService(db)
    report = service.generate_report(
        user_id=user_id,
        request=request_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report by ID
    
    Only the report owner can access it.
    """
    user_id = UUID(current_user["id"])
    service = ReportService(db)
    report = service.get_report(report_id, user_id)
    
    return report


@router.get("/{report_id}/download", response_model=SignedUrlResponse)
async def get_download_url(
    report_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get presigned S3 URL for report download
    
    URL expires in 1 hour.
    Only the report owner can download.
    """
    user_id = UUID(current_user["id"])
    service = ReportService(db)
    signed_url = service.get_signed_url(report_id, user_id)
    
    return SignedUrlResponse(
        report_id=str(report_id),
        signed_url=signed_url,
        expires_in=3600
    )


@router.get("/", response_model=list[ReportResponse])
async def list_reports(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all reports for the current user
    
    Supports pagination.
    """
    from src.modules.reports.models import TrustReport
    
    user_id = UUID(current_user["id"])
    reports = db.query(TrustReport).filter(
        TrustReport.user_id == user_id,
        TrustReport.deleted_at.is_(None)
    ).order_by(TrustReport.created_at.desc()).offset(skip).limit(limit).all()
    
    return reports
