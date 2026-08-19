import pytest
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role, Department, Complaint, ComplaintUpdate
from application.middlewares.init_jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_officer_roles(db_session: Session):
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def comm_user(db_session: Session) -> User:
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
    token = create_access_token(comm_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def citizen_headers(db_session: Session) -> dict:
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
    dept = Department(name="Health & Sanitation")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def second_department(db_session: Session) -> Department:
    dept = Department(name="Roads & Infrastructure")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def existing_officer(db_session: Session, test_department: Department) -> User:
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


def test_officer_endpoints_unauthorized(client):
    assert client.get("/api/commissioner/officers").status_code == 401
    assert client.post("/api/commissioner/officer", json={}).status_code == 401
    assert client.put("/api/commissioner/officer/1", json={}).status_code == 401
    assert client.delete("/api/commissioner/officer/1").status_code == 401
    assert client.put("/api/commissioner/assign/1", json={}).status_code == 401


def test_officer_endpoints_forbidden_for_citizen(client, citizen_headers):
    assert client.get("/api/commissioner/officers", headers=citizen_headers).status_code == 403
    assert client.post("/api/commissioner/officer", json={}, headers=citizen_headers).status_code == 403
    assert client.put("/api/commissioner/officer/1", json={}, headers=citizen_headers).status_code == 403
    assert client.delete("/api/commissioner/officer/1", headers=citizen_headers).status_code == 403
    assert client.put("/api/commissioner/assign/1", json={}, headers=citizen_headers).status_code == 403


def test_list_officers_success(client, comm_headers, existing_officer):
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


def test_create_officer_by_department_id(client, comm_headers, test_department, db_session):
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

    officer_db = db_session.query(User).filter_by(email="new.officer1@civicresolve.in").first()
    assert officer_db is not None
    assert officer_db.department_id == test_department.id
    assert officer_db.department == test_department.name
    assert officer_db.role == "field_officer"
    assert officer_db.badge_id == "OFF-201"


def test_create_officer_by_department_name(client, comm_headers, test_department, db_session):
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
    payload = {
        "email": "invalid.dept@civicresolve.in",
        "name": "Officer Unknown",
        "department": "NonExistentDept999"
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid department"


def test_create_officer_missing_department(client, comm_headers):
    payload = {
        "email": "nodept@civicresolve.in",
        "name": "Officer NoDept"
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Department is required"


def test_create_officer_duplicate_email(client, comm_headers, existing_officer):
    payload = {
        "email": existing_officer.email,
        "name": "Duplicate Email Officer",
        "department": existing_officer.department
    }

    response = client.post("/api/commissioner/officer", json=payload, headers=comm_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_create_officer_duplicate_badge_id(client, comm_headers, existing_officer, test_department):
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

    resp1 = client.post("/api/commissioner/officer", json={
        "email": "bad-email",
        "name": "Valid Name",
        "department_id": test_department.id
    }, headers=comm_headers)
    assert resp1.status_code == 400

    resp2 = client.post("/api/commissioner/officer", json={
        "email": "valid.email@civicresolve.in",
        "name": "A",
        "department_id": test_department.id
    }, headers=comm_headers)
    assert resp2.status_code == 400


def test_update_officer_success(client, comm_headers, existing_officer, db_session):
    payload = {
        "name": "Officer Bob Updated",
        "phone": "9998887776",
        "badgeId": "OFF-101-UPD",
        "active": True
    }

    response = client.put(f"/api/commissioner/officer/{existing_officer.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Officer updated successfully"

    db_session.refresh(existing_officer)
    assert existing_officer.name == "Officer Bob Updated"
    assert existing_officer.phone == "9998887776"
    assert existing_officer.badge_id == "OFF-101-UPD"


def test_update_officer_department(client, comm_headers, existing_officer, second_department, db_session):
    payload = {
        "department_id": second_department.id
    }

    response = client.put(f"/api/commissioner/officer/{existing_officer.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200

    db_session.refresh(existing_officer)
    assert existing_officer.department_id == second_department.id
    assert existing_officer.department == second_department.name


def test_update_officer_invalid_department(client, comm_headers, existing_officer):
    payload = {
        "department": "FakeDepartment99"
    }

    response = client.put(f"/api/commissioner/officer/{existing_officer.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid department"


def test_update_non_existent_officer(client, comm_headers):
    response = client.put("/api/commissioner/officer/99999", json={"name": "Ghost"}, headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Officer not found"


def test_delete_officer_soft_delete(client, comm_headers, existing_officer, db_session):
    response = client.delete(f"/api/commissioner/officer/{existing_officer.id}", headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Officer deactivated successfully"

    db_session.refresh(existing_officer)
    assert existing_officer.is_active is False


def test_delete_non_existent_officer(client, comm_headers):
    response = client.delete("/api/commissioner/officer/99999", headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Officer not found"


def test_assign_officer_success(client, comm_headers, sample_complaint, existing_officer, db_session):
    sample_complaint.severity = "Critical"
    db_session.commit()

    payload = {
        "officerId": existing_officer.id,
        "severity": "Critical"
    }

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == f"Complaint assigned to {existing_officer.name}"

    db_session.refresh(sample_complaint)
    assert sample_complaint.assigned_officer_id == existing_officer.id
    assert sample_complaint.assigned_officer_name == existing_officer.name
    assert sample_complaint.status == "Assigned"
    assert sample_complaint.severity == "Critical"

    audit = db_session.query(ComplaintUpdate).filter_by(complaint_id=sample_complaint.id).first()
    assert audit is not None
    assert audit.old_status == "Submitted"
    assert audit.new_status == "Assigned"


def test_assign_officer_non_severe_complaint_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    sample_complaint.severity = "Normal"
    db_session.commit()

    payload = {"officerId": existing_officer.id}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "Normal"
    assert sample_complaint.assigned_officer_id is None


def test_assign_officer_low_severity_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    sample_complaint.severity = "Low"
    db_session.commit()

    payload = {"officerId": existing_officer.id}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "Low"
    assert sample_complaint.assigned_officer_id is None


def test_assign_officer_high_severity_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    sample_complaint.severity = "High"
    db_session.commit()

    payload = {"officerId": existing_officer.id}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "High"
    assert sample_complaint.assigned_officer_id is None


def test_assign_officer_bypass_attempt_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    sample_complaint.severity = "Normal"
    db_session.commit()

    payload = {
        "officerId": existing_officer.id,
        "severity": "Critical"
    }

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer assignment is only allowed for severe complaints"

    db_session.refresh(sample_complaint)
    assert sample_complaint.severity == "Normal"
    assert sample_complaint.assigned_officer_id is None


def test_assign_deactivated_officer_fails(client, comm_headers, sample_complaint, existing_officer, db_session):
    sample_complaint.severity = "Critical"
    existing_officer.is_active = False
    db_session.commit()

    payload = {
        "officerId": existing_officer.id
    }

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer account is deactivated"


def test_assign_invalid_officer_fails(client, comm_headers, sample_complaint, db_session):
    sample_complaint.severity = "Critical"
    db_session.commit()

    payload = {"officerId": 99999}

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid officer"


def test_assign_non_existent_complaint(client, comm_headers, existing_officer):
    payload = {"officerId": existing_officer.id}
    response = client.put("/api/commissioner/assign/99999", json=payload, headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


def test_assign_missing_officer_id(client, comm_headers, sample_complaint, db_session):
    sample_complaint.severity = "Critical"
    db_session.commit()

    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json={}, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Officer ID is required"


def test_assign_officer_reassigns_in_progress_critical_complaint(client, comm_headers, sample_complaint, existing_officer, db_session, test_department):
    second_officer = User(
        email="second.officer@civicresolve.in",
        password=hash_password("OfficerPass123!"),
        name="Officer Alice",
        role="field_officer",
        badge_id="OFF-102",
        department_id=test_department.id,
        department=test_department.name,
        is_active=True
    )
    role = db_session.query(Role).filter_by(name="field_officer").first()
    if role:
        second_officer.roles.append(role)
    db_session.add(second_officer)

    sample_complaint.severity = "Critical"
    sample_complaint.status = "In Progress"
    sample_complaint.assigned_officer_id = existing_officer.id
    sample_complaint.assigned_officer_name = existing_officer.name
    db_session.commit()

    payload = {"officerId": second_officer.id}
    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)

    assert response.status_code == 200
    assert response.json()["message"] == f"Complaint assigned to {second_officer.name}"

    db_session.refresh(sample_complaint)
    assert sample_complaint.assigned_officer_id == second_officer.id
    assert sample_complaint.assigned_officer_name == second_officer.name
    assert sample_complaint.status == "In Progress"

    audit = db_session.query(ComplaintUpdate).filter_by(complaint_id=sample_complaint.id).order_by(ComplaintUpdate.id.desc()).first()
    assert audit is not None
    assert audit.old_status == "In Progress"
    assert audit.new_status == "In Progress"
    assert "Officer Alice" in audit.note


def test_assign_officer_fails_for_non_field_officer_role(client, comm_headers, sample_complaint, db_session):
    role = db_session.query(Role).filter_by(name="citizen").first()
    non_officer = User(
        email="citizen.target@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Citizen Target",
        role="citizen",
        is_active=True
    )
    if role:
        non_officer.roles.append(role)
    db_session.add(non_officer)

    sample_complaint.severity = "Critical"
    db_session.commit()

    payload = {"officerId": non_officer.id}
    response = client.put(f"/api/commissioner/assign/{sample_complaint.id}", json=payload, headers=comm_headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid officer"

    db_session.refresh(sample_complaint)
    assert sample_complaint.assigned_officer_id is None
