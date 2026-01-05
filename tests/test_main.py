import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

# This marker tells pytest this is an async test
@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Cloud Resource Auditor"}

@pytest.mark.asyncio
async def test_audit_results_unauthorized():
    """
    Ensure we cannot access protected routes without an API Key
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Try to access without header
        response = await ac.get("/audit-results/")
    
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}