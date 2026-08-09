"""
Commissioner Officer Management Router Integration Tests.

Endpoints Tested:
- GET /api/commissioner/officers
- POST /api/commissioner/officer
- PUT /api/commissioner/officer/{officer_id}
- DELETE /api/commissioner/officer/{officer_id}
- PUT /api/commissioner/assign/{complaint_id}
"""

import pytest
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role, Department, Complaint, ComplaintUpdate
from application.middlewares.init_jwt import create_access_token


# ============================================================================
# LOCAL FIXTURES (COMMISSIONER OFFICER MANAGEMENT SPECIFIC)
# ============================================================================

@pytest.fixture(autouse=True)
def seed_officer_roles(db_session: Session):
    """Ensures standard roles (field_officer, commissioner, citizen) exist in db_session."""
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def comm_user(db_session: Session) -> User:
    """Creates a Commissioner user in the test database."""
    role = db_session.query(Role).filter_by(name="commissioner").first()
    user = User(
        email="comm.officertest@civicresolve.in",
        password=hash_password("CommPass123!"),
        name="Comm Officer Tester",
        role="commissioner",
        badge_id="COM-777",
        is_active=True
    )
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def comm_headers(comm_user: User) -> dict:
    """Returns JWT Authorization headers for the commissioner user."""
    token = create_access_token(comm_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def citizen_headers(db_session: Session) -> dict:
    """Returns JWT Authorization headers for a citizen user (for 403 authorization checks)."""
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.commtest@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Citizen Auth Test",
        role="citizen",
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
def test_department(db_session: Session) -> Department:
    """Creates a sample Department entity in the test database."""
    dept = Department(name="Health & Sanitation")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def second_department(db_session: Session) -> Department:
    """Creates a second Department entity for update testing."""
    dept = Department(name="Roads & Infrastructure")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def existing_officer(db_session: Session, test_department: Department) -> User:
    """Creates an existing Field Officer linked to test_department."""
    role = db_session.query(Role).filter_by(name="field_officer").first()
    officer = User(
        email="existing.officer@civicresolve.in",
        password=hash_password("OfficerPass123!"),
        name="Officer Bob",
        role="field_officer",
        badge_id="OFF-101",
        department_id=test_department.id,
        department=test_department.name,
        phone="9876543210",
        address="Zone 1 HQ",
        is_active=True
    )
    if role:
        officer.roles.append(role)
    db_session.add(officer)
    db_session.commit()
    db_session.refresh(officer)
    return officer


@pytest.fixture
def sample_complaint(db_session: Session, test_department: Department) -> Complaint:
    """Creates a Submitted Complaint in the test database."""
    complaint = Complaint(
        token="CMP-9901",
        title="Broken Streetlight",
        description="Streetlight flickering on 5th Ave",
        location="5th Ave Corner",
        status="Submitted",
        severity="Normal",
        department_id=test_department.id,
        department=test_department.name
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint


# ============================================================================
# AUTHORIZATION TESTS
# ============================================================================

def test_officer_endpoints_unauthorized(client):
    """
    Verifies that unauthenticated requests (no JWT token) return 401 Unauthorized across officer endpoints.
    """
    assert client.get("/api/commissioner/officers").status_code == 401
    assert client.post("/api/commissioner/officer", json={}).status_code == 401
    assert client.put("/api/commissioner/officer/1", json={}).status_code == 401
    assert client.delete("/api/commissioner/officer/1").status_code == 401
    assert client.put("/api/commissioner/assign/1", json={}).status_code == 401


def test_officer_endpoints_forbidden_for_citizen(client, citizen_headers):
    """
    Verifies that requests by non-commissioner users (e.g. Citizen) return 403 Forbidden.
    """
    assert client.get("/api/commissioner/officers", headers=citizen_headers).status_code == 403
    assert client.post("/api/commissioner/officer", json={}, headers=citizen_headers).status_code == 403
    assert client.put("/api/commissioner/officer/1", json={}, headers=citizen_headers).status_code == 403
    assert client.delete("/api/commissioner/officer/1", headers=citizen_headers).status_code == 403
    assert client.put("/api/commissioner/assign/1", json={}, headers=citizen_headers).status_code == 403


# ============================================================================
# LIST OFFICERS TESTS (GET /api/commissioner/officers)
# ============================================================================

def test_list_officers_success(client, comm_headers, existing_officer):
    """
    Code Path: commissioner_officers_list_resource.py -> GET /api/commissioner/officers
    Verifies fetching list of officers with complete schema validation.
    """
    response = client.get("/api/commissioner/officers", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "officers" in data
    assert len(data["officers"]) >= 1

    matched = next((o for o in data["officers"] if o["id"] == existing_officer.id), None)
    assert matched is not None
    assert matched["email"] == "existing.officer@civicresolve.in"
    assert matched["name"] == "Officer Bob"
    assert matched["badgeId"] == "OFF-101"
    assert matched["department"] == existing_officer.department
    assert matched["active"] is True


# ============================================================================
# CREATE OFFICER TESTS (POST /api/commissioner/officer)
# ============================================================================

def test_create_officer_by_department_id(client, comm_headers, test_department, db_session):
    """
    Code Path: commissioner_officer_add_resource.py -> POST /api/commissioner/officer (dept numeric ID)
    Verifies creating officer by department_id and confirms BOTH department_id and department string are populated in DB.
    """
    payload = {
        "email": "new.officer1@civicresolve.in",
        "name": "Officer Alice",
        "badgeId": "OFF-201",
        "department_id": test_department.id,
        "phone": "9876543201"
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Officer Officer Alice created successfully"

    # Database Verification: both department_id and department string must be populated
    officer_db = db_session.query(User).filter_by(email="new.officer1@civicresolve.in").first()
    assert officer_db is not None
    assert officer_db.department_id == test_department.id
    assert officer_db.department == test_department.name
    assert officer_db.role == "field_officer"
    assert officer_db.badge_id == "OFF-201"


def test_create_officer_by_department_name(client, comm_headers, test_department, db_session):
    """
    Code Path: commissioner_officer_add_resource.py -> POST /api/commissioner/officer (dept name string)
    Verifies creating officer by department name resolution.
    """
    payload = {
        "email": "new.officer2@civicresolve.in",
        "name": "Officer Charlie",
        "badgeId": "OFF-202",
        "department": test_department.name,
        "phone": "9876543202"
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 200

    officer_db = db_session.query(User).filter_by(email="new.officer2@civicresolve.in").first()
    assert officer_db is not None
    assert officer_db.department_id == test_department.id
    assert officer_db.department == test_department.name


def test_create_officer_invalid_department(client, comm_headers):
    """
    Code Path: commissioner_officer_add_resource.py -> non-existent department lookup fails.
    Verifies 400 Bad Request rejection for invalid department.
    """
    payload = {
        "email": "invalid.dept@civicresolve.in",
        "name": "Officer Unknown",
        "department": "NonExistentDept999"
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid department"


def test_create_officer_missing_department(client, comm_headers):
    """
    Code Path: commissioner_officer_add_resource.py -> department missing/empty.
    Verifies 400 Bad Request when department is omitted.
    """
    payload = {
        "email": "nodept@civicresolve.in",
        "name": "Officer NoDept"
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Department is required"


def test_create_officer_duplicate_email(client, comm_headers, existing_officer):
    """
    Code Path: commissioner_officer_add_resource.py -> duplicate email check.
    Verifies 409 Conflict when attempting to use an existing email.
    """
    payload = {
        "email": existing_officer.email,
        "name": "Duplicate Email Officer",
        "department": existing_officer.department
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_create_officer_duplicate_badge_id(client, comm_headers, existing_officer, test_department):
    """
    Code Path: commissioner_officer_add_resource.py -> duplicate badge_id check.
    Verifies 409 Conflict when attempting to use an existing badge_id.
    """
    payload = {
        "email": "unique.email@civicresolve.in",
        "name": "Duplicate Badge Officer",
        "badgeId": existing_officer.badge_id,
        "department_id": test_department.id
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Badge ID already in use"


def test_create_officer_invalid_name_or_email(client, comm_headers, test_department):
    """
    Code Path: commissioner_officer_add_resource.py -> validate_email & validate_name checks.
    Verifies 400 Bad Request for malformed email or name.
    """
    # Invalid email
    resp1 = client.post("/api/commissioner/officer", json={
        "email": "bad-email",
        "name": "Valid Name",
        "department_id": test_department.id
    }, headers=comm_headers)
    assert resp1.status_code == 400

    # Short name
    resp2 = client.post("/api/commissioner/officer", json={
        "email": "valid.email@civicresolve.in",
        "name": "A",
        "department_id": test_department.id
    }, headers=comm_headers)
    assert resp2.status_code == 400


# ============================================================================
# UPDATE OFFICER TESTS (PUT /api/commissioner/officer/{officer_id})
# ============================================================================

def test_update_officer_success(client, comm_headers, existing_officer, db_session):
    """
    Code Path: commissioner_officer_update_resource.py -> PUT /api/commissioner/officer/{id}
    Verifies updating officer attributes (name, phone, badgeId, active status).
    """
    payload = {
        "name": "Officer Bob Updated",
        "phone": "9998887776",
        "badgeId": "OFF-101-UPD",
        "active": True
    }

    response = client.put(f"/api/commissioner/officer/{existing_officer.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Officer updated successfully"

    # Database Verification
    db_session.refresh(existing_officer)
    assert existing_officer.name == "Officer Bob Updated"
    assert existing_officer.phone == "9998887776"
    assert existing_officer.badge_id == "OFF-101-UPD"


def test_update_officer_department(client, comm_headers, existing_officer, second_department, db_session):
    """
    Code Path: commissioner_officer_update_resource.py -> update department.
    Verifies changing officer department and confirms BOTH department_id and department string update.
    """
    payload = {
        "department_id": second_department.id
    }

    response = client.put(f"/api/commissioner/officer/{existing_officer.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200

    db_session.refresh(existing_officer)
    assert existing_officer.department_id == second_department.id
    assert existing_officer.department == second_department.name


def test_update_officer_invalid_department(client, comm_headers, existing_officer):
    """
    Code Path: commissioner_officer_update_resource.py -> invalid department.
    Verifies 400 Bad Request when updating to an invalid department.
    """
    payload = {
        "department": "FakeDepartment99"
    }

    response = client.put(f"/api/commissioner/officer/{existing_officer.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid department"


def test_update_non_existent_officer(client, comm_headers):
    """
    Code Path: commissioner_officer_update_resource.py -> officer not found.
    Verifies 404 Not Found for non-existent officer ID.
    """
    response = client.put("/api/commissioner/officer/99999", json={"name": "Ghost"}, headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Officer not found"


# ============================================================================
# DELETE / DEACTIVATE OFFICER TESTS (DELETE /api/commissioner/officer/{officer_id})
# ============================================================================

def test_delete_officer_soft_delete(client, comm_headers, existing_officer, db_session):
    """
    Code Path: commissioner_officer_delete_resource.py -> DELETE /api/commissioner/officer/{id}
    Verifies soft deactivation of officer (is_active = False).
    """
    response = client.delete(f"/api/commissioner/officer/{existing_officer.id}", headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Officer deactivated successfully"

    db_session.refresh(existing_officer)
    assert existing_officer.is_active is False


def test_delete_non_existent_officer(client, comm_headers):
    """
    Code Path: commissioner_officer_delete_resource.py -> officer not found.
    Verifies 404 Not Found when deleting non-existent officer ID.
    """
    response = client.delete("/api/commissioner/officer/99999", headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Officer not found"


# ============================================================================
# ASSIGN OFFICER TESTS (PUT /api/commissioner/assign/{complaint_id})
# ============================================================================

def test_assign_officer_success(client, comm_headers, sample_complaint, existing_officer, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> PUT /api/commissioner/assign/{complaint_id}
    Verifies assigning an active officer to a severe complaint, status transition, and audit trail creation.
    """
    sample_complaint.severity = "Critical"
    db_session.commit()

    payload = {
        "officer_id": existing_officer.id,
        "severity": "Critical"
    }

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == f"Complaint assigned to {existing_officer.name}"

    # Database Verification
    db_session.refresh(sample_complaint)
    assert sample_complaint.assigned_officer_id == existing_officer.id
    assert sample_complaint.assigned_officer_name == existing_officer.name
    assert sample_complaint.status == "Assigned"
    assert sample_complaint.severity == "Critical"

    # Verify ComplaintUpdate audit trail created
    audit = db_session.query(ComplaintUpdate).filter_by(complaint_id=sample_complaint.id).first()
    assert audit is not None
    assert audit.old_status == "Submitted"
    assert audit.new_status == "Assigned"


def test_assign_officer_non_severe_complaint_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> severe complaint check.
    Verifies 400 Bad Request when attempting to assign an officer to a Normal severity complaint.
    """
    sample_complaint.severity = "Normal"
    db_session.commit()

    payload = {"officer_id": existing_officer.id}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    # Ensure complaint severity and assignment were not modified
    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "Normal"
    assert sample_complaint.assigned_officer_id is None


def test_assign_officer_low_severity_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> severe complaint check.
    Verifies 400 Bad Request when attempting to assign an officer to a Low severity complaint.
    """
    sample_complaint.severity = "Low"
    db_session.commit()

    payload = {"officer_id": existing_officer.id}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "Low"
    assert sample_complaint.assigned_officer_id is None


def test_assign_officer_high_severity_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> severe complaint check.
    Verifies 400 Bad Request when attempting to assign an officer to a High severity complaint.
    """
    sample_complaint.severity = "High"
    db_session.commit()

    payload = {"officer_id": existing_officer.id}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "High"
    assert sample_complaint.assigned_officer_id is None


def test_assign_officer_bypass_attempt_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> severe complaint check.
    Verifies 400 Bad Request when non-Critical complaint supplies {"severity": "Critical"} in request body.
    Confirming that a non-Critical complaint cannot bypass the severity restriction.
    """
    sample_complaint.severity = "Normal"
    db_session.commit()

    payload = {
        "officer_id": existing_officer.id,
        "severity": "Critical"
    }

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "Normal"
    assert sample_complaint.assigned_officer_id is None


def test_assign_deactivated_officer_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> deactivated officer check.
    Verifies 400 Bad Request when assigning a deactivated officer.
    """
    sample_complaint.severity = "Critical"
    existing_officer.is_active = False
    db_session.commit()

    payload = {
        "officer_id": existing_officer.id
    }

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer account is deactivated"


def test_assign_invalid_officer_fails(client, comm_headers, sample_complaint, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> invalid officer check.
    Verifies 400 Bad Request when assigning a non-existent officer ID.
    """
    sample_complaint.severity = "Critical"
    db_session.commit()

    payload = {"officer_id": 99999}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid officer"


def test_assign_non_existent_complaint(client, comm_headers, existing_officer):
    """
    Code Path: commissioner_assign_officer_resource.py -> complaint not found.
    Verifies 404 Not Found when assigning to a non-existent complaint ID.
    """
    payload = {"officer_id": existing_officer.id}
    response = client.put("/api/commissioner/assign/99999", json=payload, headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


def test_assign_missing_officer_id(client, comm_headers, sample_complaint, db_session):
    """
    Code Path: commissioner_assign_officer_resource.py -> missing officer_id.
    Verifies 400 Bad Request when officer_id is omitted.
    """
    sample_complaint.severity = "Critical"
    db_session.commit()

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json={}, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer ID is required"


