from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class AuditResult(SQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    aws_service: str  
    resource_id: str  
    check_name: str  
    is_compliant: bool
    
    details: Optional[str] = None 
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)