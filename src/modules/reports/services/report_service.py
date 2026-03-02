from sqlalchemy.orm import Session
from src.modules.reports.models import TrustReport, ReportStatus, ReportType, ActionType
from src.modules.reports.schemas import GenerateReportRequest
from src.modules.reports.services.pdf_service import PDFService
from src.modules.reports.services.storage_service import S3StorageService
from src.modules.reports.services.audit_service import AuditService
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import HTTPException


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.pdf_service = PDFService()
        self.storage_service = S3StorageService()
        self.audit_service = AuditService()
    
    def generate_report(
        self,
        user_id: UUID,
        request: GenerateReportRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TrustReport:
        """
        Generate complete trust report with PDF and S3 storage
        
        Steps:
        1. Create report record in DB
        2. Generate PDF
        3. Upload to S3
        4. Compute checksum
        5. Update DB with storage path and checksum
        6. Log audit trail
        
        Args:
            user_id: User creating the report
            request: Report generation request
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            Created TrustReport
        """
        try:
            # Step 1: Create initial report record
            # Convert report_type to lowercase value
            report_type_value = request.report_type
            print(f"DEBUG: report_type received: {report_type_value}, type: {type(report_type_value)}")
            
            if isinstance(report_type_value, ReportType):
                report_type_value = report_type_value.value
                print(f"DEBUG: Converted enum to value: {report_type_value}")
            elif isinstance(report_type_value, str):
                report_type_value = report_type_value.lower()
                print(f"DEBUG: Converted string to lowercase: {report_type_value}")
            
            print(f"DEBUG: Final report_type_value: {report_type_value}")
            
            report = TrustReport(
                user_id=user_id,
                title=request.title,
                description=request.description,
                report_type=report_type_value,
                status="generating",
                input_payload=request.input_payload,
                output_summary="Report generated successfully.",
                version=1
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            # Step 2: Generate PDF
            report_type_str = report.report_type if isinstance(report.report_type, str) else report.report_type
            pdf_content = self.pdf_service.generate_report_pdf(
                title=report.title or f"{report_type_str.title()} Report",
                report_type=report_type_str,
                input_payload=report.input_payload or {},
                output_summary=report.output_summary,
                created_at=report.created_at
            )
            
            # Step 3: Upload to S3
            storage_path = self.storage_service.upload_pdf(
                file_content=pdf_content,
                report_id=str(report.id),
                user_id=str(user_id)
            )
            
            # Step 4: Compute checksum
            checksum = self.storage_service.compute_checksum(pdf_content)
            
            # Step 5: Update report with storage info
            report.storage_path = storage_path
            report.checksum_hash = checksum
            report.status = "completed"
            report.output_full_report = {
                "report_id": str(report.id),
                "generated_at": report.created_at.isoformat(),
                "file_size_bytes": len(pdf_content),
                "checksum": checksum
            }
            
            self.db.commit()
            self.db.refresh(report)
            
            # Step 6: Log audit trail
            self.audit_service.log_action(
                db=self.db,
                user_id=user_id,
                action_type="create_report",
                entity_type="TrustReport",
                entity_id=report.id,
                metadata={
                    "report_type": report.report_type,
                    "title": report.title,
                    "storage_path": storage_path
                },
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Convert UUIDs to strings for response
            report.id = str(report.id)
            report.user_id = str(report.user_id)
            
            return report
            
        except Exception as e:
            # Mark report as failed if it was created
            if 'report' in locals():
                report.status = "failed"
                self.db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {str(e)}"
            )
    
    def get_report(self, report_id: UUID, user_id: UUID) -> Optional[TrustReport]:
        """Get report by ID with owner validation (excludes soft-deleted)"""
        report = self.db.query(TrustReport).filter(
            TrustReport.id == report_id,
            TrustReport.user_id == user_id,
            TrustReport.is_deleted == "false",
            TrustReport.deleted_at.is_(None)
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report
    
    def get_signed_url(self, report_id: UUID, user_id: UUID) -> str:
        """Generate signed URL for report download"""
        report = self.get_report(report_id, user_id)
        
        if not report.storage_path:
            raise HTTPException(status_code=400, detail="Report file not available")
        
        signed_url = self.storage_service.generate_signed_url(report.storage_path)
        return signed_url
    
    def soft_delete_report(
        self,
        report_id: UUID,
        user_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """
        Soft delete a report (user-controlled deletion)
        
        - Verifies ownership
        - Sets deleted_at and is_deleted=true
        - Logs audit trail
        - Idempotent (returns success if already deleted)
        
        Args:
            report_id: Report UUID to delete
            user_id: Authenticated user UUID
            ip_address: Client IP for audit
            user_agent: Client user agent for audit
            
        Returns:
            dict with success status and message
            
        Raises:
            HTTPException 404 if report not found or not owned by user
        """
        try:
            # Fetch report with ownership check
            report = self.db.query(TrustReport).filter(
                TrustReport.id == report_id,
                TrustReport.user_id == user_id
            ).first()
            
            # Return 404 if not found or not owned (don't leak existence)
            if not report:
                raise HTTPException(status_code=404, detail="Report not found")
            
            # Idempotent: if already deleted, return success
            if report.is_deleted == "true" or report.deleted_at is not None:
                return {
                    "success": True,
                    "message": "Report deleted",
                    "report_id": str(report_id)
                }
            
            # Perform soft delete
            report.is_deleted = "true"
            report.deleted_at = datetime.utcnow()
            
            # Log audit trail
            self.audit_service.log_action(
                db=self.db,
                user_id=user_id,
                action_type="delete_report",
                entity_type="TrustReport",
                entity_id=report_id,
                metadata={
                    "report_type": report.report_type,
                    "title": report.title,
                    "deleted_at": report.deleted_at.isoformat()
                },
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Commit transaction
            self.db.commit()
            
            return {
                "success": True,
                "message": "Report deleted",
                "report_id": str(report_id)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete report: {str(e)}"
            )
