import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role
from application.middlewares.init_jwt import create_access_token, get_current_user_id


@pytest.fixture
def active_citizen(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="citizen").first()
    if not role:
        role = Role(name="citizen")
        db_session.add(role)

    user = User(
        email="citizen.auth@example.com",
        password=hash_password("Secret123!"),
        name="Auth Test Citizen",
        role="citizen",
        phone="9876543210",
        address="123 Auth Street",
        pincode="110001",
        is_active=True
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def active_officer(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="field_officer").first()
    if not role:
        role = Role(name="field_officer")
        db_session.add(role)

    user = User(
        email="officer.auth@example.com",
        password=hash_password("Secret123!"),
        name="Auth Test Officer",
        role="field_officer",
        badge_id="BADGE-777",
        phone="9876543211",
        address="Officer HQ",
        pincode="110001",
        is_active=True
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def deactivated_user(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="citizen").first()
    if not role:
        role = Role(name="citizen")
        db_session.add(role)

    user = User(
        email="deactivated@example.com",
        password=hash_password("Secret123!"),
        name="Deactivated User",
        role="citizen",
        is_active=False
    )
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success_with_email(client, active_citizen):
    response = client.post("/api/login", json={
        "email": "citizen.auth@example.com",
        "password": "Secret123!"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "token" in data and isinstance(data["token"], str)
    assert data["user"]["id"] == active_citizen.id
    assert data["user"]["email"] == "citizen.auth@example.com"
    assert data["user"]["name"] == "Auth Test Citizen"
    assert data["user"]["role"] == "citizen"


def test_login_success_with_badge_id(client, active_officer):
    response = client.post("/api/login", json={
        "email": "BADGE-777",
        "password": "Secret123!"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["user"]["badgeId"] == "BADGE-777"
    assert data["user"]["role"] == "officer"


def test_login_invalid_password(client, active_citizen):
    response = client.post("/api/login", json={
        "email": "citizen.auth@example.com",
        "password": "WrongPassword123"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"


def test_login_user_not_found(client, db_session):
    response = client.post("/api/login", json={
        "email": "nonexistent@example.com",
        "password": "Secret123!"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"


def test_login_deactivated_account(client, deactivated_user):
    response = client.post("/api/login", json={
        "email": "deactivated@example.com",
        "password": "Secret123!"
    })

    assert response.status_code == 403
    assert response.json()["detail"] == "Account has been deactivated"


def test_login_missing_required_fields(client):
    resp1 = client.post("/api/login", json={"password": "Secret123!"})
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Email or Badge ID is required"
    resp2 = client.post("/api/login", json={"email": "citizen.auth@example.com"})
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Password is required"
    response = client.post("/api/login", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email or Badge ID is required"


def test_signup_success(client, db_session):
    payload = {
        "email": "new.citizen@example.com",
        "password": "SecurePassword123",
        "name": "Jane Citizen",
        "address": "456 Civic Blvd",
        "pincode": "110002",
        "phone": "9876543299"
    }

    response = client.post("/api/signup", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Account created successfully"
    assert "token" in data
    assert data["user"]["email"] == "new.citizen@example.com"
    assert data["user"]["role"] == "citizen"
    created_user = db_session.query(User).filter_by(email="new.citizen@example.com").first()
    assert created_user is not None
    assert created_user.name == "Jane Citizen"


def test_signup_duplicate_email(client, active_citizen):
    payload = {
        "email": "citizen.auth@example.com",
        "password": "SecurePassword123",
        "name": "Another Citizen",
        "address": "789 Another St",
        "pincode": "110003"
    }

    response = client.post("/api/signup", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.parametrize("invalid_field, payload, expected_detail", [
    ("email_format", {"email": "invalid-email", "password": "Pass123", "name": "Name", "address": "Address 123", "pincode": "110001"}, "Invalid email format"),
    ("short_password", {"email": "valid@example.com", "password": "123", "name": "Name", "address": "Address 123", "pincode": "110001"}, "Password must be at least 5 characters long"),
    ("short_name", {"email": "valid@example.com", "password": "Password123", "name": "A", "address": "Address 123", "pincode": "110001"}, "Name must be at least 2 characters long"),
    ("short_address", {"email": "valid@example.com", "password": "Password123", "name": "Valid Name", "address": "123", "pincode": "110001"}, "Address must be at least 5 characters long"),
    ("invalid_pincode", {"email": "valid@example.com", "password": "Password123", "name": "Valid Name", "address": "Address 123", "pincode": "1234"}, "Pincode must be a 6-digit number"),
    ("invalid_phone", {"email": "valid@example.com", "password": "Password123", "name": "Valid Name", "address": "Address 123", "pincode": "110001", "phone": "12345"}, "Phone must be a 10-digit number")
])
def test_signup_validation_failures(client, invalid_field, payload, expected_detail):
    response = client.post("/api/signup", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == expected_detail


def test_create_and_decode_access_token():
    user_id = 42
    token = create_access_token(user_id)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    decoded_id = get_current_user_id(credentials)
    assert decoded_id == user_id


def test_get_current_user_id_invalid_token():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.jwt.token")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired token"
