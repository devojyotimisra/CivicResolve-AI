import pytest
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password, verify_password
from application.helpers.models import User, Role, Department, Complaint, ComplaintUpdate
from application.middlewares.init_jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def test_dept(db_session: Session) -> Department:
    dept = Department(name="Public Works")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def officer_user(db_session: Session, test_dept: Department) -> User:
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
    token = create_access_token(officer_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_officer(db_session: Session, test_dept: Department) -> User:
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
    token = create_access_token(second_officer.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def citizen_headers(db_session: Session) -> dict:
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


def test_officer_endpoints_unauthorized(client):
    assert client.get("/api/officer/dash").status_code == 401
    assert client.get("/api/officer/history").status_code == 401
    assert client.get("/api/officer/profile").status_code == 401
    assert client.put("/api/officer/edit_profile", json={}).status_code == 401
    assert client.post("/api/officer/search", json={}).status_code == 401
    assert client.get("/api/officer/ticket/1").status_code == 401
    assert client.put("/api/officer/ticket/1/status", json={}).status_code == 401
    assert client.post("/api/officer/ticket/1/resolve", json={}).status_code == 401


def test_officer_endpoints_forbidden_for_citizen(client, citizen_headers):
    assert client.get("/api/officer/dash", headers=citizen_headers).status_code == 403
    assert client.get("/api/officer/history", headers=citizen_headers).status_code == 403
    assert client.get("/api/officer/profile", headers=citizen_headers).status_code == 403
    assert client.put("/api/officer/edit_profile", json={}, headers=citizen_headers).status_code == 403
    assert client.post("/api/officer/search", json={}, headers=citizen_headers).status_code == 403
    assert client.get("/api/officer/ticket/1", headers=citizen_headers).status_code == 403
    assert client.put("/api/officer/ticket/1/status", json={}, headers=citizen_headers).status_code == 403
    assert client.post("/api/officer/ticket/1/resolve", json={}, headers=citizen_headers).status_code == 403


def test_officer_dashboard_success(client, officer_headers, assigned_complaint, resolved_complaint):
    response = client.get("/api/officer/dash", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["officerName"] == "Officer Primary"
    assert data["department"] == "Public Works"
    assert "assignedTickets" in data
    assert data["totalAssigned"] >= 1

    ticket_ids = [t["id"] for t in data["assignedTickets"]]
    assert assigned_complaint.id in ticket_ids
    assert resolved_complaint.id not in ticket_ids


def test_officer_history_success(client, officer_headers, assigned_complaint, resolved_complaint):
    response = client.get("/api/officer/history", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert "history" in data
    history_ids = [h["id"] for h in data["history"]]
    assert assigned_complaint.id in history_ids
    assert resolved_complaint.id in history_ids


def test_officer_profile_fetch_success(client, officer_headers, officer_user):
    response = client.get("/api/officer/profile", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == officer_user.id
    assert data["email"] == officer_user.email
    assert data["name"] == officer_user.name
    assert data["department"] == officer_user.department


def test_officer_profile_update_success(client, officer_headers, officer_user, db_session):
    payload = {
        "name": "Officer Primary Renamed",
        "phone": "9998887771"
    }

    response = client.put("/api/officer/edit_profile", json=payload, headers=officer_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"

    db_session.refresh(officer_user)
    assert officer_user.name == "Officer Primary Renamed"
    assert officer_user.phone == "9998887771"


def test_officer_profile_update_validation_failures(client, officer_headers):

    resp1 = client.put("/api/officer/edit_profile", json={"phone": "12345"}, headers=officer_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Phone must be a 10-digit number"


def test_officer_search_success(client, officer_headers, assigned_complaint):
    response = client.post("/api/officer/search", json={"query": "Pothole"}, headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert "tickets" in data
    assert len(data["tickets"]) >= 1
    assert data["tickets"][0]["id"] == assigned_complaint.id


def test_officer_search_empty_query(client, officer_headers):
    response = client.post("/api/officer/search", json={"query": ""}, headers=officer_headers)
    assert response.status_code == 200
    assert response.json() == {"tickets": []}


def test_officer_ticket_detail_success(client, officer_headers, assigned_complaint):
    response = client.get(f"/api/officer/ticket/{assigned_complaint.id}", headers=officer_headers)
    assert response.status_code == 200

    data = response.json()
    assert "complaint" in data
    assert "updates" in data
    assert data["complaint"]["id"] == assigned_complaint.id
    assert data["complaint"]["token"] == assigned_complaint.token
    assert data["complaint"]["status"] == "Assigned"


def test_officer_ticket_detail_forbidden_for_other_officer(client, second_officer_headers, assigned_complaint):
    response = client.get(f"/api/officer/ticket/{assigned_complaint.id}", headers=second_officer_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "This ticket is not assigned to you"


def test_officer_ticket_detail_not_found(client, officer_headers):
    response = client.get("/api/officer/ticket/99999", headers=officer_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


def test_officer_ticket_status_update_valid_transitions(client, officer_headers, assigned_complaint, db_session):

    resp1 = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "En Route"}, headers=officer_headers)
    assert resp1.status_code == 200
    assert resp1.json()["message"] == "Status updated to En Route"

    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "En Route"

    resp2 = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "On Site"}, headers=officer_headers)
    assert resp2.status_code == 200

    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "On Site"

    resp3 = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "In Progress"}, headers=officer_headers)
    assert resp3.status_code == 200

    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "In Progress"

    updates = db_session.query(ComplaintUpdate).filter_by(complaint_id=assigned_complaint.id).all()
    assert len(updates) == 3


def test_officer_ticket_status_update_invalid_transition(client, officer_headers, assigned_complaint):
    response = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={"status": "Resolved"}, headers=officer_headers)
    assert response.status_code == 400
    assert "Cannot transition from 'Assigned' to 'Resolved'" in response.json()["detail"]


def test_officer_ticket_status_update_assigned_to_in_progress_rejected(client, officer_headers, assigned_complaint, db_session):
    response = client.put(
        f"/api/officer/ticket/{assigned_complaint.id}/status",
        json={"status": "In Progress"},
        headers=officer_headers
    )
    assert response.status_code == 400
    assert "Cannot transition from 'Assigned' to 'In Progress'" in response.json()["detail"]

    db_session.refresh(assigned_complaint)
    assert assigned_complaint.status == "Assigned"


def test_officer_ticket_status_update_missing_status(client, officer_headers, assigned_complaint):
    response = client.put(f"/api/officer/ticket/{assigned_complaint.id}/status", json={}, headers=officer_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "New status is required"


def test_officer_ticket_status_update_not_found(client, officer_headers):
    response = client.put("/api/officer/ticket/99999/status", json={"status": "En Route"}, headers=officer_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


def test_officer_ticket_resolve_success(client, officer_headers, in_progress_complaint, db_session):
    payload = {
        "resolution_note": "Pipe repaired and pressure tested successfully."
    }

    response = client.post(f"/api/officer/ticket/{in_progress_complaint.id}/resolve", data=payload, headers=officer_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Ticket resolved successfully"

    db_session.refresh(in_progress_complaint)
    assert in_progress_complaint.status == "Resolved"
    assert in_progress_complaint.resolution_note == "Pipe repaired and pressure tested successfully."
    assert in_progress_complaint.resolution_photos == []
    assert in_progress_complaint.resolved_at is not None

    audit = db_session.query(ComplaintUpdate).filter_by(complaint_id=in_progress_complaint.id, new_status="Resolved").first()
    assert audit is not None


def test_officer_ticket_resolve_invalid_initial_status(client, officer_headers, assigned_complaint):
    payload = {"resolution_note": "Premature resolution attempt"}
    response = client.post(f"/api/officer/ticket/{assigned_complaint.id}/resolve", data=payload, headers=officer_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Ticket must be in progress or on site to resolve"


def test_officer_ticket_resolve_not_found(client, officer_headers):
    response = client.post("/api/officer/ticket/99999/resolve", json={}, headers=officer_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"
