# KAN-15: Report Generation & Storage Pipeline

Complete implementation of trust report generation with PDF rendering and S3 storage.

## Features

✅ **POST /api/reports/generate** - Generate new reports
✅ **GET /api/reports/{id}** - Get report by ID
✅ **GET /api/reports/{id}/download** - Get presigned S3 URL
✅ **GET /api/reports** - List user reports
✅ JWT Authentication middleware
✅ Owner-based access control
✅ PDF generation with ReportLab
✅ S3 upload with encryption
✅ SHA256 checksum validation
✅ Comprehensive audit logging
✅ Error handling

## Architecture

```
src/
├── main.py                          # FastAPI application
├── core/
│   └── middleware/
│       └── auth.py                  # JWT authentication
└── modules/
    └── reports/
        ├── controllers/
        │   └── report_controller.py # API endpoints
        ├── services/
        │   ├── report_service.py    # Business logic
        │   ├── pdf_service.py       # PDF generation
        │   ├── storage_service.py   # S3 operations
        │   └── audit_service.py     # Audit logging
        ├── schemas/
        │   └── __init__.py          # Pydantic DTOs
        └── models/
            └── __init__.py          # SQLAlchemy models
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Run server:
```bash
cd src
python main.py
```

Server runs on `http://localhost:8002`

## API Endpoints

### Generate Report
```http
POST /api/reports/generate
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Q4 Compliance Report",
  "description": "Quarterly compliance analysis",
  "report_type": "compliance",
  "input_payload": {
    "period": "Q4 2024",
    "models_evaluated": 15
  }
}
```

### Get Report
```http
GET /api/reports/{report_id}
Authorization: Bearer <jwt_token>
```

### Download Report
```http
GET /api/reports/{report_id}/download
Authorization: Bearer <jwt_token>
```

Returns presigned S3 URL valid for 1 hour.

### List Reports
```http
GET /api/reports?skip=0&limit=100
Authorization: Bearer <jwt_token>
```

## Pipeline Flow

1. **Validate Request** - Pydantic DTO validation
2. **Create DB Record** - Initial report with GENERATING status
3. **Generate PDF** - ReportLab rendering
4. **Upload to S3** - Encrypted storage
5. **Compute Checksum** - SHA256 hash
6. **Update DB** - Storage path, checksum, COMPLETED status
7. **Audit Log** - Record action in audit_trails table

## Security

- **JWT Authentication** - All endpoints require valid token
- **Owner Validation** - Users can only access their own reports
- **Presigned URLs** - Time-limited S3 access (1 hour)
- **S3 Encryption** - Server-side AES256 encryption
- **Checksum Validation** - SHA256 integrity verification

## Database Tables Used

- `trust_reports` - Report metadata and status
- `audit_trails` - Action logging
- `users` - User authentication (from aegisai-auth)

## Error Handling

- 401: Unauthorized (invalid/missing JWT)
- 404: Report not found
- 500: Generation failed (with rollback)

## Testing

```bash
# Get JWT token from aegisai-auth
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Generate report
curl -X POST http://localhost:8002/api/reports/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"report_type":"compliance","title":"Test Report"}'
```

## AWS S3 Setup

1. Create S3 bucket: `aegisai-reports`
2. Enable server-side encryption
3. Create IAM user with permissions:
   - `s3:PutObject`
   - `s3:GetObject`
   - `s3:GeneratePresignedUrl`
4. Add credentials to `.env`

## Integration

This service integrates with:
- **aegisai-auth** (port 8000) - User authentication
- **PostgreSQL** - Shared AegisAI database
- **AWS S3** - Report storage

## Production Checklist

- [ ] Configure AWS credentials
- [ ] Set up S3 bucket with encryption
- [ ] Configure CORS for frontend
- [ ] Set up monitoring/logging
- [ ] Configure backup strategy
- [ ] Set up CDN for S3 (optional)
