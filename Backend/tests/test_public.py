"""
Public & Anonymous Module Integration Tests.

Endpoints Tested:
- POST /api/complaint/anonymous
- GET /api/complaint/track/{token}
"""

import io
import pytest
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role, Department, Complaint, ComplaintUpdate
from application.middlewares.init_jwt import create_access_token


# ============================================================================
# LOCAL FIXTURES (PUBLIC DOMAIN SPECIFIC)
# ============================================================================

@pytest.fixture(autouse=True)
def seed_roles(db_session: Session):
    """Ensures default roles exist in db_session."""
    for role_name in ["citizen", "field_officer", "commissioner"]:
        if not db_session.query(Role).filter_by(name=role_name).first():
            db_session.add(Role(name=role_name))
    db_session.commit()


@pytest.fixture
def citizen_headers(db_session: Session) -> dict:
    """Returns JWT Authorization headers for a citizen user (for cross-flow verification)."""
    user = User(
        email="public.citizen@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Public Flow Citizen",
        role="citizen",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_department(db_session: Session) -> Department:
    """Creates a sample Department entity in the test database."""
    dept = Department(name="Public Works & Utilities")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


# ============================================================================
# ANONYMOUS COMPLAINT CREATION TESTS (POST /api/complaint/anonymous)
# ============================================================================

def test_anonymous_complaint_creation_success_minimal(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> POST /api/complaint/anonymous
    Verifies creating an anonymous complaint with minimal required fields (title & description),
    no auth token required, tracking_token generation, and DB state verification.
    """
    payload = {
        "title": "Water Leakage on Main Street",
        "description": "Clean drinking water leaking from underground pipe for 2 days"
    }

    response = client.post("/api/complaint/anonymous", data=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Complaint filed successfully"
    assert "tracking_token" in data
    assert data["tracking_token"].startswith("CRA-")

    # DB Persistence Verification — description undergoes AI sanitization before storing
    token = data["tracking_token"]
    complaint = db_session.query(Complaint).filter_by(token=token).first()
    assert complaint is not None
    assert complaint.title == "Water Leakage on Main Street"
    assert complaint.description is not None and len(complaint.description) >= 10
    desc_lower = complaint.description.lower()
    assert any(term in desc_lower for term in ["water", "pipe", "leak"])
    assert complaint.status == "Submitted"
    assert complaint.severity == "Normal"
    assert complaint.department_id is None

    # Initial ComplaintUpdate verification
    update = db_session.query(ComplaintUpdate).filter_by(complaint_id=complaint.id).first()
    assert update is not None
    assert update.new_status == "Submitted"
    assert update.note == "Complaint submitted anonymously"


def test_anonymous_complaint_creation_with_valid_department_and_location(client, sample_department, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> category_id and address_text parameters.
    Verifies saving department_id, location, and department link in database.
    """
    payload = {
        "title": "Pothole near Central Bus Stop",
        "description": "Deep pothole causing traffic slowdown near bus terminal",
        "category_id": sample_department.id,
        "address_text": "Central Bus Stand, Sector 4"
    }

    response = client.post("/api/complaint/anonymous", data=payload)
    assert response.status_code == 200

    token = response.json()["tracking_token"]
    complaint = db_session.query(Complaint).filter_by(token=token).first()
    assert complaint is not None
    assert complaint.department_id == sample_department.id
    assert complaint.location == "Central Bus Stand, Sector 4"


def test_anonymous_complaint_title_validation_failure(client):
    """
    Code Path: anonymous_complaint_resource.py -> validate_title check.
    Verifies 400 Bad Request for short or empty title.
    """
    payload = {
        "title": "Bad",
        "description": "Valid description with sufficient length for testing"
    }

    response = client.post("/api/complaint/anonymous", data=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Title must be at least 5 characters long"


def test_anonymous_complaint_description_validation_failure(client):
    """
    Code Path: anonymous_complaint_resource.py -> validate_description check.
    Verifies 400 Bad Request for short or empty description.
    """
    payload = {
        "title": "Valid Long Title Here",
        "description": "Too short"
    }

    response = client.post("/api/complaint/anonymous", data=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Description must be at least 10 characters long"


def test_anonymous_complaint_invalid_department(client):
    """
    Code Path: anonymous_complaint_resource.py -> category_id existence check.
    Verifies 400 Bad Request for non-existent category_id.
    """
    payload = {
        "title": "Valid Long Title Here",
        "description": "Valid description with sufficient length for testing",
        "category_id": 99999
    }

    response = client.post("/api/complaint/anonymous", data=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid category"


def test_anonymous_complaint_file_upload_success(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> photo upload handling.
    Verifies uploading valid image file (.jpg) and populating submitted_photo URL.
    """
    payload = {
        "title": "Broken Streetlight on 5th Cross",
        "description": "Streetlight bulb broken and hanging dangerously"
    }
    file_data = {
        "photo": ("test_evidence.jpg", io.BytesIO(b"fake-image-bytes"), "image/jpeg")
    }

    response = client.post("/api/complaint/anonymous", data=payload, files=file_data)
    assert response.status_code == 200

    token = response.json()["tracking_token"]
    complaint = db_session.query(Complaint).filter_by(token=token).first()
    assert complaint is not None
    assert complaint.submitted_photo is not None
    assert complaint.submitted_photo.startswith("/uploads/complaints/")


def test_anonymous_complaint_invalid_file_extension(client):
    """
    Code Path: anonymous_complaint_resource.py -> file extension validation.
    Verifies 400 Bad Request for unsupported file extension (.txt).
    """
    payload = {
        "title": "Broken Streetlight on 5th Cross",
        "description": "Streetlight bulb broken and hanging dangerously"
    }
    file_data = {
        "photo": ("invalid.txt", io.BytesIO(b"text-content"), "text/plain")
    }

    response = client.post("/api/complaint/anonymous", data=payload, files=file_data)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_anonymous_complaint_invalid_mime_type(client):
    """
    Code Path: anonymous_complaint_resource.py -> MIME type validation.
    Verifies 400 Bad Request when MIME type is not image/png or image/jpeg.
    """
    payload = {
        "title": "Broken Streetlight on 5th Cross",
        "description": "Streetlight bulb broken and hanging dangerously"
    }
    file_data = {
        "photo": ("fake.jpg", io.BytesIO(b"text-content"), "application/pdf")
    }

    response = client.post("/api/complaint/anonymous", data=payload, files=file_data)
    assert response.status_code == 400
    assert "Invalid MIME type" in response.json()["detail"]


# ============================================================================
# PUBLIC COMPLAINT TRACKING TESTS (GET /api/complaint/track/{token})
# ============================================================================

def test_public_track_complaint_success(client, sample_department, db_session):
    """
    Code Path: track_complaint_resource.py -> GET /api/complaint/track/{token}
    Verifies tracking a complaint by token without authentication, returning complaint
    fields and updates audit trail array.
    """
    complaint = Complaint(
        token="CRA-TRACK01",
        title="Overflowing Dumpster in Market",
        description="Market waste overflowing onto main road",
        location="Vegetable Market Gate 1",
        status="Submitted",
        severity="Normal",
        department_id=sample_department.id
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        old_status="New",
        new_status="Submitted",
        note="Submitted publicly"
    )
    db_session.add(update)
    db_session.commit()

    response = client.get(f"/api/complaint/track/{complaint.token}")
    assert response.status_code == 200

    data = response.json()
    assert "complaint" in data
    assert "updates" in data
    c_data = data["complaint"]
    assert c_data["id"] == complaint.id
    assert c_data["token"] == "CRA-TRACK01"
    assert c_data["title"] == "Overflowing Dumpster in Market"
    assert c_data["status"] == "Submitted"
    assert c_data["severity"] == "Normal"
    assert c_data["category"] == sample_department.name
    assert len(data["updates"]) >= 1


def test_public_track_complaint_not_found(client):
    """
    Code Path: track_complaint_resource.py -> non-existent token lookup.
    Verifies 404 Not Found for invalid token string.
    """
    response = client.get("/api/complaint/track/CRA-NONEXISTENT")
    assert response.status_code == 404
    assert response.json()["detail"] == "Complaint not found"


# ============================================================================
# CROSS-FLOW REGRESSION & CONSISTENCY TESTS
# ============================================================================

def test_cross_flow_anonymous_creation_then_public_tracking(client, db_session):
    """
    Verifies end-to-end flow: creating an anonymous complaint, retrieving tracking token,
    and successfully tracking it publicly without authentication.
    """
    create_payload = {
        "title": "Open Manhole Cover near School",
        "description": "Hazardous open manhole cover right next to primary school gate"
    }

    create_resp = client.post("/api/complaint/anonymous", data=create_payload)
    assert create_resp.status_code == 200
    token = create_resp.json()["tracking_token"]

    # Public unauthenticated tracking call
    track_resp = client.get(f"/api/complaint/track/{token}")
    assert track_resp.status_code == 200

    track_data = track_resp.json()["complaint"]
    assert track_data["token"] == token
    assert track_data["title"] == "Open Manhole Cover near School"
    assert track_data["status"] == "Submitted"
    assert track_data["severity"] == "Normal"


def test_cross_flow_anonymous_complaint_retrievable_in_public_tracking(client, db_session):
    """
    Verifies Phase 9 architecture decision: Anonymously created civic complaints are retrievable
    via GET /api/complaint/track/{token}.
    """
    create_payload = {
        "title": "Clogged Storm Drain before Monsoon",
        "description": "Drain filled with plastic bottles causing waterlogging risk"
    }
    create_resp = client.post("/api/complaint/anonymous", data=create_payload)
    assert create_resp.status_code == 200
    token = create_resp.json()["tracking_token"]

    # Public tracking call
    track_resp = client.get(f"/api/complaint/track/{token}")
    assert track_resp.status_code == 200

    data = track_resp.json()
    assert "complaint" in data
    c_data = data["complaint"]
    assert c_data["token"] == token
    assert c_data["severity"] == "Normal"
    assert c_data["title"] == "Clogged Storm Drain before Monsoon"
