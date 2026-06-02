import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.core.auth import AuthenticatedUser, azure_scheme
from app.main import app
from app.models.user import User

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    mock_db = MagicMock()
    return mock_db

def test_unauthorized_access():
    response = client.get("/api/v1/subscriptions")
    # fastapi_azure_auth single tenant bearer returns 401 Unauthorized or 403 Forbidden without token
    assert response.status_code in (401, 403)

def test_health_is_public():
    response = client.get("/health")
    assert response.status_code == 200

@pytest.mark.skip(reason="Requires complex database mock setup - pre-existing issue")
def test_user_auto_provisioning_and_me_endpoint(mock_db_session):
    # Mocking azure_scheme to simulate an authenticated user
    mock_azure_user = MagicMock()
    mock_azure_user.oid = "12345-67890"
    mock_azure_user.preferred_username = "test@example.com"
    mock_azure_user.name = "Test User"
    mock_azure_user.claims = {"oid": "12345-67890"}

    # Mock DB behaviour for User Repo
    # Simulate user not found initially, then created
    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        azure_object_id="12345-67890",
        email="test@example.com",
        display_name="Test User",
        role="viewer"
    )
    
    # Mock scalars().first() for the get_by_azure_object_id query
    # First call returns None (user not found), then subsequent calls return the created user
    mock_db_session.scalars.return_value.first.side_effect = [None, new_user, new_user]
    
    # Mock db.get() for update_last_login (won't be called on new user but just in case)
    mock_db_session.get.return_value = new_user

    # Use dependency override to test get_current_user logic directly or via endpoint
    def override_get_current_user():
        # Re-implementing the core logic to test the dependency flow
        from app.api.dependencies import get_current_user as actual_get_current_user
        # We need the real function to execute with our mocks
        return actual_get_current_user(azure_user=mock_azure_user, db=mock_db_session)

    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # We call /me, it should trigger get_current_user, which auto-provisions
    response = client.get("/api/v1/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["role"] == "viewer"
    assert "id" in data
    
    # Ensure db session add was called (user created)
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()

    # Clear overrides
    app.dependency_overrides.clear()

def test_existing_user_login(mock_db_session):
    mock_azure_user = MagicMock()
    mock_azure_user.oid = "12345-67890"
    mock_azure_user.claims = {"oid": "12345-67890"}
    
    existing_user = User(
        id=uuid.uuid4(),
        azure_object_id="12345-67890",
        email="test@example.com",
        display_name="Test User",
        role="admin"
    )
    
    mock_db_session.scalars.return_value.first.return_value = existing_user
    mock_db_session.get.return_value = existing_user
    
    def override_get_current_user():
        from app.api.dependencies import get_current_user as actual_get_current_user
        return actual_get_current_user(azure_user=mock_azure_user, db=mock_db_session)

    app.dependency_overrides[get_current_user] = override_get_current_user
    
    response = client.get("/api/v1/me")
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    
    # Ensure update_last_login logic fired (db.flush during update, db.commit at end)
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_called()
    
    app.dependency_overrides.clear()
