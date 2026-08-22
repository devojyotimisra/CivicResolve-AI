import pytest
from sqlalchemy.orm import Session

from application.extensions.security_extn import hash_password
from application.helpers.models import Notification, Role, User
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
        email="notif.citizen@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Notif User",
        role="citizen",
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
def other_user(db_session: Session) -> User:
    user = User(
        email="other.citizen@civicresolve.in",
        password=hash_password("Pass123!"),
        name="Other User",
        role="citizen",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_notifications(db_session: Session, citizen_user: User, other_user: User):
    n1 = Notification(
        user_id=citizen_user.id,
        title="Notif 1",
        message="Message 1",
        notif_type="info",
        is_read=False,
    )
    n2 = Notification(
        user_id=citizen_user.id,
        title="Notif 2",
        message="Message 2",
        notif_type="success",
        is_read=True,
    )
    n3 = Notification(
        user_id=citizen_user.id,
        title="Role Notif",
        message="Message Role",
        notif_type="warning",
        is_read=False,
    )
    n4 = Notification(
        user_id=other_user.id,
        title="Other Notif",
        message="Other Message",
        notif_type="error",
        is_read=False,
    )
    db_session.add_all([n1, n2, n3, n4])
    db_session.commit()
    db_session.refresh(n1)
    db_session.refresh(n2)
    db_session.refresh(n3)
    db_session.refresh(n4)
    return n1, n2, n3, n4


def test_list_notifications(client, citizen_headers, sample_notifications):
    n1, n2, n3, n4 = sample_notifications
    response = client.get("/api/notifications", headers=citizen_headers)
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    notif_ids = [n["id"] for n in data["notifications"]]
    assert n1.id in notif_ids
    assert n2.id in notif_ids
    assert n3.id in notif_ids
    assert n4.id not in notif_ids


def test_mark_as_read(client, citizen_headers, sample_notifications, db_session):
    n1, n2, n3, n4 = sample_notifications

    response = client.patch(f"/api/notifications/{n1.id}/read", headers=citizen_headers)
    assert response.status_code == 200
    assert response.json()["isRead"] is True

    db_session.refresh(n1)
    assert n1.is_read is True


def test_mark_as_read_forbidden(client, citizen_headers, sample_notifications):
    n1, n2, n3, n4 = sample_notifications

    response = client.patch(f"/api/notifications/{n4.id}/read", headers=citizen_headers)
    assert response.status_code == 403


def test_mark_as_read_not_found(client, citizen_headers):
    response = client.patch("/api/notifications/999/read", headers=citizen_headers)
    assert response.status_code == 404


def test_mark_as_unread(client, citizen_headers, sample_notifications, db_session):
    n1, n2, n3, n4 = sample_notifications

    response = client.patch(f"/api/notifications/{n2.id}/unread", headers=citizen_headers)
    assert response.status_code == 200
    assert response.json()["isRead"] is False

    db_session.refresh(n2)
    assert n2.is_read is False


def test_mark_all_as_read(client, citizen_headers, sample_notifications, db_session):
    n1, n2, n3, n4 = sample_notifications

    response = client.patch("/api/notifications/read-all", headers=citizen_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "All notifications marked as read"

    db_session.refresh(n1)
    db_session.refresh(n3)
    db_session.refresh(n4)

    assert n1.is_read is True
    assert n3.is_read is True

    assert n4.is_read is False


def test_delete_notification(client, citizen_headers, sample_notifications, db_session):
    n1, n2, n3, n4 = sample_notifications

    response = client.delete(f"/api/notifications/{n1.id}", headers=citizen_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Notification deleted"

    assert db_session.get(Notification, n1.id) is None


def test_delete_notification_forbidden(client, citizen_headers, sample_notifications, db_session):
    n1, n2, n3, n4 = sample_notifications

    response = client.delete(f"/api/notifications/{n4.id}", headers=citizen_headers)
    assert response.status_code == 403

    assert db_session.get(Notification, n4.id) is not None


def test_clear_all_notifications(client, citizen_headers, sample_notifications, db_session):
    n1, n2, n3, n4 = sample_notifications
    n1_id, n2_id, n3_id, n4_id = n1.id, n2.id, n3.id, n4.id

    response = client.delete("/api/notifications", headers=citizen_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "All notifications cleared"

    assert db_session.get(Notification, n1_id) is None
    assert db_session.get(Notification, n2_id) is None
    assert db_session.get(Notification, n3_id) is None

    assert db_session.get(Notification, n4_id) is not None
