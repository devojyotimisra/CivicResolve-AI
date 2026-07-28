"""
Field Officer Module Router Integration Tests.

Endpoints Tested:
- GET /api/officer/dash
- GET /api/officer/history
- GET /api/officer/profile
- PUT /api/officer/edit_profile
- POST /api/officer/search
- GET /api/officer/ticket/{complaint_id}
- PUT /api/officer/ticket/{complaint_id}/status
- POST /api/officer/ticket/{complaint_id}/resolve
"""

import pytest
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password, verify_password
from application.helpers.models import User, Role, Department, Complaint, ComplaintUpdate
from application.middlewares.init_jwt import create_access_token


# ============================================================================
# LOCAL FIXTURES (OFFICER MODULE SPECIFIC)
# ============================================================================

@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    """Ensures citizen, field_officer, commissioner roles exist in db_session."""
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def test_dept(db_session: Session) -> Department:
    """Creates a sample Department."""
    dept = Department(name="Public Works")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def officer_user(db_session: Session, test_dept: Department) -> User:
    """Creates a primary Field Officer user."""
    role = db_session.query(Role).filter_by(name="field_officer").first()
    officer = User(
        email="officer.primary@civicresolve.in",
        password=hash_password("OfficerPass123!"),
        name="Officer Primary",
        role="field_officer",
        badge_id="OFF-888",
        department_id=test_dept.id,
        department=test_dept.name,
        phone="9876543210",
        address="Zone 2 HQ",
        pincode="110001",
        is_active=True
    )
    if role:
        officer.roles.append(role)
    db_session.add(officer)
    db_session.commit()
    db_session.refresh(officer)
    return officer


@pytest.fixture
def officer_headers(officer_user: User) -> dict:
    """Returns JWT Authorization headers for officer_user."""
    token = create_access_token(officer_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_officer(db_session: Session, test_dept: Department) -> User:
    """Creates a secondary Field Officer user for cross-assignment authorization tests."""
    role = db_session.query(Role).filter_by(name="field_officer").first()
    officer = User(
        email="officer.secondary@civicresolve.in",
        password=hash_password("OfficerPass123!"),
        name="Officer Secondary",
        role="field_officer",
        badge_id="OFF-889",
        department_id=test_dept.id,
        department=test_dept.name,
        phone="9876543211",
        address="Zone 2 HQ",
        pincode="110001",
        is_active=True
    )
    if role:
        officer.roles.append(role)
    db_session.add(officer)
    db_session.commit()
    db_session.refresh(officer)
    return officer


@pytest.fixture
def second_officer_headers(second_officer: User) -> dict:
    """Returns JWT Authorization headers for second_officer."""
    token = create_access_token(second_officer.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def citizen_headers(db_session: Session) -> dict:
    """Returns JWT Authorization headers for a citizen user (for 403 authorization checks)."""
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.officertest@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Citizen Test User",
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
def assigned_complaint(db_session: Session, officer_user: User, test_dept: Department) -> Complaint:
    """Creates a Complaint assigned to officer_user with status 'Assigned'."""
    complaint = Complaint(
        token="CMP-1001",
        title="Pothole on Main Street",
        description="Large pothole near central park entrance causing traffic issues",
        location="Main Street & Park Ave",
        status="Assigned",
        severity="Normal",
        department_id=test_dept.id,
        department=test_dept.name,
        assigned_officer_id=officer_user.id,
        assigned_officer_name=officer_user.name
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint


@pytest.fixture
def in_progress_complaint(db_session: Session, officer_user: User, test_dept: Department) -> Complaint:
    """Creates a Complaint assigned to officer_user with status 'In Progress'."""
    complaint = Complaint(
        token="CMP-1002",
        title="Water Pipe Leakage",
        description="High pressure water leak on 4th cross road",
        location="4th Cross Road",
        status="In Progress",
        severity="High",
        department_id=test_dept.id,
        department=test_dept.name,
        assigned_officer_id=officer_user.id,
        assigned_officer_name=officer_user.name
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint


@pytest.fixture
def resolved_complaint(db_session: Session, officer_user: User, test_dept: Department) -> Complaint:
    """Creates a Complaint assigned to officer_user with status 'Resolved'."""
    complaint = Complaint(
        token="CMP-1003",
        title="Streetlight Fixed",
        description="Broken lamp replaced with LED light",
        location="7th Sector",
        status="Resolved",
        severity="Low",
        department_id=test_dept.id,
        department=test_dept.name,
        assigned_officer_id=officer_user.id,
        assigned_officer_name=officer_user.name
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint


# ============================================================================
# AUTHORIZATION & ROLE CHECKS
# ============================================================================

def test_officer_endpoints_unauthorized(client):
    """
    Verifies 401 Unauthorized for unauthenticated requests across all officer routes.
    """
    assert client.get("/api/officer/dash").status_code == 401
    assert client.get("/api/officer/history").status_code == 401
    assert client.get("/api/officer/profile").status_code == 401
    assert client.put("/api/officer/edit_profile", json={}).status_code == 401
    assert client.post("/api/officer/search", json={}).status_code == 401
    assert client.get("/api/officer/ticket/1").status_code == 401
    assert client.put("/api/officer/ticket/1/status", json={}).status_code == 401
    assert client.post("/api/officer/ticket/1/resolve", json={}).status_code == 401


def test_officer_endpoints_forbidden_for_citizen(client, citizen_headers):
    """
    Verifies 403 Forbidden for authenticated non-officer (e.g. Citizen) user.
    """
    assert client.get("/api/officer/dash", headers=citizen_headers).status_code == 403
    assert client.get("/api/officer/history", headers=citizen_headers).status_code == 403
    assert client.get("/api/officer/profile", headers=citizen_headers).status_code == 403
    assert client.put("/api/officer/edit_profile", json={}, headers=citizen_headers).status_code == 403
    assert client.post("/api/officer/search", json={}, headers=citizen_headers).status_code == 403
    assert client.get("/api/officer/ticket/1", headers=citizen_headers).status_code == 403
    assert client.put("/api/officer/ticket/1/status", json={}, headers=citizen_headers).status_code == 403
    assert client.post("/api/officer/ticket/1/resolve", json={}, headers=citizen_headers).status_code == 403


# ============================================================================
# OFFICER DASHBOARD & HISTORY TESTS
# ============================================================================

def test_officer_dashboard_success(client, officer_headers, assigned_complaint, resolved_complaint):
    """
    Code Path: officer_dashboard_resource.py -> GET /api/officer/dash
    Verifies dashboard statistics and active ticket listing (excludes resolved/closed tickets).
    """
    response = client.get("/api/officer/dash", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["officer_name"] == "Officer Primary"
    assert data["department"] == "Public Works"
    assert "assigned_tickets" in data
    assert data["total_assigned"] >= 1

    ticket_ids = [t["id"] for t in data["assigned_tickets"]]
    assert assigned_complaint.id in ticket_ids
    assert resolved_complaint.id not in ticket_ids  # Resolved tickets excluded from dash


def test_officer_history_success(client, officer_headers, assigned_complaint, resolved_complaint):
    """
    Code Path: officer_history_resource.py -> GET /api/officer/history
    Verifies fetching history returns ALL assigned complaints (both active and resolved).
    """
    response = client.get("/api/officer/history", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert "history" in data
    history_ids = [h["id"] for h in data["history"]]
    assert assigned_complaint.id in history_ids
    assert resolved_complaint.id in history_ids  # Includes resolved tickets


# ============================================================================
# OFFICER PROFILE TESTS
# ============================================================================

def test_officer_profile_fetch_success(client, officer_headers, officer_user):
    """
    Code Path: officer_profile_fetch_resource.py -> GET /api/officer/profile
    Verifies officer profile payload schema.
    """
    response = client.get("/api/officer/profile", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == officer_user.id
    assert data["email"] == officer_user.email
    assert data["name"] == officer_user.name
    assert data["department"] == officer_user.department


def test_officer_profile_update_success(client, officer_headers, officer_user, db_session):
    """
    Code Path: officer_profile_update_resource.py -> PUT /api/officer/edit_profile
    Verifies updating officer name, phone, and password with DB persistence and password hashing.
    """
    payload = {
        "name": "Officer Primary Renamed",
        "phone": "9998887771",
        "password": "NewSecretPassword123"
    }

    response = client.put("/api/officer/edit_profile", json=payload, headers=officer_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"

    # DB Verification
    db_session.refresh(officer_user)
    assert officer_user.name == "Officer Primary Renamed"
    assert officer_user.phone == "9998887771"
    assert verify_password("NewSecretPassword123", officer_user.password) is True


def test_officer_profile_update_validation_failures(client, officer_headers):
    """
    Code Path: officer_profile_update_resource.py -> field validators.
    Verifies 400 Bad Request for invalid phone or short password.
    """
    # Invalid phone format
    resp1 = client.put("/api/officer/edit_profile", json={"phone": "12345"}, headers=officer_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Phone must be a 10-digit number"

    # Password too short (< 5 chars)
    resp2 = client.put("/api/officer/edit_profile", json={"password": "123"}, headers=officer_headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Password must be at least 5 characters long"


# ============================================================================
# OFFICER SEARCH TESTS
# ============================================================================

def test_officer_search_success(client, officer_headers, assigned_complaint):
    """
    Code Path: officer_search_resource.py -> POST /api/officer/search
    Verifies searching assigned tickets by title, token, description, or location.
    """
    response = client.post("/api/officer/search", json={"query": "Pothole"}, headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert "tickets" in data
    assert len(data["tickets"]) >= 1
    assert data["tickets"][0]["id"] == assigned_complaint.id


def test_officer_search_empty_query(client, officer_headers):
    """
    Code Path: officer_search_resource.py -> empty query string returns empty list.
    """
    response = client.post("/api/officer/search", json={"query": ""}, headers=officer_headers)
    assert response.status_code == 200
    assert response.json() == {"tickets": []}


# ============================================================================
# TICKET DETAIL TESTS (GET /api/officer/ticket/{complaint_id})
# ============================================================================

def test_officer_ticket_detail_success(client, officer_headers, assigned_complaint):
    """
    Code Path: officer_ticket_detail_resource.py -> GET /api/officer/ticket/{id}
    Verifies ticket details and update history payload schema.
    """
    response = client.get(f"/api/officer/ticket/{assigned_complaint.id}", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert "complaint" in data
    assert "updates" in data
    assert data["complaint"]["id"] == assigned_complaint.id
    assert data["complaint"]["token"] == assigned_complaint.token
    assert data["complaint"]["status"] == "Assigned"


def test_officer_ticket_detail_forbidden_for_other_officer(client, second_officer_headers, assigned_complaint):
    """
    Code Path: officer_ticket_detail_resource.py -> assigned officer check.
    Verifies 403 Forbidden when an officer accesses a ticket assigned to a different officer.
    """
    response = client.get(f"/api/officer/ticket/{assigned_complaint.id}", headers=second_officer_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "This ticket is not assigned to you"


def test_officer_ticket_detail_not_found(client, officer_headers):
    """
    Code Path: officer_ticket_detail_resource.py -> ticket not found.
    Verifies 404 Not Found for non-existent ticket ID.
    """
    response = client.get("/api/officer/ticket/99999", headers=officer_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


# ============================================================================
# TICKET STATUS UPDATE TESTS (PUT /api/officer/ticket/{complaint_id}/status)
# ============================================================================

def test_officer_ticket_status_update_valid_transitions(client, officer_headers, assigned_complaint, db_session):
    """
    Code Path: officer_ticket_update_status_resource.py -> PUT /api/officer/ticket/{id}/status
    Verifies valid state transitions ('Assigned' -> 'En Route' -> 'On Site' -> 'In Progress'),
    DB status updates, and ComplaintUpdate audit log entries.
    """
    # 1. Assigned -> En Route
    resp1 = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "En Route"}, headers=officer_headers)
    assert resp1.status_code == 200
    assert resp1.json()["message"] == "Status updated to En Route"

    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "En Route"

    # 2. En Route -> On Site
    resp2 = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "On Site"}, headers=officer_headers)
    assert resp2.status_code == 200

    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "On Site"

    # 3. On Site -> In Progress
    resp3 = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "In Progress"}, headers=officer_headers)
    assert resp3.status_code == 200

    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "In Progress"

    # Verify audit logs created
    updates = db_session.query(ComplaintUpdate).filter_by(complaint_id=assigned_complaint.id).all()
    assert len(updates) == 3


def test_officer_ticket_status_update_invalid_transition(client, officer_headers, assigned_complaint):
    """
    Code Path: officer_ticket_update_status_resource.py -> VALID_TRANSITIONS state machine failure.
    Verifies 400 Bad Request when attempting an illegal transition (e.g. Assigned -> Resolved).
    """
    response = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "Resolved"}, headers=officer_headers)
    assert response.status_code == 400
    assert "Cannot transition from 'Assigned' to 'Resolved'" in response.json()["detail"]


def test_officer_ticket_status_update_assigned_to_in_progress_rejected(client, officer_headers, assigned_complaint, db_session):
    """
    Code Path: officer_ticket_update_status_resource.py -> VALID_TRANSITIONS state machine failure.
    Verifies 400 Bad Request when attempting direct transition from 'Assigned' to 'In Progress',
    and verifies that complaint status remains 'Assigned' in the database.
    """
    response = client.put(
        f"/api/officer/ticket/{assigned_complaint.id}/status",
        json={"status": "In Progress"},
        headers=officer_headers
    )
    assert response.status_code == 400
    assert "Cannot transition from 'Assigned' to 'In Progress'" in response.json()["detail"]

    # Verify DB status remains unchanged
    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "Assigned"


def test_officer_ticket_status_update_missing_status(client, officer_headers, assigned_complaint):
    """
    Code Path: officer_ticket_update_status_resource.py -> missing status key.
    Verifies 400 Bad Request when status is omitted.
    """
    response = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={}, headers=officer_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "New status is required"


def test_officer_ticket_status_update_not_found(client, officer_headers):
    """
    Code Path: officer_ticket_update_status_resource.py -> ticket not found.
    Verifies 404 Not Found for non-existent ticket ID.
    """
    response = client.put("/api/officer/ticket/99999/status", json={"status": "En Route"}, headers=officer_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


# ============================================================================
# TICKET RESOLVE TESTS (POST /api/officer/ticket/{complaint_id}/resolve)
# ============================================================================

def test_officer_ticket_resolve_success(client, officer_headers, in_progress_complaint, db_session):
    """
    Code Path: officer_ticket_resolve_resource.py -> POST /api/officer/ticket/{id}/resolve
    Verifies ticket resolution when ticket is 'In Progress', setting status to 'Resolved',
    resolved_at timestamp, resolution note/photo, and ComplaintUpdate audit entry.
    """
    payload = {
        "resolution_note": "Pipe repaired and pressure tested successfully.",
        "resolution_photo_url": "/uploads/resolutions/pipe_fixed.jpg"
    }

    response = client.post(f"/api/officer/ticket/{in_progress_complaint.id}/resolve", json=payload, headers=officer_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Ticket resolved successfully"

    # DB Verification
    db_session.refresh(in_progress_complaint)
    assert in_progress_complaint.status == "Resolved"
    assert in_progress_complaint.resolution_note == "Pipe repaired and pressure tested successfully."
    assert in_progress_complaint.resolution_photo == "/uploads/resolutions/pipe_fixed.jpg"
    assert in_progress_complaint.resolved_at is not None

    # Verify audit entry created
    audit = db_session.query(ComplaintUpdate).filter_by(complaint_id=in_progress_complaint.id, new_status="Resolved").first()
    assert audit is not None


def test_officer_ticket_resolve_invalid_initial_status(client, officer_headers, assigned_complaint):
    """
    Code Path: officer_ticket_resolve_resource.py -> status check failure.
    Verifies 400 Bad Request when attempting to resolve a ticket with status 'Assigned'.
    """
    payload = {"resolution_note": "Premature resolution attempt"}
    response = client.post(f"/api/officer/ticket/{assigned_complaint.id}/resolve", json=payload, headers=officer_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Ticket must be in progress or on site to resolve"


def test_officer_ticket_resolve_not_found(client, officer_headers):
    """
    Code Path: officer_ticket_resolve_resource.py -> ticket not found.
    Verifies 404 Not Found for non-existent ticket ID.
    """
    response = client.post("/api/officer/ticket/99999/resolve", json={}, headers=officer_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"
