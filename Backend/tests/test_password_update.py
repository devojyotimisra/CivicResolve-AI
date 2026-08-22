import pytest
from sqlalchemy.orm import Session

from application.extensions.security_extn import hash_password, verify_password
from application.helpers.models import Role, User
from application.middlewares.init_jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        email="test.password@civicresolve.in",
        password=hash_password("OldPassword123!"),
        name="Password Test",
        role="citizen",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


def test_password_update_success(client, auth_headers, test_user, db_session):
    payload = {"current_password": "OldPassword123!", "new_password": "NewStrongPassword456!"}
    response = client.put("/api/update_password", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully!"

    db_session.refresh(test_user)
    assert verify_password("NewStrongPassword456!", test_user.password) is True
    assert verify_password("OldPassword123!", test_user.password) is False


def test_password_update_wrong_current_password(client, auth_headers, test_user, db_session):
    payload = {"current_password": "WrongPassword123!", "new_password": "NewStrongPassword456!"}
    response = client.put("/api/update_password", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect."

    db_session.refresh(test_user)
    assert verify_password("OldPassword123!", test_user.password) is True


def test_password_update_invalid_new_password(client, auth_headers, test_user):
    payload = {"current_password": "OldPassword123!", "new_password": "123"}
    response = client.put("/api/update_password", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Password must be at least 8 characters long and contain a number and a special character."
    )


def test_password_update_unauthenticated(client):
    payload = {"current_password": "OldPassword123!", "new_password": "NewStrongPassword456!"}
    response = client.put("/api/update_password", json=payload)
    assert response.status_code == 401
