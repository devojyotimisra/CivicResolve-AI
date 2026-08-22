import pytest
from sqlalchemy.orm import Session

from application.extensions.security_extn import hash_password
from application.helpers.models import Complaint, Department, Role, User
from application.middlewares.init_jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def citizen_user(db_session: Session) -> User:
    user = User(
        email="citizen.user@civicresolve.in",
        password=hash_password("Pass123!"),
        name="John Citizen",
        role="citizen",
        phone="9876543210",
        address="123 Civic Lane",
        pincode="560001",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def citizen_headers(citizen_user: User) -> dict:
    token = create_access_token(citizen_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_citizen_user(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.second@civicresolve.in",
        password=hash_password("CitizenSecret123!"),
        name="Jane Citizen",
        role="citizen",
        phone="9876543211",
        address="456 Municipal Way",
        pincode="110002",
        is_active=True,
    )
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def comm_headers(db_session: Session) -> dict:
    user = User(
        email="comm.citizen_test@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Comm User",
        role="commissioner",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def officer_headers(db_session: Session) -> dict:
    user = User(
        email="officer.citizen_test@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Officer User",
        role="field_officer",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_department(db_session: Session) -> Department:
    dept = Department(name="Roads & Infrastructure")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def sample_complaint(db_session: Session, sample_department: Department) -> Complaint:
    complaint = Complaint(
        token="CRA-CITIZEN01",
        title="Pothole on MG Road",
        description="Large pothole near city center junction",
        location="MG Road, Sector 3",
        status="Submitted",
        severity="Normal",
        department_id=sample_department.id,
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)
    return complaint


def test_unauthenticated_access_blocked(client):
    assert client.get("/api/citizen/dash").status_code == 401
    assert client.get("/api/citizen/profile").status_code == 401
    assert client.put("/api/citizen/edit_profile", json={}).status_code == 401
    assert client.post("/api/citizen/search", json={}).status_code == 401


def test_citizen_endpoints_forbidden_for_commissioner_and_officer(
    client, comm_headers, officer_headers
):
    for headers in [comm_headers, officer_headers]:
        assert client.get("/api/citizen/dash", headers=headers).status_code == 403
        assert client.get("/api/citizen/profile", headers=headers).status_code == 403
        assert client.put("/api/citizen/edit_profile", json={}, headers=headers).status_code == 403
        assert client.post("/api/citizen/search", json={}, headers=headers).status_code == 403


def test_citizen_dashboard_success(client, citizen_headers, citizen_user):
    response = client.get("/api/citizen/dash", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["userName"] == citizen_user.name
    assert "totalBillsDue" in data
    assert "upcomingBookingsCount" in data
    assert isinstance(data["pendingBills"], list)
    assert isinstance(data["upcomingBookings"], list)


def test_citizen_profile_fetch_success(client, citizen_headers, citizen_user):
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
    payload = {
        "email": "john.updated@civicresolve.in",
        "name": "John Citizen Updated",
        "address": "999 Updated Boulevard",
        "pincode": "110005",
        "phone": "9998887775",
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


def test_citizen_profile_update_duplicate_email(client, citizen_headers, second_citizen_user):
    payload = {"email": second_citizen_user.email}
    response = client.put("/api/citizen/edit_profile", json=payload, headers=citizen_headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already in use"


def test_citizen_profile_update_validation_failures(client, citizen_headers):

    resp1 = client.put(
        "/api/citizen/edit_profile", json={"email": "bad-email"}, headers=citizen_headers
    )
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Invalid email format"

    resp2 = client.put("/api/citizen/edit_profile", json={"name": "A"}, headers=citizen_headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Name must be at least 2 characters long"

    resp3 = client.put(
        "/api/citizen/edit_profile", json={"address": "123"}, headers=citizen_headers
    )
    assert resp3.status_code == 400
    assert resp3.json()["detail"] == "Address must be at least 5 characters long"

    resp4 = client.put(
        "/api/citizen/edit_profile", json={"pincode": "1234"}, headers=citizen_headers
    )
    assert resp4.status_code == 400
    assert resp4.json()["detail"] == "Pincode must be a 6-digit number"

    resp5 = client.put(
        "/api/citizen/edit_profile", json={"phone": "12345"}, headers=citizen_headers
    )
    assert resp5.status_code == 400
    assert resp5.json()["detail"] == "Phone must be a 10-digit number"


def test_citizen_search_success(client, citizen_headers, db_session):
    from application.helpers.models import Facility

    facility = Facility(
        name="Citizen Park Community Hall",
        facility_type="Community Hall",
        address="10 Park Road",
        pincode="110001",
        price_per_day=300.0,
        is_active=True,
    )
    db_session.add(facility)
    db_session.commit()

    response = client.post(
        "/api/citizen/search", json={"query": "Community Hall"}, headers=citizen_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "facilities" in data
    assert any(f["id"] == facility.id for f in data["facilities"])


def test_citizen_search_empty_query(client, citizen_headers):
    response = client.post("/api/citizen/search", json={"query": ""}, headers=citizen_headers)
    assert response.status_code == 200
    assert response.json() == {"facilities": []}
