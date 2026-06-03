import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.core.auth import AuthenticatedUser
from app.db.session import get_db_session
from app.main import app

client = TestClient(app)


def test_tenant_me_endpoint():
    mock_user = AuthenticatedUser(
        id=uuid.uuid4(),
        email="user@tenant.local",
        display_name="Test User",
        role="viewer",
        tenant_id="tenant-12345-abc"
    )
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    response = client.get("/api/v1/tenant/me")
    assert response.status_code == 200
    assert response.json()["tenant_id"] == "tenant-12345-abc"
    
    app.dependency_overrides.clear()


def test_tenant_stats_endpoint():
    mock_user = AuthenticatedUser(
        id=uuid.uuid4(),
        email="admin@tenant.local",
        display_name="Admin User",
        role="admin",
        tenant_id="tenant-12345-abc"
    )
    
    mock_db = MagicMock()
    # We simulate the 3 sequential func.count queries executed by db.scalar()
    mock_db.scalar.side_effect = [3, 10, 250] 

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db_session] = lambda: mock_db

    response = client.get("/api/v1/tenant/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant-12345-abc"
    assert data["user_count"] == 3
    assert data["analysis_count"] == 10
    assert data["resource_count"] == 250

    app.dependency_overrides.clear()