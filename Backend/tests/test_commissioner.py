import pytest
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password, verify_password
from application.helpers.models import User, Role, Department, Complaint, ComplaintUpdate, UtilityBill, FacilityBooking
from application.middlewares.init_jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def comm_user(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="commissioner").first()
    comm = User(
        email="commissioner.main@civicresolve.in",
        password=hash_password("CommSecret123!"),
        name="Chief Commissioner",
        role="commissioner",
        badge_id="COM-001",
        phone="9876543200",
        address="Municipal HQ",
        pincode="110001",
        is_active=True
    )
    if role:
        comm.roles.append(role)
    db_session.add(comm)
    db_session.commit()
    db_session.refresh(comm)
    return comm


@pytest.fixture
def comm_headers(comm_user: User) -> dict:
    token = create_access_token(comm_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def officer_headers(db_session: Session) -> dict:
    role = db_session.query(Role).filter_by(name="field_officer").first()
    officer = User(
        email="officer.commtest@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Officer Role Test",
        role="field_officer",
        badge_id="OFF-701",
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
def citizen_headers(db_session: Session) -> dict:
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.commtest@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Citizen Role Test",
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
def sample_department(db_session: Session) -> Department:
    dept = Department(name="Water Supply & Drainage")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def sample_complaint(db_session: Session, sample_department: Department) -> Complaint:
    complaint = Complaint(
        token="CMP-7701",
        title="Water Pipe Leakage on High Street",
        description="Major water pipe burst near city center causing road flooding",
        location="High Street & 2nd Ave",
        status="Submitted",
        severity="Critical",
        department_id=sample_department.id,
        department=sample_department.name
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint


@pytest.fixture
def sample_paid_bill(db_session: Session) -> UtilityBill:
    from datetime import date
    bill = UtilityBill(
        bill_type="Water",
        bill_number="UB-TEST-99",
        amount=150.0,
        due_date=date.today(),
        status="Paid"
    )
    db_session.add(bill)
    db_session.commit()
    db_session.refresh(bill)
    return bill


@pytest.fixture
def sample_confirmed_booking(db_session: Session) -> FacilityBooking:
    from datetime import date
    booking = FacilityBooking(
        booking_reference="BK-TEST-99",
        booked_date=date.today(),
        amount_paid=500.0,
        status="Confirmed"
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking


def test_commissioner_endpoints_unauthorized(client):
    assert client.get("/api/commissioner/dash").status_code == 401
    assert client.get("/api/commissioner/complaints").status_code == 401
    assert client.get("/api/commissioner/complaint/1").status_code == 401
    assert client.get("/api/commissioner/categories").status_code == 401
    assert client.post("/api/commissioner/category", json={}).status_code == 401
    assert client.delete("/api/commissioner/category/1").status_code == 401
    assert client.get("/api/commissioner/citizens").status_code == 401
    assert client.post("/api/commissioner/search", json={}).status_code == 401
    assert client.get("/api/commissioner/profile").status_code == 401
    assert client.put("/api/commissioner/edit_profile", json={}).status_code == 401


def test_commissioner_endpoints_forbidden_for_officer_and_citizen(client, officer_headers, citizen_headers):
    for headers in [officer_headers, citizen_headers]:
        assert client.get("/api/commissioner/dash", headers=headers).status_code == 403
        assert client.get("/api/commissioner/complaints", headers=headers).status_code == 403
        assert client.get("/api/commissioner/complaint/1", headers=headers).status_code == 403
        assert client.get("/api/commissioner/categories", headers=headers).status_code == 403
        assert client.post("/api/commissioner/category", json={}, headers=headers).status_code == 403
        assert client.delete("/api/commissioner/category/1", headers=headers).status_code == 403
        assert client.get("/api/commissioner/citizens", headers=headers).status_code == 403
        assert client.post("/api/commissioner/search", json={}, headers=headers).status_code == 403
        assert client.put("/api/commissioner/edit_profile", json={}, headers=headers).status_code == 403


def test_commissioner_dashboard_kpis_and_revenue(
    client,
    comm_headers,
    sample_complaint,
    sample_paid_bill,
    sample_confirmed_booking
):
    response = client.get("/api/commissioner/dash", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["totalComplaints"] >= 1
    assert data["pendingComplaints"] >= 1
    assert data["criticalComplaints"] >= 1
    assert data["billRevenue"] >= 150.0
    assert data["bookingRevenue"] >= 500.0
    assert data["totalRevenue"] >= 650.0
    assert isinstance(data["complaintsByCategory"], list)
    assert isinstance(data["complaintsByStatus"], list)


def test_commissioner_complaints_list_all_and_categories(client, comm_headers, sample_complaint):
    response = client.get("/api/commissioner/complaints", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "complaints" in data
    assert "categories" in data
    assert any(c["id"] == sample_complaint.id for c in data["complaints"])


def test_commissioner_complaints_list_filtered_by_status_and_dept(
    client,
    comm_headers,
    sample_complaint,
    sample_department
):
    response = client.get(
        f"/api/commissioner/complaints?status=Submitted&department_id={sample_department.id}",
        headers=comm_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["complaints"]) >= 1
    assert data["complaints"][0]["status"] == "Submitted"
    assert data["complaints"][0]["departmentId"] == sample_department.id


def test_commissioner_complaint_detail_success(client, comm_headers, sample_complaint, db_session):

    update = ComplaintUpdate(
        complaint_id=sample_complaint.id,
        old_status="Submitted",
        new_status="Submitted",
        note="Initial audit log"
    )
    db_session.add(update)
    db_session.commit()

    response = client.get(f"/api/commissioner/complaint/{sample_complaint.id}", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "complaint" in data
    assert "updates" in data
    assert data["complaint"]["id"] == sample_complaint.id
    assert data["complaint"]["token"] == sample_complaint.token
    assert len(data["updates"]) >= 1


def test_commissioner_complaint_detail_not_found(client, comm_headers):
    response = client.get("/api/commissioner/complaint/99999", headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


def test_commissioner_categories_list_success(client, comm_headers, sample_department):
    response = client.get("/api/commissioner/categories", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "categories" in data
    assert any(c["id"] == sample_department.id for c in data["categories"])


def test_commissioner_category_add_create_success(client, comm_headers, db_session):
    payload = {"name": "Electrical & Power"}
    response = client.post("/api/commissioner/category", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert "created successfully" in response.json()["message"]

    dept = db_session.query(Department).filter_by(name="Electrical & Power").first()
    assert dept is not None


def test_commissioner_category_add_create_duplicate_conflict(client, comm_headers, sample_department):
    payload = {"name": sample_department.name}
    response = client.post("/api/commissioner/category", json=payload, headers=comm_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Category already exists"


def test_commissioner_category_add_missing_name(client, comm_headers):
    response = client.post("/api/commissioner/category", json={}, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Category name is required"


def test_commissioner_category_add_edit_success(client, comm_headers, sample_department, db_session):
    payload = {
        "id": sample_department.id,
        "name": "Water Supply Renamed"
    }

    response = client.post("/api/commissioner/category", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]

    db_session.refresh(sample_department)
    assert sample_department.name == "Water Supply Renamed"


def test_commissioner_category_add_edit_conflict_with_other_category(client, comm_headers, sample_department, db_session):
    dept2 = Department(name="Other Department")
    db_session.add(dept2)
    db_session.commit()

    payload = {
        "id": sample_department.id,
        "name": "Other Department"
    }

    response = client.post("/api/commissioner/category", json=payload, headers=comm_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Category already exists"


def test_commissioner_category_add_edit_not_found(client, comm_headers):
    payload = {
        "id": 99999,
        "name": "Ghost Category"
    }

    response = client.post("/api/commissioner/category", json=payload, headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_commissioner_category_delete_success(client, comm_headers, sample_department, db_session):
    response = client.delete(f"/api/commissioner/category/{sample_department.id}", headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted"

    deleted = db_session.get(Department, sample_department.id)
    assert deleted is None


def test_commissioner_category_delete_not_found(client, comm_headers):
    response = client.delete("/api/commissioner/category/99999", headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_commissioner_citizens_list_success(client, comm_headers, db_session):
    role = db_session.query(Role).filter_by(name="citizen").first()
    citizen = User(
        email="citizen.registry@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Registry Citizen",
        role="citizen",
        pincode="110001",
        is_active=True
    )
    if role:
        citizen.roles.append(role)
    db_session.add(citizen)
    db_session.commit()

    response = client.get("/api/commissioner/citizens", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "citizens" in data
    assert any(c["email"] == "citizen.registry@civicresolve.in" for c in data["citizens"])


def test_commissioner_search_success(client, comm_headers, sample_complaint):
    response = client.post("/api/commissioner/search", json={"query": "Water Pipe"}, headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "complaints" in data
    assert len(data["complaints"]) >= 1
    assert data["complaints"][0]["id"] == sample_complaint.id


def test_commissioner_search_empty_query(client, comm_headers):
    response = client.post("/api/commissioner/search", json={"query": ""}, headers=comm_headers)
    assert response.status_code == 200
    assert response.json() == {"complaints": []}


def test_commissioner_profile_fetch_success(client, comm_headers, comm_user):
    response = client.get("/api/commissioner/profile", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == comm_user.id
    assert data["email"] == comm_user.email
    assert data["name"] == comm_user.name


def test_commissioner_profile_update_success(client, comm_headers, comm_user, db_session):
    payload = {
        "name": "Chief Commissioner Updated",
        "phone": "9998887770"
    }

    response = client.put("/api/commissioner/edit_profile", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"

    db_session.refresh(comm_user)
    assert comm_user.name == "Chief Commissioner Updated"
    assert comm_user.phone == "9998887770"


def test_commissioner_profile_update_validation_failures(client, comm_headers):

    resp1 = client.put("/api/commissioner/edit_profile", json={"phone": "12345"}, headers=comm_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Phone must be a 10-digit number"
