# AegisAI Connectors - Reports & Audit Module

Production-grade data models for KAN-14: Reports & Audit epic.

## Overview

This module implements:
- **Trust Reports**: AI evaluation reports with versioning and soft delete
- **Audit Trail**: Comprehensive system action logging
- **Deletion Logs**: Compliance tracking for report deletions

## Database Schema

### Tables
- `trust_reports` - Stores AI trust evaluation reports
- `audit_trails` - System-wide audit logging
- `deletion_logs` - Report deletion tracking

### ENUMs
- `report_status`: generating, completed, failed
- `report_type`: compliance, risk, bias, model_eval
- `action_type`: CREATE_REPORT, DELETE_REPORT, LOGIN, LOGOUT, etc.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run migration:
```bash
python run_migration.py
```

## Database Connection

Uses the same PostgreSQL database as `aegisai-auth`:
- **Database**: AegisAI
- **Host**: localhost:5432
- **Credentials**: From aegisai-auth/.env

## Features

### Trust Reports
- UUID primary keys
- User association with CASCADE delete
- JSONB for flexible payload storage
- Soft delete support (deleted_at)
- Automatic versioning
- Checksum validation
- Indexed for performance

### Audit Trail
- Comprehensive action logging
- IP address and user agent tracking
- JSONB metadata for flexible data
- Entity tracking (type + ID)
- Indexed for fast queries

### Deletion Logs
- Tracks soft and hard deletions
- Reason and metadata storage
- User and report association
- Compliance-ready

## Indexes

Optimized for:
- User queries (`user_id`)
- Status filtering (`status`)
- Time-based queries (`created_at`)
- Entity lookups (`entity_type`, `entity_id`)

## Relationships

```
User (1) ────< TrustReport (Many)
User (1) ────< AuditTrail (Many)
User (1) ────< DeletionLog (Many)
TrustReport (1) ────< DeletionLog (Many)
```

## Production Ready

✓ UUID primary keys
✓ Foreign key constraints
✓ Database-level ENUMs
✓ Comprehensive indexing
✓ Soft delete support
✓ Automatic timestamps
✓ Trigger for updated_at
✓ JSONB for flexibility
✓ Type safety (Python + TypeScript)

## Files

- `migrations/001_kan14_reports_audit.sql` - Database schema
- `src/modules/reports/models/__init__.py` - SQLAlchemy ORM models
- `src/modules/reports/models/types.ts` - TypeScript definitions
- `run_migration.py` - Migration runner
- `requirements.txt` - Python dependencies
