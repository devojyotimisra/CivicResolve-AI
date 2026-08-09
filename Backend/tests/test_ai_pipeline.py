"""
AI Pipeline Integration & Unit Tests.

Covers the complete 5-stage AI pipeline in POST /api/complaint/anonymous:
1. Spam Detection (detect_spam)
2. Language Translation (translate_text)
3. Content Sanitization (sanitize_complaint)
4. Multimodal Auto-Routing & Least-Loaded Officer Dispatch (auto_route_complaint)
5. Semantic Duplicate Detection & Severe/Critical Escalation (find_duplicate_complaints)
6. Duplicate Photo Handling
7. Graceful Fallback Handling on AI Failures
8. JSON Response Parsing Helper (_parse_json_response)
9. Function Invocation Parameter Verification
"""

import io
import os
import uuid
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from application.extensions.security_extn import hash_password
from application.helpers.models import User, Role, Department, Complaint, IST
from application.helpers.ai_service import _parse_json_response


# ============================================================================
# LOCAL FIXTURES FOR AI TESTING
# ============================================================================

@pytest.fixture
def ai_dept(db_session: Session) -> Department:
    """Creates a sample department for AI auto-routing tests."""
    dept = Department(name="Water Supply & Sewage")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def secondary_dept(db_session: Session) -> Department:
    """Creates a secondary department for AI auto-routing tests."""
    dept = Department(name="Roads & Traffic")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def officer_low_load(db_session: Session, ai_dept: Department) -> User:
    """Field Officer in ai_dept with 0 active tickets."""
    role = db_session.query(Role).filter_by(name="field_officer").first()
    if not role:
        role = Role(name="field_officer")
        db_session.add(role)

    officer = User(
        email="officer.low@civicresolve.in",
        password=hash_password("OfficerPass123!"),
        name="Officer Low Workload",
        role="field_officer",
        department_id=ai_dept.id,
        department=ai_dept.name,
        badge_id="BADGE-LOW-01",
        is_active=True
    )
    if role not in officer.roles:
        officer.roles.append(role)
    db_session.add(officer)
    db_session.commit()
    db_session.refresh(officer)
    return officer


@pytest.fixture
def officer_high_load(db_session: Session, ai_dept: Department) -> User:
    """Field Officer in ai_dept with 2 active tickets."""
    role = db_session.query(Role).filter_by(name="field_officer").first()
    if not role:
        role = Role(name="field_officer")
        db_session.add(role)

    officer = User(
        email="officer.high@civicresolve.in",
        password=hash_password("OfficerPass123!"),
        name="Officer High Workload",
        role="field_officer",
        department_id=ai_dept.id,
        department=ai_dept.name,
        badge_id="BADGE-HIGH-01",
        is_active=True
    )
    if role not in officer.roles:
        officer.roles.append(role)
    db_session.add(officer)
    db_session.commit()

    # Seed 2 active tickets assigned to officer_high_load
    for i in range(2):
        c = Complaint(
            token=f"CRA-HIGH-0{i+1}",
            title=f"Active Ticket {i+1}",
            description="Ongoing maintenance issue",
            department_id=ai_dept.id,
            department=ai_dept.name,
            assigned_officer_id=officer.id,
            assigned_officer_name=officer.name,
            status="In Progress",
            severity="Normal"
        )
        db_session.add(c)
    db_session.commit()
    db_session.refresh(officer)
    return officer


# ============================================================================
# 1. AI SPAM DETECTION TESTS
# ============================================================================

def test_ai_spam_detection_blocked_returns_400(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> detect_spam returning is_spam=True
    Verifies HTTP 400 response blocking submission and ensuring no DB record is created.
    """
    mock_spam = AsyncMock(return_value={
        "is_spam": True,
        "spam_type": "bot",
        "reason": "Automated repetitive lorem ipsum text detected"
    })

    form_data = {
        "title": "Broken Streetlight",
        "description": "Lorem ipsum dolor sit amet repetitive text"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 400
    assert "Spam detected: Automated repetitive lorem ipsum text detected (type: bot). Submission blocked." in response.json()["detail"]

    # Verify no complaint was created in the DB
    assert db_session.query(Complaint).count() == 0


def test_ai_spam_detection_cleans_up_uploaded_photo(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> detect_spam cleanup path
    Verifies that if spam is detected, the specific temporary photo saved to disk is deleted.
    """
    mock_spam = AsyncMock(return_value={
        "is_spam": True,
        "spam_type": "scam",
        "reason": "Phishing link contained in description"
    })

    test_uuid = uuid.UUID("11111111-2222-3333-4444-555555555555")
    expected_filepath = os.path.join("uploads", "complaints", "11111111-2222-3333-4444-555555555555.jpg")

    file_content = b"fake image content for testing cleanup"
    files = {"photo": ("spam_photo.jpg", io.BytesIO(file_content), "image/jpeg")}
    form_data = {
        "title": "Free Money Scam",
        "description": "Click here http://phishing.com for free money"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("uuid.uuid4", return_value=test_uuid):
        response = client.post("/api/complaint/anonymous", data=form_data, files=files)

    assert response.status_code == 400
    assert "Spam detected" in response.json()["detail"]

    # Verify no complaint in DB
    assert db_session.query(Complaint).count() == 0

    # Specifically verify that the file created at expected_filepath was deleted
    assert os.path.exists(expected_filepath) is False


def test_ai_spam_detection_not_spam_proceeds(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> detect_spam returning is_spam=False
    Verifies submission proceeds normally when spam check passes.
    """
    mock_spam = AsyncMock(return_value={
        "is_spam": False,
        "spam_type": "none",
        "reason": "Legitimate civic issue"
    })

    form_data = {
        "title": "Pothole on Main Road",
        "description": "Large pothole causing traffic slowdown near park gate"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Complaint filed successfully"
    assert db_session.query(Complaint).count() == 1


# ============================================================================
# 2. AI TRANSLATION TESTS
# ============================================================================

def test_ai_translation_non_english_input(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> translate_text
    Verifies that non-English title and description are translated to English before storing in DB.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})

    async def mock_translate(text, target_lang="en"):
        if "पानी" in text:
            return {"translated_text": "Water leakage on Main Street", "detected_language": "hi"}
        if "पाइप" in text:
            return {"translated_text": "Water pipe burst near colony entrance", "detected_language": "hi"}
        return {"translated_text": text, "detected_language": "en"}

    form_data = {
        "title": "पानी का रिसाव",
        "description": "मुख्य सड़क पर पाइप फट गया है"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.translate_text", side_effect=mock_translate):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    created = db_session.query(Complaint).first()
    assert created is not None
    assert created.title == "Water leakage on Main Street"
    assert created.description == "Water pipe burst near colony entrance"


def test_ai_translation_english_input_retains_original(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> translate_text (detected_language='en')
    Verifies English input is stored as-is.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_trans = AsyncMock(return_value={"translated_text": "Garbage issue", "detected_language": "en"})

    form_data = {
        "title": "Garbage Overflow",
        "description": "Garbage bin overflowing near market area"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.translate_text", mock_trans):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    created = db_session.query(Complaint).first()
    assert created.title == "Garbage Overflow"
    assert created.description == "Garbage bin overflowing near market area"


# ============================================================================
# 3. AI SANITIZATION TESTS
# ============================================================================

def test_ai_sanitization_removes_pii_and_neutralizes_tone(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> sanitize_complaint
    Verifies description is overwritten with sanitized professional text.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_sanitize = AsyncMock(return_value={
        "sanitized_text": "Broken streetlight reported at Sector 4 main junction. Active hazard for nighttime pedestrian traffic.",
        "summary": "Broken streetlight"
    })

    form_data = {
        "title": "Broken Streetlight",
        "description": "My name is John Doe, call 9876543210! Fix this damn light at Flat 402, I will sue the department!!!"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.sanitize_complaint", mock_sanitize):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    created = db_session.query(Complaint).first()
    assert created.description == "Broken streetlight reported at Sector 4 main junction. Active hazard for nighttime pedestrian traffic."
    assert "John Doe" not in created.description
    assert "9876543210" not in created.description


# ============================================================================
# 4. AI AUTO-ROUTING TESTS
# ============================================================================

def test_ai_auto_routing_assigns_correct_department(client, db_session, ai_dept):
    """
    Code Path: anonymous_complaint_resource.py -> auto_route_complaint
    Verifies AI routing matches department name and persists department_id and department string.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_route = AsyncMock(return_value={
        "department": ai_dept.name,
        "confidence": 0.95,
        "reasoning": "Complaint describes water supply pipe burst"
    })

    form_data = {
        "title": "Water Leakage",
        "description": "Clean drinking water leaking on road"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.auto_route_complaint", mock_route):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    created = db_session.query(Complaint).first()
    assert created.department_id == ai_dept.id
    assert created.department == ai_dept.name


# ============================================================================
# 5. LEAST-LOADED OFFICER DISPATCH TESTS
# ============================================================================

def test_ai_auto_routing_dispatches_least_loaded_officer(client, db_session, ai_dept, officer_low_load, officer_high_load):
    """
    Code Path: anonymous_complaint_resource.py -> officer auto-assignment algorithm
    Verifies that when AI routes to a department, the officer with the fewest active tickets is selected.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_route = AsyncMock(return_value={
        "department": ai_dept.name,
        "confidence": 0.92
    })

    form_data = {
        "title": "Water Pipe Repair Needed",
        "description": "Water pipeline burst causing street flooding"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.auto_route_complaint", mock_route):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    new_complaint = db_session.query(Complaint).filter_by(title="Water Pipe Repair Needed").first()
    assert new_complaint is not None
    assert new_complaint.assigned_officer_id == officer_low_load.id
    assert new_complaint.assigned_officer_name == officer_low_load.name
    assert new_complaint.status == "Assigned"


# ============================================================================
# 6. AI DUPLICATE DETECTION & CRITICAL ESCALATION TESTS
# ============================================================================

def test_ai_duplicate_detection_escalates_master_severity_to_critical(client, db_session, ai_dept):
    """
    Code Path: anonymous_complaint_resource.py -> find_duplicate_complaints (is_duplicate=True)
    Verifies that when AI identifies a duplicate complaint:
    1. Returns HTTP 200 with master complaint's tracking token.
    2. Escalates master complaint severity to 'Critical' in DB.
    3. Does NOT create a second Complaint record.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})

    # Seed an open master complaint created 1 hour ago
    master = Complaint(
        token="CRA-MASTER01",
        title="Burst Water Main",
        description="Major water pipe burst near Anna Nagar tower",
        location="Anna Nagar Tower Park",
        status="Submitted",
        severity="Normal",
        department_id=ai_dept.id,
        department=ai_dept.name,
        created_at=datetime.now(IST) - timedelta(hours=1)
    )
    db_session.add(master)
    db_session.commit()
    db_session.refresh(master)

    mock_dup = AsyncMock(return_value={
        "is_duplicate": True,
        "master_id": master.id,
        "master_token": master.token,
        "reason": "Same water main leak at Anna Nagar Tower"
    })

    form_data = {
        "title": "Water Pipe Leak near Tower",
        "description": "Massive water flooding near Anna Nagar Tower park",
        "address_text": "Anna Nagar Tower Park"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.find_duplicate_complaints", mock_dup):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["tracking_token"] == "CRA-MASTER01"
    assert res_data["trackingToken"] == "CRA-MASTER01"
    assert res_data["complaint_id"] == master.id

    # Verify Database Master State
    db_session.refresh(master)
    assert master.severity == "Critical"  # CRITICAL SEVERITY ESCALATION VERIFIED

    # Verify no second complaint created
    assert db_session.query(Complaint).count() == 1


# ============================================================================
# 7. DUPLICATE PHOTO HANDLING TESTS
# ============================================================================

def test_ai_duplicate_photo_master_without_photo_adopts_new_photo(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> duplicate path photo adoption
    Verifies that if master has no photo, but duplicate submission provides one, master updates submitted_photo.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})

    master = Complaint(
        token="CRA-NOPHOTO1",
        title="Open Manhole",
        description="Dangerous open manhole on 2nd cross road",
        location="2nd Cross Road",
        status="Submitted",
        severity="Normal",
        submitted_photo=None,
        created_at=datetime.now(IST) - timedelta(hours=2)
    )
    db_session.add(master)
    db_session.commit()

    mock_dup = AsyncMock(return_value={
        "is_duplicate": True,
        "master_id": master.id,
        "master_token": master.token
    })

    files = {"photo": ("manhole.jpg", io.BytesIO(b"photo content"), "image/jpeg")}
    form_data = {
        "title": "Open Manhole Cover",
        "description": "Deep open manhole hazard",
        "address_text": "2nd Cross Road"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.find_duplicate_complaints", mock_dup):
        response = client.post("/api/complaint/anonymous", data=form_data, files=files)

    assert response.status_code == 200
    db_session.refresh(master)
    assert master.submitted_photo is not None
    assert master.submitted_photo.startswith("/uploads/complaints/")


def test_ai_duplicate_photo_master_with_photo_discards_new_photo(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> duplicate path photo discard
    Verifies that if master already has a photo, new duplicate photo file is discarded from disk.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})

    existing_photo_url = "/uploads/complaints/master_original.jpg"
    master = Complaint(
        token="CRA-HASPHOTO1",
        title="Burst Pipe",
        description="Burst pipe on 4th street",
        location="4th Street",
        status="Submitted",
        severity="Normal",
        submitted_photo=existing_photo_url,
        created_at=datetime.now(IST) - timedelta(hours=1)
    )
    db_session.add(master)
    db_session.commit()

    mock_dup = AsyncMock(return_value={
        "is_duplicate": True,
        "master_id": master.id,
        "master_token": master.token
    })

    test_uuid = uuid.UUID("99999999-8888-7777-6666-555555555555")
    expected_filepath = os.path.join("uploads", "complaints", "99999999-8888-7777-6666-555555555555.jpg")

    dup_photo_bytes = b"duplicate submitted photo content"
    files = {"photo": ("dup_photo.jpg", io.BytesIO(dup_photo_bytes), "image/jpeg")}
    form_data = {
        "title": "Burst Pipe",
        "description": "Burst pipe on 4th street",
        "address_text": "4th Street"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.find_duplicate_complaints", mock_dup), \
         patch("uuid.uuid4", return_value=test_uuid):
        response = client.post("/api/complaint/anonymous", data=form_data, files=files)

    assert response.status_code == 200
    db_session.refresh(master)
    assert master.submitted_photo == existing_photo_url

    # Specifically verify that the temporary file created for duplicate submission was deleted
    assert os.path.exists(expected_filepath) is False


# ============================================================================
# 8. AI FAILURE / GRACEFUL FALLBACK TESTS
# ============================================================================

def test_ai_failure_detect_spam_fallback(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> detect_spam returns None on failure
    Verifies that if detect_spam returns None (AI failure), submission continues gracefully.
    """
    mock_spam = AsyncMock(return_value=None)

    form_data = {
        "title": "Streetlight Out",
        "description": "Dark area at street junction"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    assert db_session.query(Complaint).count() == 1


def test_ai_failure_translate_text_fallback(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> translate_text returns None on failure
    Verifies that if translation returns None (AI failure), original text is retained.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_trans = AsyncMock(return_value=None)

    form_data = {
        "title": "Raw Title Text",
        "description": "Raw Description Text"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.translate_text", mock_trans):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    created = db_session.query(Complaint).first()
    assert created.title == "Raw Title Text"
    assert created.description == "Raw Description Text"


def test_ai_failure_sanitize_complaint_fallback(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> sanitize_complaint returns None on failure
    Verifies that if sanitization returns None (AI failure), original description is retained.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_sanitize = AsyncMock(return_value=None)

    form_data = {
        "title": "Unsanitized Issue",
        "description": "Original raw complaint description text"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.sanitize_complaint", mock_sanitize):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    created = db_session.query(Complaint).first()
    assert created.description == "Original raw complaint description text"


def test_ai_failure_auto_route_complaint_fallback(client, db_session, ai_dept):
    """
    Code Path: anonymous_complaint_resource.py -> auto_route_complaint returns None on failure
    Verifies that if auto-routing returns None (AI failure), category_id fallback is used.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_route = AsyncMock(return_value=None)

    form_data = {
        "title": "Pothole Damage",
        "description": "Pothole on main road",
        "category_id": ai_dept.id
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.auto_route_complaint", mock_route):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    created = db_session.query(Complaint).first()
    assert created.department_id == ai_dept.id


def test_ai_failure_find_duplicate_complaints_fallback(client, db_session):
    """
    Code Path: anonymous_complaint_resource.py -> find_duplicate_complaints returns None on failure
    Verifies that if deduplication returns None (AI failure), request treats submission as non-duplicate and creates new complaint.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})

    master = Complaint(
        token="CRA-EXISTING1",
        title="Broken Gate",
        description="Broken park gate",
        status="Submitted",
        severity="Normal",
        created_at=datetime.now(IST) - timedelta(hours=1)
    )
    db_session.add(master)
    db_session.commit()

    mock_dup = AsyncMock(return_value=None)

    form_data = {
        "title": "Broken Gate",
        "description": "Broken park gate"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.find_duplicate_complaints", mock_dup):
        response = client.post("/api/complaint/anonymous", data=form_data)

    assert response.status_code == 200
    assert db_session.query(Complaint).count() == 2


# ============================================================================
# 9. AI MALFORMED RESPONSE PARSING UNIT TESTS
# ============================================================================

def test_parse_json_response_clean_json():
    text = '{"is_spam": false, "reason": "clean"}'
    res = _parse_json_response(text)
    assert res == {"is_spam": False, "reason": "clean"}


def test_parse_json_response_markdown_codeblock():
    text = """```json
    {
        "department": "Water Supply",
        "confidence": 0.9
    }
    ```"""
    res = _parse_json_response(text)
    assert res == {"department": "Water Supply", "confidence": 0.9}


def test_parse_json_response_embedded_json_in_text():
    text = 'Here is the analysis result: {"is_duplicate": true, "master_id": 42} Hope this helps!'
    res = _parse_json_response(text)
    assert res == {"is_duplicate": True, "master_id": 42}


def test_parse_json_response_invalid_json_returns_none():
    text = "Not a json response at all"
    res = _parse_json_response(text)
    assert res is None


def test_parse_json_response_empty_string_returns_none():
    assert _parse_json_response("") is None
    assert _parse_json_response("   ") is None


# ============================================================================
# 10. AI FUNCTION INVOCATION VERIFICATION TESTS
# ============================================================================

def test_ai_functions_invoked_with_expected_parameters(client, db_session, ai_dept):
    """
    Code Path: anonymous_complaint_resource.py -> AI function invocation parameter check
    Verifies that title, description, photo_bytes, and existing open complaints are passed correctly to AI functions.
    """
    mock_spam = AsyncMock(return_value={"is_spam": False})
    mock_trans = AsyncMock(return_value={"translated_text": "Sample Title", "detected_language": "en"})
    mock_sanitize = AsyncMock(return_value={"sanitized_text": "Sanitized Description"})
    mock_route = AsyncMock(return_value={"department": ai_dept.name})
    mock_dup = AsyncMock(return_value={"is_duplicate": False})

    # Seed an open complaint to be included in deduplication candidate list
    open_c = Complaint(
        token="CRA-OPEN01",
        title="Open Drain",
        description="Drain clogged",
        location="Block A",
        status="Submitted",
        severity="Normal",
        created_at=datetime.now(IST) - timedelta(hours=3)
    )
    db_session.add(open_c)
    db_session.commit()

    photo_content = b"sample photo bytes for invocation test"
    files = {"photo": ("test_photo.jpg", io.BytesIO(photo_content), "image/jpeg")}
    form_data = {
        "title": "Clogged Drain",
        "description": "Drain overflowing near Block A",
        "address_text": "Block A Corner"
    }

    with patch("application.resources.general.anonymous_complaint_resource.detect_spam", mock_spam), \
         patch("application.resources.general.anonymous_complaint_resource.translate_text", mock_trans), \
         patch("application.resources.general.anonymous_complaint_resource.sanitize_complaint", mock_sanitize), \
         patch("application.resources.general.anonymous_complaint_resource.auto_route_complaint", mock_route), \
         patch("application.resources.general.anonymous_complaint_resource.find_duplicate_complaints", mock_dup):

        response = client.post("/api/complaint/anonymous", data=form_data, files=files)

    assert response.status_code == 200

    # 1. Spam check called with title & description
    mock_spam.assert_called_once_with("Clogged Drain", "Drain overflowing near Block A")

    # 2. Translation called for title and description
    mock_trans.assert_any_call("Clogged Drain", target_lang="en")
    mock_trans.assert_any_call("Drain overflowing near Block A", target_lang="en")

    # 3. Sanitization called with description
    mock_sanitize.assert_called_once_with("Drain overflowing near Block A")

    # 4. Auto-routing called with title, sanitized description, photo_bytes, and dept_names
    mock_route.assert_called_once()
    route_args = mock_route.call_args[0]
    assert route_args[0] == "Clogged Drain"  # English input detected_language='en' so original title retained
    assert route_args[1] == "Sanitized Description"
    assert route_args[2] == photo_content  # Photo bytes passed to multimodal routing

    # 5. Deduplication called with new complaint dict & existing open complaints list
    mock_dup.assert_called_once()
    dup_args = mock_dup.call_args[0]
    new_cmp_dict, candidate_list = dup_args[0], dup_args[1]
    assert new_cmp_dict["title"] == "Clogged Drain"
    assert new_cmp_dict["description"] == "Sanitized Description"
    assert new_cmp_dict["location"] == "Block A Corner"
    assert len(candidate_list) >= 1
    assert candidate_list[0]["id"] == open_c.id
