import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.middlewares.init_jwt import create_access_token
from application.helpers.models import User, Role, Department, Complaint, Facility, FacilityBooking, BillType, UtilityBill


@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def test_department(db_session: Session) -> Department:
    dept = Department(name="Public Works Department")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def citizen_user(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="citizen").first()
    user = User(
        email="cross.citizen@civicresolve.in",
        password=hash_password("CitizenPass123!"),
        name="Cross Citizen",
        role="citizen",
        phone="9876543210",
        address="123 Cross Lane",
        pincode="560001",
        is_active=True
    )
    if role not in user.roles:
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
def officer_user(db_session: Session, test_department: Department) -> User:
    role = db_session.query(Role).filter_by(name="field_officer").first()
    user = User(
        email="cross.officer@civicresolve.in",
        password=hash_password("OfficerPass123!"),
        name="Cross Officer",
        role="field_officer",
        department_id=test_department.id,
        badge_id="BADGE-CROSS-01",
        is_active=True
    )
    if role not in user.roles:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def officer_headers(officer_user: User) -> dict:
    token = create_access_token(officer_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def comm_user(db_session: Session) -> User:
    role = db_session.query(Role).filter_by(name="commissioner").first()
    user = User(
        email="cross.commissioner@civicresolve.in",
        password=hash_password("CommPass123!"),
        name="Cross Commissioner",
        role="commissioner",
        is_active=True
    )
    if role not in user.roles:
        user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def comm_headers(comm_user: User) -> dict:
    token = create_access_token(comm_user.id)
    return {"Authorization": f"Bearer {token}"}


def test_cross_flow_full_complaint_lifecycle_anonymous_to_resolution_tracking(client, db_session, officer_user, comm_headers, test_department):

    anon_resp = client.post("/api/complaint/anonymous", data={
        "title": "Severe Water Leakage on Main Street",
        "description": "Massive underground water pipe burst flooding road",
        "addressText": "Main Street Block C",
        "categoryId": test_department.id
    })
    assert anon_resp.status_code == 200
    token = anon_resp.json()["trackingToken"]
    complaint_id = anon_resp.json()["complaintId"]

    complaint = db_session.get(Complaint, complaint_id)
    complaint.severity = "Critical"
    db_session.commit()

    assign_resp = client.put(f"/api/commissioner/assign/{complaint_id}", json={"officerId": officer_user.id}, headers=comm_headers)
    assert assign_resp.status_code == 200

    off_headers = {"Authorization": f"Bearer {create_access_token(officer_user.id)}"}
    ticket_resp = client.get(f"/api/officer/ticket/{complaint_id}", headers=off_headers)
    assert ticket_resp.status_code == 200
    assert ticket_resp.json()["complaint"]["status"] == "Assigned"

    statuses = ["En Route", "On Site", "In Progress"]
    for s in statuses:
        st_resp = client.put(f"/api/officer/ticket/{complaint_id}/status", json={"status": s, "note": f"Moving to {s}"}, headers=off_headers)
        assert st_resp.status_code == 200

    res_resp = client.post(
        f"/api/officer/ticket/{complaint_id}/resolve",
        data={"resolution_note": "Pipe repaired and pressure tested successfully"},
        headers=off_headers
    )
    assert res_resp.status_code == 200
    assert res_resp.json()["message"] == "Ticket resolved successfully"

    track_resp = client.get(f"/api/complaint/track/{token}")
    assert track_resp.status_code == 200
    track_data = track_resp.json()
    assert track_data["complaint"]["status"] == "Resolved"
    assert track_data["complaint"]["resolutionNote"] == "Pipe repaired and pressure tested successfully"
    assert track_data["complaint"]["resolutionPhotos"] == []

    timeline_statuses = [u["newStatus"] for u in track_data["updates"]]
    assert "Assigned" in timeline_statuses
    assert "En Route" in timeline_statuses
    assert "On Site" in timeline_statuses
    assert "In Progress" in timeline_statuses
    assert "Resolved" in timeline_statuses


def test_cross_flow_bill_issuance_payment_and_commissioner_reconciliation(client, db_session, citizen_user, citizen_headers, comm_headers):

    bt_resp = client.post("/api/commissioner/bill_type", json={"name": "Property Tax Q3"}, headers=comm_headers)
    assert bt_resp.status_code == 200
    bill_type_name = bt_resp.json()["name"]

    due_date_str = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    bill_resp = client.post("/api/commissioner/bill", json={
        "userId": citizen_user.id,
        "billType": bill_type_name,
        "amount": 2500.50,
        "dueDate": due_date_str
    }, headers=comm_headers)
    assert bill_resp.status_code == 200
    assert "issued to" in bill_resp.json()["message"]

    issued_bill = db_session.query(UtilityBill).filter(UtilityBill.user_id==citizen_user.id, UtilityBill._bill_type==bill_type_name).first()
    assert issued_bill is not None
    bill_id = issued_bill.id

    cit_bills_resp = client.get("/api/citizen/bills?status=Pending", headers=citizen_headers)
    assert cit_bills_resp.status_code == 200
    pending_ids = [b["id"] for b in cit_bills_resp.json()["bills"]]
    assert bill_id in pending_ids

    pay_resp = client.post(f"/api/citizen/pay_bill/{bill_id}", headers=citizen_headers)
    assert pay_resp.status_code == 200
    assert pay_resp.json()["message"] == "Payment successful"

    comm_bills_resp = client.get("/api/commissioner/bills", headers=comm_headers)
    assert comm_bills_resp.status_code == 200
    paid_bill = next((b for b in comm_bills_resp.json()["bills"] if b["id"] == bill_id), None)
    assert paid_bill is not None
    assert paid_bill["status"] == "Paid"
    assert paid_bill["paidAt"] is not None


def test_cross_flow_facility_lifecycle_commissioner_create_citizen_book_and_list(client, db_session, citizen_user, citizen_headers, comm_headers):

    fac_resp = client.post("/api/commissioner/facility", json={
        "name": "Community Badminton Court",
        "facilityType": "Sports",
        "description": "Indoor wooden floor badminton court",
        "address": "Sector 9 Sports Complex, Main Road",
        "pincode": "560001",
        "pricePerDay": 150.00
    }, headers=comm_headers)
    assert fac_resp.status_code == 200
    assert "created successfully" in fac_resp.json()["message"]

    facility = db_session.query(Facility).filter_by(name="Community Badminton Court").first()
    assert facility is not None
    facility_id = facility.id

    list_resp = client.get("/api/citizen/facilities", headers=citizen_headers)
    assert list_resp.status_code == 200
    assert any(f["id"] == facility_id for f in list_resp.json()["facilities"])

    detail_resp = client.get(f"/api/citizen/facility/{facility_id}", headers=citizen_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["facility"]["name"] == "Community Badminton Court"

    booking_date_str = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    book_resp = client.post(f"/api/citizen/book_facility/{facility_id}", json={
        "booked_date": booking_date_str,
        "start_time": "14:00",
        "end_time": "16:00"
    }, headers=citizen_headers)
    assert book_resp.status_code == 200
    booking_ref = book_resp.json()["booking"]["bookingReference"]

    my_bookings = client.get("/api/citizen/bookings", headers=citizen_headers)
    assert my_bookings.status_code == 200
    assert any(b["bookingReference"] == booking_ref for b in my_bookings.json()["bookings"])

    upd_resp = client.put(f"/api/commissioner/facility/{facility_id}", json={
        "pricePerDay": 180.00,
        "description": "Air Conditioned indoor wooden floor badminton court"
    }, headers=comm_headers)
    assert upd_resp.status_code == 200

    updated_detail = client.get(f"/api/citizen/facility/{facility_id}", headers=citizen_headers)
    assert updated_detail.status_code == 200
    assert updated_detail.json()["facility"]["pricePerDay"] == 180.00
    assert "Air Conditioned" in updated_detail.json()["facility"]["description"]


def test_token_refresh_middleware_emits_header(client, citizen_headers):
    response = client.get("/api/citizen/dash", headers=citizen_headers)
    assert response.status_code == 200
    assert "X-Refresh-Token" in response.headers


def test_officer_cannot_access_or_modify_unassigned_ticket(client, db_session, officer_user, officer_headers, test_department):
    role = db_session.query(Role).filter_by(name="field_officer").first()
    other_officer = User(
        email="officer.other@civicresolve.in",
        password=hash_password("OfficerPassword123!"),
        name="Officer Other",
        role="field_officer",
        department_id=test_department.id,
        badge_id="BADGE-OTHER-99",
        is_active=True
    )
    if role not in other_officer.roles:
        other_officer.roles.append(role)
    db_session.add(other_officer)
    db_session.commit()

    ticket = Complaint(
        token="CRA-UNASSIGNED01",
        title="Pothole Damage",
        description="Pothole near market",
        assigned_officer_id=other_officer.id,
        assigned_officer_name=other_officer.name,
        status="Assigned",
        severity="Critical"
    )
    db_session.add(ticket)
    db_session.commit()

    assert client.get(f"/api/officer/ticket/{ticket.id}", headers=officer_headers).status_code == 403

    assert client.put(f"/api/officer/ticket/{ticket.id}/status", json={"status": "In Progress"}, headers=officer_headers).status_code == 403

    assert client.post(f"/api/officer/ticket/{ticket.id}/resolve", json={"resolution_note": "Unallowed resolve"}, headers=officer_headers).status_code == 403


def test_officer_invalid_status_transition_rejection(client, db_session, officer_user, officer_headers):
    ticket = Complaint(
        token="CRA-STATUSINVALID01",
        title="Water Leakage",
        description="Leaking pipe",
        assigned_officer_id=officer_user.id,
        assigned_officer_name=officer_user.name,
        status="Assigned",
        severity="Critical"
    )
    db_session.add(ticket)
    db_session.commit()

    resp1 = client.put(f"/api/officer/ticket/{ticket.id}/status", json={"status": "NonExistentStatus"}, headers=officer_headers)
    assert resp1.status_code == 400

    resp2 = client.put(f"/api/officer/ticket/{ticket.id}/status", json={}, headers=officer_headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "New status is required"


def test_commissioner_category_lifecycle(client, db_session, comm_headers):

    create_resp = client.post("/api/commissioner/category", json={"name": "Parks & Recreation"}, headers=comm_headers)
    assert create_resp.status_code == 200
    assert "created successfully" in create_resp.json()["message"]

    cat = db_session.query(Department).filter_by(name="Parks & Recreation").first()
    assert cat is not None
    cat_id = cat.id

    dup_resp = client.post("/api/commissioner/category", json={"name": "Parks & Recreation"}, headers=comm_headers)
    assert dup_resp.status_code == 409
    assert dup_resp.json()["detail"] == "Category already exists"

    list_resp = client.get("/api/commissioner/categories", headers=comm_headers)
    assert list_resp.status_code == 200
    categories = list_resp.json()["categories"]
    assert any(c["id"] == cat_id for c in categories)

    del_resp = client.delete(f"/api/commissioner/category/{cat_id}", headers=comm_headers)
    assert del_resp.status_code == 200

    list_resp2 = client.get("/api/commissioner/categories", headers=comm_headers)
    categories2 = list_resp2.json()["categories"]
    assert not any(c["id"] == cat_id for c in categories2)


def test_citizen_and_commissioner_search_behavior(client, db_session, citizen_headers, comm_headers):

    fac = Facility(
        name="City Central Park",
        description="Public park and recreation area",
        address="123 Park Avenue",
        pincode="560001",
        facility_type="Park",
        price_per_day=500.0,
        is_active=True
    )
    db_session.add(fac)

    cmp = Complaint(
        token="CRA-SEARCHTEST99",
        title="Broken Park Bench",
        description="Vandalized park bench near main gazebo",
        location="Gazebo Garden",
        status="Submitted",
        severity="Normal"
    )
    db_session.add(cmp)
    db_session.commit()

    s1 = client.post("/api/citizen/search", json={"query": "Central Park"}, headers=citizen_headers)
    assert s1.status_code == 200
    assert len(s1.json()["facilities"]) == 1

    s2 = client.post("/api/citizen/search", json={"query": ""}, headers=citizen_headers)
    assert s2.status_code == 200
    assert len(s2.json()["facilities"]) == 0

    s3 = client.post("/api/commissioner/search", json={"query": "Park Bench"}, headers=comm_headers)
    assert s3.status_code == 200
    res = s3.json()
    assert "complaints" in res
    assert any(c["id"] == cmp.id for c in res["complaints"])
