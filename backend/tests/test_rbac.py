import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.core.auth import AuthenticatedUser
from app.core.permissions import RoleEnum
from app.db.session import get_db_session
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    return MagicMock()


def create_mock_user(role: str) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=uuid.uuid4(),
        email=f"{role}@example.com",
        display_name=f"{role.capitalize()} User",
        role=role,
    )


def test_viewer_access_denied_to_admin_route(mock_db_session):
    viewer = create_mock_user(RoleEnum.VIEWER.value)

    app.dependency_overrides[get_current_user] = lambda: viewer
    app.dependency_overrides[get_db_session] = lambda: mock_db_session

    response = client.get("/api/v1/admin/users")
    assert response.status_code == 403
    response_data = response.json()
    # FastAPI wraps HTTPException detail at top level for dict details
    assert "message" in response_data or ("detail" in response_data and isinstance(response_data["detail"], dict))

    app.dependency_overrides.clear()


def test_admin_access_allowed_to_admin_route(mock_db_session):
    admin = create_mock_user(RoleEnum.ADMIN.value)

    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_db_session] = lambda: mock_db_session

    mock_db_session.scalars.return_value.all.return_value = []

    response = client.get("/api/v1/admin/users")
    assert response.status_code == 200

    app.dependency_overrides.clear()


def test_analyst_access_denied_to_admin_route(mock_db_session):
    analyst = create_mock_user(RoleEnum.ANALYST.value)

    app.dependency_overrides[get_current_user] = lambda: analyst
    app.dependency_overrides[get_db_session] = lambda: mock_db_session

    response = client.get("/api/v1/admin/users")
    assert response.status_code == 403

    app.dependency_overrides.clear()


def test_role_updates_audit_logging(mock_db_session):
    admin = create_mock_user(RoleEnum.ADMIN.value)
    target_user_id = uuid.uuid4()

    mock_target_user = MagicMock()
    mock_target_user.id = target_user_id
    mock_target_user.role = RoleEnum.VIEWER.value
    mock_target_user.email = "target@example.com"
    mock_target_user.display_name = "Target"
    
    # We also need a proper pydantic model serialization or dict behavior when returning from route
    class MockUserReturn:
        id = target_user_id
        email = "target@example.com"
        display_name = "Target"
        role = RoleEnum.ANALYST.value

    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[get_db_session] = lambda: mock_db_session

    mock_db_session.get.side_effect = [mock_target_user, mock_target_user, MockUserReturn()]

    response = client.patch(
        f"/api/v1/admin/users/{target_user_id}/role", json={"role": RoleEnum.ANALYST.value}
    )

    assert response.status_code == 200

    # Verify Audit log was created
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()

    args, kwargs = mock_db_session.add.call_args
    audit_log = args[0]

    assert audit_log.actor_user_id == str(admin.id)
    assert audit_log.target_user_id == str(target_user_id)
    assert audit_log.action == "UPDATE_USER_ROLE"
    assert "viewer to analyst" in audit_log.details

    app.dependency_overrides.clear()


def test_prevent_viewer_to_admin_by_non_admin(mock_db_session):
    analyst = create_mock_user(RoleEnum.ANALYST.value)
    target_user_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: analyst
    app.dependency_overrides[get_db_session] = lambda: mock_db_session

    response = client.patch(
        f"/api/v1/admin/users/{target_user_id}/role", json={"role": RoleEnum.ADMIN.value}
    )

    assert response.status_code == 403

    app.dependency_overrides.clear()

def test_viewer_can_view_findings(mock_db_session):
    viewer = create_mock_user(RoleEnum.VIEWER.value)
    analysis_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: viewer
    app.dependency_overrides[get_db_session] = lambda: mock_db_session
    
    # Mock get_analysis_service dependency because it requires many DB/Azure services
    from app.api.dependencies import get_analysis_service
    mock_analysis_service = MagicMock()
    mock_analysis_service.get_findings.return_value = []
    
    app.dependency_overrides[get_analysis_service] = lambda: mock_analysis_service

    response = client.get(f"/api/v1/analysis/{analysis_id}/findings")
    assert response.status_code == 200
    
    app.dependency_overrides.clear()

def test_viewer_cannot_create_analysis(mock_db_session):
    viewer = create_mock_user(RoleEnum.VIEWER.value)

    app.dependency_overrides[get_current_user] = lambda: viewer
    app.dependency_overrides[get_db_session] = lambda: mock_db_session

    response = client.post(
        "/api/v1/analysis", 
        json={
            "subscription_id": "00000000-0000-0000-0000-000000000000",
            "resource_group": "test-rg"
        }
    )
    assert response.status_code == 403

    app.dependency_overrides.clear()
