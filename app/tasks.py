import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine
from app.models import AuditResult
from app.auditor import S3Auditor, IAMAuditor, EC2Auditor

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
s3_auditor = S3Auditor()
iam_auditor = IAMAuditor()
ec2_auditor = EC2Auditor()

async def run_full_audit():
    """
    Orchestrates the full audit for ALL services.
    """
    print("Background Task: Starting Cloud Audit...")

    async with async_session() as session:
        
        # --- S3 AUDIT ---
        print("--- Starting S3 Audit ---")
        buckets = await asyncio.to_thread(s3_auditor.list_buckets)
        for bucket in buckets:
            print(f"Scanning S3 bucket: {bucket}")
            audit_data = await asyncio.to_thread(s3_auditor.check_bucket_versioning, bucket)
            session.add(AuditResult(**audit_data))
        
        # --- IAM AUDIT ---
        print("--- Starting IAM Audit ---")
        users = await asyncio.to_thread(iam_auditor.list_users)
        print(f"Found {len(users)} IAM users.")
        
        for user in users:
            print(f"Scanning IAM user: {user}")
            audit_data = await asyncio.to_thread(iam_auditor.check_mfa_enabled, user)
            session.add(AuditResult(**audit_data))

        # --- EC2 SECURITY GROUP AUDIT ---
        print("--- Starting EC2 Security Group Audit ---")
        sgs = await asyncio.to_thread(ec2_auditor.list_security_groups)
        print(f"Found {len(sgs)} Security Groups.")

        for sg_id in sgs:
            print(f"Scanning Security Group: {sg_id}")
            audit_data = await asyncio.to_thread(ec2_auditor.check_ssh_open_to_world, sg_id)
            session.add(AuditResult(**audit_data))

        # Commit everything
        await session.commit()
    
    print("Background Task: Cloud Audit Completed.")