from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session

from application.extensions.security_extn import hash_password
from application.helpers.models import Facility, FacilityBooking, Role, User
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
    user = User(
        email="comm.fac@civicresolve.in",
        password=hash_password("CommPass123!"),
        name="Facility Commissioner",
        role="commissioner",
        badge_id="COM-FAC-1",
        is_active=True,
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
def citizen_user(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.fac@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Facility Citizen One",
        role="citizen",
        phone="9876543210",
        address="100 Civic Lane",
        pincode="110001",
        is_active=True,
    )
    if role:
        user.roles.append(role)
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
        email="citizen.fac2@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Facility Citizen Two",
        role="citizen",
        phone="9876543211",
        address="101 Civic Lane",
        pincode="110001",
        is_active=True,
    )
    if role:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_citizen_headers(second_citizen_user: User) -> dict:
    token = create_access_token(second_citizen_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def officer_headers(db_session: Session) -> dict:
    role = db_session.query(Role).filter_by(name="field_officer").first()
    officer = User(
        email="officer.fac@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Officer Facility Test",
        role="field_officer",
        badge_id="OFF-FAC-1",
        is_active=True,
    )
    if role:
        officer.roles.append(role)
    db_session.add(officer)
    db_session.commit()
    db_session.refresh(officer)
    token = create_access_token(officer.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def active_facility(db_session: Session) -> Facility:
    facility = Facility(
        name="Town Hall Auditorium",
        facility_type="Auditorium",
        address="1 Central Plaza",
        pincode="110001",
        price_per_day=500.0,
        capacity=200,
        description="Spacious venue for public and private events",
        is_active=True,
    )
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


@pytest.fixture
def inactive_facility(db_session: Session) -> Facility:
    facility = Facility(
        name="Closed Community Center",
        facility_type="Community Hall",
        address="99 Old Road",
        pincode="110002",
        price_per_day=200.0,
        capacity=50,
        description="Under renovation",
        is_active=False,
    )
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


@pytest.fixture
def sample_booking(
    db_session: Session, active_facility: Facility, citizen_user: User
) -> FacilityBooking:
    booking_date = date.today() + timedelta(days=5)
    booking = FacilityBooking(
        user_id=citizen_user.id,
        facility_id=active_facility.id,
        facility_name=active_facility.name,
        booking_reference="BKG-TEST-1234",
        booked_date=booking_date,
        amount_paid=active_facility.price_per_day,
        purpose="Town Hall Meeting",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking


def test_commissioner_facility_endpoints_unauthorized(client):
    assert client.get("/api/commissioner/facilities").status_code == 401
    assert client.post("/api/commissioner/facility", json={}).status_code == 401
    assert client.put("/api/commissioner/facility/1", json={}).status_code == 401
    assert client.delete("/api/commissioner/facility/1").status_code == 401


def test_citizen_facility_endpoints_unauthorized(client):
    assert client.get("/api/citizen/facilities").status_code == 401
    assert client.get("/api/citizen/facility/1").status_code == 401
    assert client.post("/api/citizen/book_facility/1", json={}).status_code == 401
    assert client.get("/api/citizen/bookings").status_code == 401


def test_commissioner_facility_endpoints_forbidden_for_citizen_and_officer(
    client, citizen_headers, officer_headers
):
    for headers in [citizen_headers, officer_headers]:
        res_get = client.get("/api/commissioner/facilities", headers=headers)
        assert res_get.status_code == 403
        assert res_get.json()["detail"] == "Commissioner access required"

        assert (
            client.post("/api/commissioner/facility", json={}, headers=headers).status_code == 403
        )
        assert (
            client.put("/api/commissioner/facility/1", json={}, headers=headers).status_code == 403
        )
        assert client.delete("/api/commissioner/facility/1", headers=headers).status_code == 403


def test_citizen_facility_endpoints_forbidden_for_commissioner_and_officer(
    client, comm_headers, officer_headers
):
    for headers in [comm_headers, officer_headers]:
        assert client.get("/api/citizen/facilities", headers=headers).status_code == 403
        assert client.get("/api/citizen/facility/1", headers=headers).status_code == 403
        assert (
            client.post("/api/citizen/book_facility/1", json={}, headers=headers).status_code == 403
        )
        assert client.get("/api/citizen/bookings", headers=headers).status_code == 403


def test_commissioner_facilities_list_success(
    client, comm_headers, active_facility, inactive_facility
):
    response = client.get("/api/commissioner/facilities", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "facilities" in data
    facility_ids = [f["id"] for f in data["facilities"]]
    assert active_facility.id in facility_ids
    assert inactive_facility.id in facility_ids


def test_commissioner_add_facility_success(client, comm_headers, db_session):
    payload = {
        "name": "Sports Complex Arena",
        "facilityType": "Indoor Stadium",
        "address": "50 Ring Road",
        "pincode": "110005",
        "pricePerDay": 750.0,
        "description": "State-of-the-art sports complex",
    }

    response = client.post("/api/commissioner/facility", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert "created successfully" in response.json()["message"]

    created = db_session.query(Facility).filter_by(name="Sports Complex Arena").first()
    assert created is not None
    assert created.facility_type == "Indoor Stadium"
    assert created.price_per_day == 750.0
    assert created.is_active is True


def test_commissioner_add_facility_validation_failures(client, comm_headers):

    resp1 = client.post(
        "/api/commissioner/facility",
        json={
            "name": "A",
            "facilityType": "Type",
            "address": "Valid Address 123",
            "pincode": "110001",
            "pricePerDay": 100.0,
        },
        headers=comm_headers,
    )
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Name must be at least 2 characters long"

    resp2 = client.post(
        "/api/commissioner/facility",
        json={
            "name": "Valid Name",
            "facilityType": "Type",
            "address": "Valid Address 123",
            "pincode": "123",
            "pricePerDay": 100.0,
        },
        headers=comm_headers,
    )
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Pincode must be a 6-digit number"

    resp3 = client.post(
        "/api/commissioner/facility",
        json={
            "name": "Valid Name",
            "address": "Valid Address 123",
            "pincode": "110001",
            "pricePerDay": 100.0,
        },
        headers=comm_headers,
    )
    assert resp3.status_code == 400
    assert resp3.json()["detail"] == "Facility type is required"


def test_commissioner_update_facility_success(client, comm_headers, active_facility, db_session):
    payload = {"name": "Town Hall Auditorium Renamed", "pricePerDay": 600.0, "isActive": False}

    response = client.put(
        f"/api/commissioner/facility/{active_facility.id}", json=payload, headers=comm_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Facility updated successfully"

    db_session.refresh(active_facility)
    assert active_facility.name == "Town Hall Auditorium Renamed"
    assert active_facility.price_per_day == 600.0
    assert active_facility.is_active is False


def test_commissioner_update_facility_not_found(client, comm_headers):
    response = client.put(
        "/api/commissioner/facility/99999", json={"name": "Ghost"}, headers=comm_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


def test_commissioner_update_facility_invalid_price(client, comm_headers, active_facility):
    response = client.put(
        f"/api/commissioner/facility/{active_facility.id}",
        json={"pricePerDay": -50.0},
        headers=comm_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Price must be greater than 0"


def test_commissioner_delete_facility_success(client, comm_headers, active_facility, db_session):
    response = client.delete(
        f"/api/commissioner/facility/{active_facility.id}", headers=comm_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Facility deleted"

    deleted = db_session.get(Facility, active_facility.id)
    assert deleted is None


def test_commissioner_delete_facility_not_found(client, comm_headers):
    response = client.delete("/api/commissioner/facility/99999", headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


def test_citizen_facilities_list_includes_inactive(
    client, citizen_headers, active_facility, inactive_facility
):
    response = client.get("/api/citizen/facilities", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "facilities" in data
    facility_ids = [f["id"] for f in data["facilities"]]
    assert active_facility.id in facility_ids
    assert inactive_facility.id in facility_ids


def test_citizen_facility_detail_success(client, citizen_headers, active_facility, sample_booking):
    response = client.get(f"/api/citizen/facility/{active_facility.id}", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "facility" in data
    assert "bookedDates" in data
    assert "myBookedDates" in data
    assert data["facility"]["id"] == active_facility.id
    assert sample_booking.booked_date.isoformat() in data["bookedDates"]
    assert sample_booking.booked_date.isoformat() in data["myBookedDates"]


def test_citizen_facility_detail_inactive_or_not_found(client, citizen_headers, inactive_facility):

    resp1 = client.get(f"/api/citizen/facility/{inactive_facility.id}", headers=citizen_headers)
    assert resp1.status_code == 404
    assert resp1.json()["detail"] == "Facility not found"

    resp2 = client.get("/api/citizen/facility/99999", headers=citizen_headers)
    assert resp2.status_code == 404
    assert resp2.json()["detail"] == "Facility not found"


def test_citizen_book_facility_success(
    client, citizen_headers, active_facility, db_session, citizen_user
):
    target_date = date.today() + timedelta(days=10)
    payload = {"bookedDate": target_date.isoformat(), "purpose": "Birthday Party Gathering"}

    response = client.post(
        f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Booking confirmed"
    assert "booking" in data
    assert data["booking"]["facilityName"] == active_facility.name
    assert data["booking"]["amountPaid"] == active_facility.price_per_day
    assert data["booking"]["bookingReference"].startswith("BKG-")

    created_booking = (
        db_session.query(FacilityBooking)
        .filter_by(booking_reference=data["booking"]["bookingReference"])
        .first()
    )
    assert created_booking is not None
    assert created_booking.user_id == citizen_user.id
    assert created_booking.facility_id == active_facility.id
    assert created_booking.booked_date == target_date


def test_citizen_book_facility_past_date_fails(client, citizen_headers, active_facility):
    past_date = date.today() - timedelta(days=1)
    payload = {"booked_date": past_date.isoformat()}

    response = client.post(
        f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot book a past date"


def test_citizen_book_facility_too_far_in_future_fails(client, citizen_headers, active_facility):
    far_future = date.today() + timedelta(days=95)
    payload = {"booked_date": far_future.isoformat()}

    response = client.post(
        f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot book more than 90 days in advance"


def test_citizen_book_facility_duplicate_date_fails(
    client, citizen_headers, active_facility, sample_booking
):
    payload = {"booked_date": sample_booking.booked_date.isoformat()}

    response = client.post(
        f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "This date is already booked"


def test_citizen_book_facility_missing_or_invalid_date(client, citizen_headers, active_facility):

    resp1 = client.post(
        f"/api/citizen/book_facility/{active_facility.id}", json={}, headers=citizen_headers
    )
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Date is required"

    resp2 = client.post(
        f"/api/citizen/book_facility/{active_facility.id}",
        json={"bookedDate": "invalid-date"},
        headers=citizen_headers,
    )
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Invalid date format. Use YYYY-MM-DD"


def test_citizen_book_facility_inactive_facility_fails(client, citizen_headers, inactive_facility):
    target_date = date.today() + timedelta(days=2)
    payload = {"booked_date": target_date.isoformat()}

    response = client.post(
        f"/api/citizen/book_facility/{inactive_facility.id}", json=payload, headers=citizen_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


def test_citizen_bookings_list_success(client, citizen_headers, sample_booking):
    response = client.get("/api/citizen/bookings", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "bookings" in data
    assert len(data["bookings"]) >= 1
    matched = next((b for b in data["bookings"] if b["id"] == sample_booking.id), None)
    assert matched is not None
    assert matched["bookingReference"] == sample_booking.booking_reference
    assert matched["facilityName"] == sample_booking.facility.name
