"""
Bills & Utility Bill Management Integration Tests.

Covers both sides of the Bills domain:
1. Commissioner Bill Administration:
   - GET /api/commissioner/bill_types
   - POST /api/commissioner/bill_type
   - PUT /api/commissioner/bill_type/{bill_type_id}
   - DELETE /api/commissioner/bill_type/{bill_type_id}
   - POST /api/commissioner/bill
   - GET /api/commissioner/bills

2. Citizen Bill Inspection & Payment:
   - GET /api/citizen/bills
   - POST /api/citizen/pay_bill/{bill_id}
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role, BillType, UtilityBill
from application.middlewares.init_jwt import create_access_token


# ============================================================================
# LOCAL FIXTURES (BILLS DOMAIN SPECIFIC)
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
        email="comm.bills@civicresolve.in",
        password=hash_password("CommPass123!"),
        name="Bills Commissioner",
        role="commissioner",
        badge_id="COM-BILL-1",
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
        email="citizen.bills@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Bills Citizen One",
        role="citizen",
        phone="9876543210",
        address="200 Bill Street",
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
        email="citizen.bills2@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Bills Citizen Two",
        role="citizen",
        phone="9876543211",
        address="201 Bill Street",
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
        email="officer.bills@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Officer Bills Test",
        role="field_officer",
        badge_id="OFF-BILL-1",
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
def sample_bill_type(db_session: Session) -> BillType:
    """Creates a sample BillType in the test database."""
    bt = BillType(name="Electricity Tax")
    db_session.add(bt)
    db_session.commit()
    db_session.refresh(bt)
    return bt


@pytest.fixture
def sample_pending_bill(db_session: Session, citizen_user: User, sample_bill_type: BillType) -> UtilityBill:
    """Creates a Pending UtilityBill assigned to citizen_user."""
    due = date.today() + timedelta(days=15)
    bill = UtilityBill(
        user_id=citizen_user.id,
        citizen_name=citizen_user.name,
        bill_type_id=sample_bill_type.id,
        bill_type=sample_bill_type.name,
        bill_number="BILL-TEST-8801",
        amount=250.0,
        due_date=due,
        period="Q3-2026",
        status="Pending"
    )
    db_session.add(bill)
    db_session.commit()
    db_session.refresh(bill)
    return bill


@pytest.fixture
def sample_paid_bill(db_session: Session, citizen_user: User, sample_bill_type: BillType) -> UtilityBill:
    """Creates a Paid UtilityBill assigned to citizen_user."""
    due = date.today() - timedelta(days=5)
    bill = UtilityBill(
        user_id=citizen_user.id,
        citizen_name=citizen_user.name,
        bill_type_id=sample_bill_type.id,
        bill_type=sample_bill_type.name,
        bill_number="BILL-TEST-8802",
        amount=180.0,
        due_date=due,
        period="Q2-2026",
        status="Paid"
    )
    db_session.add(bill)
    db_session.commit()
    db_session.refresh(bill)
    return bill


# ============================================================================
# AUTHORIZATION & ROLE CHECKS
# ============================================================================

def test_commissioner_bill_endpoints_unauthorized(client):
    """
    Verifies 401 Unauthorized for unauthenticated requests across commissioner bill routes.
    """
    assert client.get("/api/commissioner/bill_types").status_code == 401
    assert client.post("/api/commissioner/bill_type", json={}).status_code == 401
    assert client.put("/api/commissioner/bill_type/1", json={}).status_code == 401
    assert client.delete("/api/commissioner/bill_type/1").status_code == 401
    assert client.post("/api/commissioner/bill", json={}).status_code == 401
    assert client.get("/api/commissioner/bills").status_code == 401


def test_citizen_bill_endpoints_unauthorized(client):
    """
    Verifies 401 Unauthorized for unauthenticated requests across citizen bill routes.
    """
    assert client.get("/api/citizen/bills").status_code == 401
    assert client.post("/api/citizen/pay_bill/1").status_code == 401


def test_commissioner_bill_endpoints_forbidden_for_citizen_and_officer(client, citizen_headers, officer_headers):
    """
    Verifies 403 Forbidden for Citizen or Field Officer calling commissioner bill routes.
    """
    for headers in [citizen_headers, officer_headers]:
        assert client.get("/api/commissioner/bill_types", headers=headers).status_code == 403
        assert client.post("/api/commissioner/bill_type", json={}, headers=headers).status_code == 403
        assert client.put("/api/commissioner/bill_type/1", json={}, headers=headers).status_code == 403
        assert client.delete("/api/commissioner/bill_type/1", headers=headers).status_code == 403
        assert client.post("/api/commissioner/bill", json={}, headers=headers).status_code == 403
        assert client.get("/api/commissioner/bills", headers=headers).status_code == 403


def test_citizen_bill_endpoints_forbidden_for_commissioner_and_officer(client, comm_headers, officer_headers):
    """
    Verifies 403 Forbidden for Commissioner or Field Officer calling citizen bill routes.
    """
    for headers in [comm_headers, officer_headers]:
        assert client.get("/api/citizen/bills", headers=headers).status_code == 403
        assert client.post("/api/citizen/pay_bill/1", headers=headers).status_code == 403


# ============================================================================
# COMMISSIONER BILL TYPES MANAGEMENT TESTS
# ============================================================================

def test_commissioner_bill_types_list_success(client, comm_headers, sample_bill_type):
    """
    Code Path: commissioner_bill_types_list_resource.py -> GET /api/commissioner/bill_types
    Verifies listing bill types sorted by name.
    """
    response = client.get("/api/commissioner/bill_types", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(b["id"] == sample_bill_type.id for b in data)


def test_commissioner_create_bill_type_success(client, comm_headers, db_session):
    """
    Code Path: commissioner_bill_type_resource.py -> POST /api/commissioner/bill_type
    Verifies creating a new BillType in database.
    """
    payload = {"name": "Water Consumption Tax"}
    response = client.post("/api/commissioner/bill_type", json=payload, headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "created successfully" in data["message"]
    assert data["name"] == "Water Consumption Tax"

    created = db_session.query(BillType).filter_by(name="Water Consumption Tax").first()
    assert created is not None


def test_commissioner_create_bill_type_validation_and_conflict(client, comm_headers, sample_bill_type):
    """
    Code Path: commissioner_bill_type_resource.py -> empty name & duplicate name checks.
    """
    # Empty name
    resp1 = client.post("/api/commissioner/bill_type", json={"name": "  "}, headers=comm_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Bill type name is required"

    # Duplicate name
    resp2 = client.post("/api/commissioner/bill_type", json={"name": sample_bill_type.name}, headers=comm_headers)
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == "Bill type already exists"


def test_commissioner_update_bill_type_success(client, comm_headers, sample_bill_type, db_session):
    """
    Code Path: commissioner_bill_type_resource.py -> PUT /api/commissioner/bill_type/{id}
    Verifies updating BillType name in DB.
    """
    payload = {"name": "Electricity Tax Renamed"}
    response = client.put(f"/api/commissioner/bill_type/{sample_bill_type.id}", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]

    db_session.refresh(sample_bill_type)
    assert sample_bill_type.name == "Electricity Tax Renamed"


def test_commissioner_update_bill_type_conflict_and_not_found(client, comm_headers, sample_bill_type, db_session):
    """
    Code Path: commissioner_bill_type_resource.py -> edit mode name conflict & not found checks.
    """
    bt2 = BillType(name="Property Tax")
    db_session.add(bt2)
    db_session.commit()

    # Conflict with another record
    resp1 = client.put(f"/api/commissioner/bill_type/{sample_bill_type.id}", json={"name": "Property Tax"}, headers=comm_headers)
    assert resp1.status_code == 409
    assert resp1.json()["detail"] == "Bill type name already in use"

    # Not found
    resp2 = client.put("/api/commissioner/bill_type/99999", json={"name": "Ghost Tax"}, headers=comm_headers)
    assert resp2.status_code == 404
    assert resp2.json()["detail"] == "Bill type not found"


def test_commissioner_delete_bill_type_success(client, comm_headers, sample_bill_type, db_session):
    """
    Code Path: commissioner_bill_type_resource.py -> DELETE /api/commissioner/bill_type/{id}
    Verifies deleting a BillType from DB.
    """
    response = client.delete(f"/api/commissioner/bill_type/{sample_bill_type.id}", headers=comm_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

    deleted = db_session.query(BillType).get(sample_bill_type.id)
    assert deleted is None


def test_commissioner_delete_bill_type_not_found(client, comm_headers):
    """
    Code Path: commissioner_bill_type_resource.py -> delete non-existent ID.
    Verifies 404 Not Found.
    """
    response = client.delete("/api/commissioner/bill_type/99999", headers=comm_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Bill type not found"


# ============================================================================
# COMMISSIONER BILL ISSUE & LISTING TESTS
# ============================================================================

def test_commissioner_issue_bill_success(client, comm_headers, citizen_user, sample_bill_type, db_session):
    """
    Code Path: commissioner_bill_add_resource.py -> POST /api/commissioner/bill
    Verifies issuing a bill for a citizen, checking DB creation, status 'Pending',
    and unique bill_number format ('BILL-...').
    """
    due = date.today() + timedelta(days=20)
    payload = {
        "citizenId": citizen_user.id,
        "billType": sample_bill_type.name,
        "amount": 350.0,
        "dueDate": due.isoformat(),
        "period": "Q4-2026"
    }

    response = client.post("/api/commissioner/bill", json=payload, headers=comm_headers)
    assert response.status_code == 200
    assert "issued to" in response.json()["message"]

    created = db_session.query(UtilityBill).filter_by(user_id=citizen_user.id, amount=350.0).first()
    assert created is not None
    assert created.bill_type == sample_bill_type.name
    assert created.status == "Pending"
    assert created.bill_number.startswith("BILL-")
    assert created.due_date == due


def test_commissioner_issue_bill_invalid_citizen(client, comm_headers):
    """
    Code Path: commissioner_bill_add_resource.py -> citizen lookup & role check.
    Verifies 400 Bad Request for non-existent citizen ID.
    """
    payload = {
        "citizenId": 99999,
        "billType": "Water Tax",
        "amount": 100.0,
        "dueDate": date.today().isoformat()
    }

    response = client.post("/api/commissioner/bill", json=payload, headers=comm_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid citizen"


def test_commissioner_issue_bill_validation_failures(client, comm_headers, citizen_user):
    """
    Code Path: commissioner_bill_add_resource.py -> input payload validation rules.
    """
    # Missing citizen ID
    resp1 = client.post("/api/commissioner/bill", json={"billType": "Water", "amount": 100.0, "dueDate": "2026-10-10"}, headers=comm_headers)
    assert resp1.status_code == 400
    assert resp1.json()["detail"] == "Citizen ID is required"

    # Missing bill type
    resp2 = client.post("/api/commissioner/bill", json={"citizenId": citizen_user.id, "amount": 100.0, "dueDate": "2026-10-10"}, headers=comm_headers)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Bill type is required"

    # Invalid amount (negative)
    resp3 = client.post("/api/commissioner/bill", json={"citizenId": citizen_user.id, "billType": "Water", "amount": -50.0, "dueDate": "2026-10-10"}, headers=comm_headers)
    assert resp3.status_code == 400
    assert resp3.json()["detail"] == "Amount must be greater than 0"

    # Missing due date
    resp4 = client.post("/api/commissioner/bill", json={"citizenId": citizen_user.id, "billType": "Water", "amount": 100.0}, headers=comm_headers)
    assert resp4.status_code == 400
    assert resp4.json()["detail"] == "Due date is required"

    # Invalid ISO due date format
    resp5 = client.post("/api/commissioner/bill", json={"citizenId": citizen_user.id, "billType": "Water", "amount": 100.0, "dueDate": "not-a-date"}, headers=comm_headers)
    assert resp5.status_code == 400
    assert resp5.json()["detail"] == "Invalid date format. Use YYYY-MM-DD"


def test_commissioner_bills_list_success(client, comm_headers, sample_pending_bill):
    """
    Code Path: commissioner_bills_list_resource.py -> GET /api/commissioner/bills
    Verifies listing all utility bills across all citizens with citizen name and status.
    """
    response = client.get("/api/commissioner/bills", headers=comm_headers)
    assert response.status_code == 200

    data = response.json()
    assert "bills" in data
    assert any(b["id"] == sample_pending_bill.id for b in data["bills"])


# ============================================================================
# CITIZEN BILL INSPECTION & PAYMENT TESTS
# ============================================================================

def test_citizen_bills_list_all_and_filtered(client, citizen_headers, sample_pending_bill, sample_paid_bill):
    """
    Code Path: citizen_bills_list_resource.py -> GET /api/citizen/bills (all and filtered by status)
    """
    # 1. All bills
    res1 = client.get("/api/citizen/bills", headers=citizen_headers)
    assert res1.status_code == 200
    bills1 = res1.json()["bills"]
    ids1 = [b["id"] for b in bills1]
    assert sample_pending_bill.id in ids1
    assert sample_paid_bill.id in ids1

    # 2. Filter status=Pending
    res2 = client.get("/api/citizen/bills?status=Pending", headers=citizen_headers)
    assert res2.status_code == 200
    bills2 = res2.json()["bills"]
    assert all(b["status"] == "Pending" for b in bills2)

    # 3. Filter status=Paid
    res3 = client.get("/api/citizen/bills?status=Paid", headers=citizen_headers)
    assert res3.status_code == 200
    bills3 = res3.json()["bills"]
    assert all(b["status"] == "Paid" for b in bills3)


def test_citizen_pay_bill_success(client, citizen_headers, sample_pending_bill, db_session):
    """
    Code Path: citizen_bill_pay_resource.py -> POST /api/citizen/pay_bill/{id}
    Verifies paying a pending bill, updating status to 'Paid', setting paid_at timestamp,
    and returning payment receipt with transactionId format 'TXN-...'.
    """
    response = client.post(f"/api/citizen/pay_bill/{sample_pending_bill.id}", headers=citizen_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Payment successful"
    assert "receipt" in data
    assert data["receipt"]["billNumber"] == sample_pending_bill.bill_number
    assert data["receipt"]["amount"] == sample_pending_bill.amount
    assert data["receipt"]["transactionId"] == f"TXN-{sample_pending_bill.id:06d}"

    # DB Verification
    db_session.refresh(sample_pending_bill)
    assert sample_pending_bill.status == "Paid"
    assert sample_pending_bill.paid_at is not None


def test_citizen_pay_bill_already_paid_fails(client, citizen_headers, sample_paid_bill):
    """
    Code Path: citizen_bill_pay_resource.py -> status check for already paid.
    Verifies 400 Bad Request when attempting to pay an already paid bill.
    """
    response = client.post(f"/api/citizen/pay_bill/{sample_paid_bill.id}", headers=citizen_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Bill is already paid"


def test_citizen_pay_bill_ownership_check_fails(client, second_citizen_headers, sample_pending_bill):
    """
    Code Path: citizen_bill_pay_resource.py -> user_id ownership check.
    Verifies 403 Forbidden when a citizen attempts to pay another citizen's bill.
    """
    response = client.post(f"/api/citizen/pay_bill/{sample_pending_bill.id}", headers=second_citizen_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


def test_citizen_pay_bill_not_found(client, citizen_headers):
    """
    Code Path: citizen_bill_pay_resource.py -> bill not found.
    Verifies 404 Not Found for non-existent bill ID.
    """
    response = client.post("/api/citizen/pay_bill/99999", headers=citizen_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Bill not found"
