"""
Citizen Module Router Integration Tests (Excluding Facilities & Bills).

Endpoints Tested:
- GET /api/citizen/dash
- GET /api/citizen/profile
- PUT /api/citizen/edit_profile
- GET /api/citizen/complaints
- GET /api/citizen/complaint/{complaint_id}
- POST /api/citizen/search
"""

import pytest
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password, verify_password
from application.helpers.models import User, Role, Department, Complaint, ComplaintUpdate, UtilityBill, FacilityBooking
from application.middlewares.init_jwt import create_access_token


# ============================================================================
# LOCAL FIXTURES (CITIZEN DOMAIN SPECIFIC)
# ============================================================================

@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    """Ensures citizen, field_officer, commissioner roles exist in db_session."""
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def citizen_user(db_session: Session) -> User:
    """Creates a primary Citizen user in the test database."""
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.main@civicresolve.in",
        password=hash_password("CitizenSecret123!"),
        name="John Citizen",
        role="citizen",
        phone="9876543210",
        address="123 Civic Boulevard",
        pincode="110001",
        is_active=True
    )
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def citizen_headers(citizen_user: User) -> dict:
    """Returns JWT Authorization headers for citizen_user."""
    token = create_access_token(citizen_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_citizen_user(db_session: Session) -> User:
    """Creates a secondary Citizen user for duplicate email testing."""
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.second@civicresolve.in",
        password=hash_password("CitizenSecret123!"),
        name="Jane Citizen",
        role="citizen",
        phone="9876543211",
        address="456 Municipal Way",
        pincode="110002",
        is_active=True
    )
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def comm_headers(db_session: Session) -> dict:
    """Returns JWT Authorization headers for a commissioner user (for 403 role checks)."""
    role = db_session.query(Role).filter_by(name="commissioner").first()
    user = User(
        email="comm.citizentest@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Commissioner Role Test",
        role="commissioner",
        badge_id="COM-CIT-1",
        is_active=True
    )
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def officer_headers(db_session: Session) -> dict:
    """Returns JWT Authorization headers for a field officer (for 403 role checks)."""
    role = db_session.query(Role).filter_by(name="field_officer").first()
    officer = User(
        email="officer.citizentest@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Officer Role Test",
        role="field_officer",
        badge_id="OFF-CIT-1",
        is_active=True
    )
    if role:
        officer.roles.append(role)
    db_session.add(officer)
    db_session.commit()
    db_session.refresh(officer)
    token = create_access_token(officer.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_department(db_session: Session) -> Department:
    """Creates a sample Department entity."""
    dept = Department(name="Roads & Sanitation")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def sample_complaint(db_session: Session, sample_department: Department) -> Complaint:
    """Creates a sample Complaint entity linked to sample_department."""
    complaint = Complaint(
        token="CMP-CIT-99",
        title="Garbage Overflow near Park",
        description="Uncollected waste accumulating at park entrance",
        location="Green Park Gate 2",
        status="Submitted",
        severity="Normal",
        department_id=sample_department.id,
        department=sample_department.name
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint


# ============================================================================
# AUTHORIZATION CHECKS
# ============================================================================

def test_citizen_endpoints_unauthorized(client):
    """
    Verifies 401 Unauthorized for unauthenticated requests across citizen routes.
    """
    assert client.get("/api/citizen/dash").status_code == 401
    assert client.get("/api/citizen/profile").status_code == 401
    assert client.put("/api/citizen/edit_profile", json={}).status_code == 401
    assert client.get("/api/citizen/complaints").status_code == 401
    assert client.get("/api/citizen/complaint/1").status_code == 401
    assert client.post("/api/citizen/search", json={}).status_code == 401


def test_citizen_endpoints_forbidden_for_commissioner_and_officer(client, comm_headers, officer_headers):
    """
    Verifies 403 Forbidden for Commissioner or Field Officer calling citizen routes.
    """
    for headers in [comm_headers, officer_headers]:
        assert client.get("/api/citizen/dash", headers=headers).status_code == 403
        assert client.get("/api/citizen/profile", headers=headers).status_code == 403
        assert client.put("/api/citizen/edit_profile", json={}, headers=headers).status_code == 403
        assert client.get("/api/citizen/complaints", headers=headers).status_code == 403
        assert client.get("/api/citizen/complaint/1", headers=headers).status_code == 403
        assert client.post("/api/citizen/search", json={}, headers=headers).status_code == 403


# ============================================================================
# CITIZEN DASHBOARD TESTS (GET /api/citizen/dash)
# ============================================================================

def test_citizen_dashboard_success(client, citizen_headers, citizen_user):
    """
    Code Path: citizen_dashboard_resource.py -> GET /api/citizen/dash
    Verifies dashboard returns user_name, total_bills_due, upcoming_bookings_count, and lists.
    """
    response = client.get("/api/citizen/dash", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["user_name"] == citizen_user.name
    assert "total_bills_due" in data
    assert "upcoming_bookings_count" in data
    assert isinstance(data["pending_bills"], list)
    assert isinstance(data["upcoming_bookings"], list)


# ============================================================================
# CITIZEN PROFILE TESTS (GET & PUT /api/citizen/profile & edit_profile)
# ============================================================================

def test_citizen_profile_fetch_success(client, citizen_headers, citizen_user):
    """
    Code Path: citizen_profile_fetch_resource.py -> GET /api/citizen/profile
    Verifies fetching citizen profile payload schema.
    """
    response = client.get("/api/citizen/profile", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == citizen_user.id
    assert data["email"] == citizen_user.email
    assert data["name"] == citizen_user.name
    assert data["phone"] == citizen_user.phone
    assert data["address"] == citizen_user.address
    assert data["pincode"] == citizen_user.pincode


def test_citizen_profile_update_success(client, citizen_headers, citizen_user, db_session):
    """
    Code Path: citizen_profile_update_resource.py -> PUT /api/citizen/edit_profile
    Verifies updating citizen email, name, address, pincode, phone, and hashed password in DB.
    """
    payload = {
        "email": "john.updated@civicresolve.in",
        "name": "John Citizen Updated",
        "address": "999 Updated Boulevard",
        "pincode": "110005",
        "phone": "9998887775",
        "password": "NewSecretPass123!"
    }

    response = client.put("/api/citizen/edit_profile", json=payload, headers=citizen_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"

    db_session.refresh(citizen_user)
    assert citizen_user.email == "john.updated@civicresolve.in"
    assert citizen_user.name == "John Citizen Updated"
    assert citizen_user.address == "999 Updated Boulevard"
    assert citizen_user.pincode == "110005"
    assert citizen_user.phone == "9998887775"
    assert verify_password("NewSecretPass123!", citizen_user.password) is True


def test_citizen_profile_update_duplicate_email(client, citizen_headers, second_citizen_user):
    """
    Code Path: citizen_profile_update_resource.py -> duplicate email check.
    Verifies 409 Conflict when updating email to match an existing user's email.
    """
    payload = {"email": second_citizen_user.email}
    response = client.put("/api/citizen/edit_profile", json=payload, headers=citizen_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already in use"


def test_citizen_profile_update_validation_failures(client, citizen_headers):
    """
    Code Path: citizen_profile_update_resource.py -> validators.py field validations.
    Verifies 400 Bad Request responses for invalid fields.
    """
    # Invalid email
    resp1 = client.put("/api/citizen/edit_profile", json={"email": "bad-email"}, headers=citizen_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Invalid email format"

    # Short name
    resp2 = client.put("/api/citizen/edit_profile", json={"name": "A"}, headers=citizen_headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Name must be at least 2 characters long"

    # Short address
    resp3 = client.put("/api/citizen/edit_profile", json={"address": "123"}, headers=citizen_headers)
    assert resp3.status_code == 400
    assert resp3.json()["detail"] == "Address must be at least 5 characters long"

    # Invalid pincode
    resp4 = client.put("/api/citizen/edit_profile", json={"pincode": "1234"}, headers=citizen_headers)
    assert resp4.status_code == 400
    assert resp4.json()["detail"] == "Pincode must be a 6-digit number"

    # Invalid phone
    resp5 = client.put("/api/citizen/edit_profile", json={"phone": "12345"}, headers=citizen_headers)
    assert resp5.status_code == 400
    assert resp5.json()["detail"] == "Phone must be a 10-digit number"

    # Short password
    resp6 = client.put("/api/citizen/edit_profile", json={"password": "123"}, headers=citizen_headers)
    assert resp6.status_code == 400
    assert resp6.json()["detail"] == "Password must be at least 5 characters long"


# ============================================================================
# CITIZEN COMPLAINT LIST & DETAIL TESTS
# ============================================================================

def test_citizen_complaints_list_success(client, citizen_headers):
    """
    Code Path: citizen_complaints_list_resource.py -> GET /api/citizen/complaints
    Verifies fetching citizen's personal complaints list.
    """
    response = client.get("/api/citizen/complaints", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "complaints" in data
    assert isinstance(data["complaints"], list)


def test_citizen_complaint_detail_success(client, citizen_headers, sample_complaint, db_session):
    """
    Code Path: citizen_complaint_detail_resource.py -> GET /api/citizen/complaint/{id}
    Verifies complaint detail view and updates audit trail array.
    """
    update = ComplaintUpdate(
        complaint_id=sample_complaint.id,
        old_status="Submitted",
        new_status="Assigned",
        note="Assigned to field officer"
    )
    db_session.add(update)
    db_session.commit()

    response = client.get(f"/api/citizen/complaint/{sample_complaint.id}", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "complaint" in data
    assert "updates" in data
    assert data["complaint"]["id"] == sample_complaint.id
    assert data["complaint"]["token"] == sample_complaint.token
    assert len(data["updates"]) >= 1


def test_citizen_complaint_detail_not_found(client, citizen_headers):
    """
    Code Path: citizen_complaint_detail_resource.py -> complaint not found.
    Verifies 404 Not Found for non-existent complaint ID.
    """
    response = client.get("/api/citizen/complaint/99999", headers=citizen_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


# ============================================================================
# CITIZEN SEARCH TESTS (POST /api/citizen/search)
# ============================================================================

def test_citizen_search_success(client, citizen_headers, db_session):
    """
    Code Path: citizen_search_resource.py -> POST /api/citizen/search
    Verifies searching active facilities by name, address, facility_type, or pincode.
    """
    from application.helpers.models import Facility
    facility = Facility(
        name="Citizen Park Community Hall",
        facility_type="Community Hall",
        address="10 Park Road",
        pincode="110001",
        price_per_day=300.0,
        is_active=True
    )
    db_session.add(facility)
    db_session.commit()

    response = client.post("/api/citizen/search", json={"query": "Community Hall"}, headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "facilities" in data
    assert any(f["id"] == facility.id for f in data["facilities"])


def test_citizen_search_empty_query(client, citizen_headers):
    """
    Code Path: citizen_search_resource.py -> empty query returns empty list.
    """
    response = client.post("/api/citizen/search", json={"query": ""}, headers=citizen_headers)
    assert response.status_code == 200
    assert response.json() == {"facilities": []}
