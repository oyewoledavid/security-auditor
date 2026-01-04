import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlmodel import select, col, delete

from app.database import init_db, get_session
from app.models import AuditResult
from app.auditor import S3Auditor
from app.tasks import run_full_audit


auditor = S3Auditor()
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup: Initializing Database...")
    await init_db() # This will see AuditResult and create the table
    yield
    print("Shutdown: Closing connections...")

app = FastAPI(title="Cloud Resource Auditor", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Cloud Resource Auditor"}

@app.get("/audit-results/", response_model=List[AuditResult])
async def get_audit_results(
    service: Optional[str] = None,
    compliant: Optional[bool] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Fetch audit results with optional filtering.
    - **service**: Filter by AWS service (e.g., 's3', 'iam')
    - **compliant**: Filter by compliance status (true/false)
    """
    query = select(AuditResult)

    if service:
        query = query.where(AuditResult.aws_service == service)
    
    if compliant is not None:
        query = query.where(AuditResult.is_compliant == compliant)

    query = query.order_by(AuditResult.timestamp.desc())

    result = await session.execute(query)
    return result.scalars().all()
    

@app.post("/audit/run-full-scan", status_code=202)
async def run_full_cloud_scan(background_tasks: BackgroundTasks):
    """
    Triggers a full background scan of ALL configured AWS services (S3, IAM, etc.).
    """
    background_tasks.add_task(run_full_audit)
    return {"message": "Full cloud audit started in background."}

@app.post("/audit/s3/{bucket_name}", response_model=AuditResult)
async def audit_s3_bucket(
    bucket_name: str, 
    session: AsyncSession = Depends(get_session)
    ):
    """
    Triggers an audit for a specific S3 bucket.
    """
    
    audit_data = await asyncio.to_thread(auditor.check_bucket_versioning, bucket_name)
    audit_result = AuditResult(**audit_data)
    
    # SAVE TO DB
    session.add(audit_result)
    await session.commit()
    await session.refresh(audit_result)
    
    return audit_result

@app.get("/audit/stats")
async def get_audit_stats(session: AsyncSession = Depends(get_session)):
    """
    Returns a summary of compliance status.
    """
    async def count_query(q):
        result = await session.execute(q)
        return len(result.all()) 

    total_checks = await count_query(select(AuditResult))
    passed_checks = await count_query(select(AuditResult).where(AuditResult.is_compliant == True))
    failed_checks = await count_query(select(AuditResult).where(AuditResult.is_compliant == False))

    compliance_score = 0
    if total_checks > 0:
        compliance_score = round((passed_checks / total_checks) * 100, 2)

    return {
        "total_checks": total_checks,
        "passed": passed_checks,
        "failed": failed_checks,
        "compliance_score_percent": compliance_score
    }

@app.delete("/audit-results/clear")
async def clear_audit_results(session: AsyncSession = Depends(get_session)):
    statement = delete(AuditResult)
    await session.execute(statement)
    await session.commit()
    return {"message": "All audit history cleared."}