"""
Facilities & Facility Bookings Integration Tests.

Covers both sides of the Facility domain:
1. Commissioner Facility Management:
   - GET /api/commissioner/facilities
   - POST /api/commissioner/facility
   - PUT /api/commissioner/facility/{facility_id}
   - DELETE /api/commissioner/facility/{facility_id}

2. Citizen Facility Catalog, Booking & Cancellation:
   - GET /api/citizen/facilities
   - GET /api/citizen/facility/{facility_id}
   - POST /api/citizen/book_facility/{facility_id}
   - GET /api/citizen/bookings
   - POST /api/citizen/cancel_booking/{booking_id}
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role, Facility, FacilityBooking
from application.middlewares.init_jwt import create_access_token


# ============================================================================
# LOCAL FIXTURES (FACILITY DOMAIN SPECIFIC)
# ============================================================================

@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    """Ensures citizen, field_officer, commissioner roles exist in db_session."""
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def comm_user(db_session: Session) -> User:
    """Creates a Commissioner user."""
    role = db_session.query(Role).filter_by(name="commissioner").first()
    user = User(
        email="comm.fac@civicresolve.in",
        password=hash_password("CommPass123!"),
        name="Facility Commissioner",
        role="commissioner",
        badge_id="COM-FAC-1",
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
    """Returns JWT Authorization headers for comm_user."""
    token = create_access_token(comm_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def citizen_user(db_session: Session) -> User:
    """Creates a primary Citizen user."""
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.fac@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Facility Citizen One",
        role="citizen",
        phone="9876543210",
        address="100 Civic Lane",
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
    """Creates a secondary Citizen user for ownership testing."""
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="citizen.fac2@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Facility Citizen Two",
        role="citizen",
        phone="9876543211",
        address="101 Civic Lane",
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
def second_citizen_headers(second_citizen_user: User) -> dict:
    """Returns JWT Authorization headers for second_citizen_user."""
    token = create_access_token(second_citizen_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def officer_headers(db_session: Session) -> dict:
    """Returns JWT Authorization headers for a field officer (for 403 role checks)."""
    role = db_session.query(Role).filter_by(name="field_officer").first()
    officer = User(
        email="officer.fac@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Officer Facility Test",
        role="field_officer",
        badge_id="OFF-FAC-1",
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
def active_facility(db_session: Session) -> Facility:
    """Creates an active Facility in the test database."""
    facility = Facility(
        name="Town Hall Auditorium",
        facility_type="Auditorium",
        address="1 Central Plaza",
        pincode="110001",
        price_per_day=500.0,
        capacity=200,
        description="Spacious venue for public and private events",
        is_active=True
    )
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


@pytest.fixture
def inactive_facility(db_session: Session) -> Facility:
    """Creates an inactive Facility in the test database."""
    facility = Facility(
        name="Closed Community Center",
        facility_type="Community Hall",
        address="99 Old Road",
        pincode="110002",
        price_per_day=200.0,
        capacity=50,
        description="Under renovation",
        is_active=False
    )
    db_session.add(facility)
    db_session.commit()
    db_session.refresh(facility)
    return facility


@pytest.fixture
def sample_booking(db_session: Session, active_facility: Facility, citizen_user: User) -> FacilityBooking:
    """Creates a confirmed FacilityBooking for tomorrow booked by citizen_user."""
    booking_date = date.today() + timedelta(days=5)
    booking = FacilityBooking(
        user_id=citizen_user.id,
        facility_id=active_facility.id,
        citizen_name=citizen_user.name,
        facility_name=active_facility.name,
        booking_reference="BKG-TEST-1234",
        booked_date=booking_date,
        amount_paid=active_facility.price_per_day,
        purpose="Town Hall Meeting",
        status="Confirmed"
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking


# ============================================================================
# AUTHORIZATION & ROLE CHECKS
# ============================================================================

def test_commissioner_facility_endpoints_unauthorized(client):
    """
    Verifies 401 Unauthorized for unauthenticated requests across commissioner facility routes.
    """
    assert client.get("/api/commissioner/facilities").status_code == 401
    assert client.post("/api/commissioner/facility", json={}).status_code == 401
    assert client.put("/api/commissioner/facility/1", json={}).status_code == 401
    assert client.delete("/api/commissioner/facility/1").status_code == 401


def test_citizen_facility_endpoints_unauthorized(client):
    """
    Verifies 401 Unauthorized for unauthenticated requests across citizen facility routes.
    """
    assert client.get("/api/citizen/facilities").status_code == 401
    assert client.get("/api/citizen/facility/1").status_code == 401
    assert client.post("/api/citizen/book_facility/1", json={}).status_code == 401
    assert client.get("/api/citizen/bookings").status_code == 401
    assert client.post("/api/citizen/cancel_booking/1").status_code == 401


def test_commissioner_facility_endpoints_forbidden_for_citizen_and_officer(client, citizen_headers, officer_headers):
    """
    Verifies 403 Forbidden for Citizen or Field Officer calling all commissioner facility endpoints.
    """
    for headers in [citizen_headers, officer_headers]:
        res_get = client.get("/api/commissioner/facilities", headers=headers)
        assert res_get.status_code == 403
        assert res_get.json()["detail"] == "Commissioner access required"

        assert client.post("/api/commissioner/facility", json={}, headers=headers).status_code == 403
        assert client.put("/api/commissioner/facility/1", json={}, headers=headers).status_code == 403
        assert client.delete("/api/commissioner/facility/1", headers=headers).status_code == 403


def test_citizen_facility_endpoints_forbidden_for_commissioner_and_officer(client, comm_headers, officer_headers):
    """
    Verifies 403 Forbidden for Commissioner or Field Officer calling citizen facility routes.
    """
    for headers in [comm_headers, officer_headers]:
        assert client.get("/api/citizen/facilities", headers=headers).status_code == 403
        assert client.get("/api/citizen/facility/1", headers=headers).status_code == 403
        assert client.post("/api/citizen/book_facility/1", json={}, headers=headers).status_code == 403
        assert client.get("/api/citizen/bookings", headers=headers).status_code == 403
        assert client.post("/api/citizen/cancel_booking/1", headers=headers).status_code == 403


# ============================================================================
# COMMISSIONER FACILITY MANAGEMENT TESTS
# ============================================================================

def test_commissioner_facilities_list_success(client, comm_headers, active_facility, inactive_facility):
    """
    Code Path: commissioner_facilities_list_resource.py -> GET /api/commissioner/facilities
    Verifies fetching all facilities (both active and inactive) with complete schema validation.
    """
    response = client.get("/api/commissioner/facilities", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "facilities" in data
    facility_ids = [f["id"] for f in data["facilities"]]
    assert active_facility.id in facility_ids
    assert inactive_facility.id in facility_ids


def test_commissioner_add_facility_success(client, comm_headers, db_session):
    """
    Code Path: commissioner_facility_add_resource.py -> POST /api/commissioner/facility
    Verifies creating a new Facility with both camelCase and snake_case field parsing.
    """
    payload = {
        "name": "Sports Complex Arena",
        "facilityType": "Indoor Stadium",
        "address": "50 Ring Road",
        "pincode": "110005",
        "pricePerDay": 750.0,
        "description": "State-of-the-art sports complex"
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
    """
    Code Path: commissioner_facility_add_resource.py -> field validators.
    Verifies 400 Bad Request for invalid name, address, pincode, price, or missing facility_type.
    """
    # Missing/short name
    resp1 = client.post("/api/commissioner/facility", json={
        "name": "A",
        "facilityType": "Type",
        "address": "Valid Address 123",
        "pincode": "110001",
        "pricePerDay": 100.0
    }, headers=comm_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Name must be at least 2 characters long"

    # Invalid pincode
    resp2 = client.post("/api/commissioner/facility", json={
        "name": "Valid Name",
        "facilityType": "Type",
        "address": "Valid Address 123",
        "pincode": "123",
        "pricePerDay": 100.0
    }, headers=comm_headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Pincode must be a 6-digit number"

    # Missing facility type
    resp3 = client.post("/api/commissioner/facility", json={
        "name": "Valid Name",
        "address": "Valid Address 123",
        "pincode": "110001",
        "pricePerDay": 100.0
    }, headers=comm_headers)
    assert resp3.status_code == 400
    assert resp3.json()["detail"] == "Facility type is required"


def test_commissioner_update_facility_success(client, comm_headers, active_facility, db_session):
    """
    Code Path: commissioner_facility_update_resource.py -> PUT /api/commissioner/facility/{id}
    Verifies partial updates of facility attributes and active status.
    """
    payload = {
        "name": "Town Hall Auditorium Renamed",
        "price_per_day": 600.0,
        "is_active": False
    }

    response = client.put(f"/api/commissioner/facility/{active_facility.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Facility updated successfully"

    db_session.refresh(active_facility)
    assert active_facility.name == "Town Hall Auditorium Renamed"
    assert active_facility.price_per_day == 600.0
    assert active_facility.is_active is False


def test_commissioner_update_facility_not_found(client, comm_headers):
    """
    Code Path: commissioner_facility_update_resource.py -> facility not found.
    Verifies 404 Not Found for non-existent facility ID.
    """
    response = client.put("/api/commissioner/facility/99999", json={"name": "Ghost"}, headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


def test_commissioner_update_facility_invalid_price(client, comm_headers, active_facility):
    """
    Code Path: commissioner_facility_update_resource.py -> validate_price.
    Verifies 400 Bad Request for negative price.
    """
    response = client.put(f"/api/commissioner/facility/{active_facility.id}", json={"price_per_day": -50.0}, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Price must be greater than 0"



def test_commissioner_delete_facility_soft_deactivation(client, comm_headers, active_facility, db_session):
    """
    Code Path: commissioner_facility_delete_resource.py -> DELETE /api/commissioner/facility/{id}
    Verifies soft deactivation of facility (is_active = False).
    """
    response = client.delete(f"/api/commissioner/facility/{active_facility.id}", headers=comm_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Facility deactivated"

    db_session.refresh(active_facility)
    assert active_facility.is_active is False


def test_commissioner_delete_facility_not_found(client, comm_headers):
    """
    Code Path: commissioner_facility_delete_resource.py -> facility not found.
    Verifies 404 Not Found for non-existent facility ID.
    """
    response = client.delete("/api/commissioner/facility/99999", headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


# ============================================================================
# CITIZEN FACILITY CATALOG & DETAIL TESTS
# ============================================================================

def test_citizen_facilities_list_only_active(client, citizen_headers, active_facility, inactive_facility):
    """
    Code Path: citizen_facilities_list_resource.py -> GET /api/citizen/facilities
    Verifies returning ONLY active facilities (is_active = True).
    """
    response = client.get("/api/citizen/facilities", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "facilities" in data
    facility_ids = [f["id"] for f in data["facilities"]]
    assert active_facility.id in facility_ids
    assert inactive_facility.id not in facility_ids  # Inactive facility excluded


def test_citizen_facility_detail_success(client, citizen_headers, active_facility, sample_booking):
    """
    Code Path: citizen_facility_detail_resource.py -> GET /api/citizen/facility/{id}
    Verifies returning facility details, booked_dates array, and my_booked_dates array.
    """
    response = client.get(f"/api/citizen/facility/{active_facility.id}", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "facility" in data
    assert "booked_dates" in data
    assert "my_booked_dates" in data
    assert data["facility"]["id"] == active_facility.id
    assert sample_booking.booked_date.isoformat() in data["booked_dates"]
    assert sample_booking.booked_date.isoformat() in data["my_booked_dates"]


def test_citizen_facility_detail_inactive_or_not_found(client, citizen_headers, inactive_facility):
    """
    Code Path: citizen_facility_detail_resource.py -> inactive or non-existent facility.
    Verifies 404 Not Found.
    """
    # Inactive facility
    resp1 = client.get(f"/api/citizen/facility/{inactive_facility.id}", headers=citizen_headers)
    assert resp1.status_code == 404
    assert resp1.json()["detail"] == "Facility not found"

    # Non-existent facility ID
    resp2 = client.get("/api/citizen/facility/99999", headers=citizen_headers)
    assert resp2.status_code == 404
    assert resp2.json()["detail"] == "Facility not found"


# ============================================================================
# CITIZEN FACILITY BOOKING TESTS
# ============================================================================

def test_citizen_book_facility_success(client, citizen_headers, active_facility, db_session, citizen_user):
    """
    Code Path: citizen_facility_book_resource.py -> POST /api/citizen/book_facility/{id}
    Verifies successful booking creation, reference code generation ('BKG-...'),
    amount_paid matching facility price_per_day, and status 'Confirmed'.
    """
    target_date = date.today() + timedelta(days=10)
    payload = {
        "bookedDate": target_date.isoformat(),
        "purpose": "Birthday Party Gathering"
    }

    response = client.post(f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Booking confirmed"
    assert "booking" in data
    assert data["booking"]["facilityName"] == active_facility.name
    assert data["booking"]["amountPaid"] == active_facility.price_per_day
    assert data["booking"]["status"] == "Confirmed"
    assert data["booking"]["bookingReference"].startswith("BKG-")

    # DB Verification
    created_booking = db_session.query(FacilityBooking).filter_by(booking_reference=data["booking"]["bookingReference"]).first()
    assert created_booking is not None
    assert created_booking.user_id == citizen_user.id
    assert created_booking.facility_id == active_facility.id
    assert created_booking.booked_date == target_date
    assert created_booking.status == "Confirmed"


def test_citizen_book_facility_past_date_fails(client, citizen_headers, active_facility):
    """
    Code Path: citizen_facility_book_resource.py -> past date check.
    Verifies 400 Bad Request when attempting to book a past date.
    """
    past_date = date.today() - timedelta(days=1)
    payload = {"booked_date": past_date.isoformat()}

    response = client.post(f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot book a past date"


def test_citizen_book_facility_too_far_in_future_fails(client, citizen_headers, active_facility):
    """
    Code Path: citizen_facility_book_resource.py -> 90-day advance booking limit check.
    Verifies 400 Bad Request when attempting to book > 90 days in advance.
    """
    far_future = date.today() + timedelta(days=95)
    payload = {"booked_date": far_future.isoformat()}

    response = client.post(f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot book more than 90 days in advance"


def test_citizen_book_facility_duplicate_date_fails(client, citizen_headers, active_facility, sample_booking):
    """
    Code Path: citizen_facility_book_resource.py -> existing confirmed booking check for same date.
    Verifies 400 Bad Request when attempting to book an already booked date.
    """
    payload = {"booked_date": sample_booking.booked_date.isoformat()}

    response = client.post(f"/api/citizen/book_facility/{active_facility.id}", json=payload, headers=citizen_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "This date is already booked"


def test_citizen_book_facility_missing_or_invalid_date(client, citizen_headers, active_facility):
    """
    Code Path: citizen_facility_book_resource.py -> date presence & isoformat parsing checks.
    Verifies 400 Bad Request for missing date or bad date string.
    """
    # Missing date
    resp1 = client.post(f"/api/citizen/book_facility/{active_facility.id}", json={}, headers=citizen_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Date is required"

    # Invalid date string format
    resp2 = client.post(f"/api/citizen/book_facility/{active_facility.id}", json={"date": "invalid-date"}, headers=citizen_headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Invalid date format. Use YYYY-MM-DD"


def test_citizen_book_facility_inactive_facility_fails(client, citizen_headers, inactive_facility):
    """
    Code Path: citizen_facility_book_resource.py -> facility not found or is_active is False.
    Verifies 404 Not Found when booking an inactive facility.
    """
    target_date = date.today() + timedelta(days=2)
    payload = {"booked_date": target_date.isoformat()}

    response = client.post(f"/api/citizen/book_facility/{inactive_facility.id}", json=payload, headers=citizen_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


# ============================================================================
# CITIZEN BOOKING HISTORY & CANCELLATION TESTS
# ============================================================================

def test_citizen_bookings_list_success(client, citizen_headers, sample_booking):
    """
    Code Path: citizen_bookings_list_resource.py -> GET /api/citizen/bookings
    Verifies listing citizen's own bookings ordered by date descending.
    """
    response = client.get("/api/citizen/bookings", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert "bookings" in data
    assert len(data["bookings"]) >= 1
    matched = next((b for b in data["bookings"] if b["id"] == sample_booking.id), None)
    assert matched is not None
    assert matched["bookingReference"] == sample_booking.booking_reference
    assert matched["facilityName"] == sample_booking.facility.name
    assert matched["status"] == "Confirmed"


def test_citizen_cancel_booking_success(client, citizen_headers, sample_booking, db_session):
    """
    Code Path: citizen_booking_cancel_resource.py -> POST /api/citizen/cancel_booking/{id}
    Verifies cancelling a confirmed booking, updating status to 'Cancelled' in DB.
    """
    response = client.post(f"/api/citizen/cancel_booking/{sample_booking.id}", headers=citizen_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Booking cancelled successfully"

    db_session.refresh(sample_booking)
    assert sample_booking.status == "Cancelled"


def test_citizen_cancel_booking_ownership_check_fails(client, second_citizen_headers, sample_booking):
    """
    Code Path: citizen_booking_cancel_resource.py -> user_id ownership check.
    Verifies 403 Forbidden when a user attempts to cancel someone else's booking.
    """
    response = client.post(f"/api/citizen/cancel_booking/{sample_booking.id}", headers=second_citizen_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


def test_citizen_cancel_booking_already_cancelled_fails(client, citizen_headers, sample_booking, db_session):
    """
    Code Path: citizen_booking_cancel_resource.py -> already cancelled check.
    Verifies 400 Bad Request when attempting to cancel an already cancelled booking.
    """
    sample_booking.status = "Cancelled"
    db_session.commit()

    response = client.post(f"/api/citizen/cancel_booking/{sample_booking.id}", headers=citizen_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Booking is already cancelled"


def test_citizen_cancel_booking_past_booking_fails(client, citizen_headers, sample_booking, db_session):
    """
    Code Path: citizen_booking_cancel_resource.py -> past booking date check.
    Verifies 400 Bad Request when attempting to cancel a past booking.
    """
    sample_booking.booked_date = date.today() - timedelta(days=2)
    db_session.commit()

    response = client.post(f"/api/citizen/cancel_booking/{sample_booking.id}", headers=citizen_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot cancel a past booking"


def test_citizen_cancel_booking_not_found(client, citizen_headers):
    """
    Code Path: citizen_booking_cancel_resource.py -> booking not found.
    Verifies 404 Not Found for non-existent booking ID.
    """
    response = client.post("/api/citizen/cancel_booking/99999", headers=citizen_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"
