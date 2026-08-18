from application.extensions.db_extn import Base, get_db
from app import create_app
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from fastapi import FastAPI
import pytest
from typing import Generator
import os

os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_app()


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    import application.extensions.db_extn as db_extn
    db_extn.engine = db_engine
    db_extn.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def autocleanup_dependency_overrides(app: FastAPI) -> Generator[None, None, None]:
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_genai_client_default():
    from unittest.mock import patch, AsyncMock
    mock_resp = AsyncMock()
    mock_resp.text = '{"is_spam": false, "is_duplicate": false, "department": null}'
    mock_client = AsyncMock()
    mock_client.models.generate_content.return_value = mock_resp
    with patch("application.helpers.ai_service._get_client", return_value=mock_client):
        yield


@pytest.fixture(scope="function")
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    stats = terminalreporter.stats
    stats_by_file = {}

    for outcome in ("passed", "failed", "skipped", "error"):
        for rep in stats.get(outcome, []):
            path_part = rep.nodeid.split("::")[0]
            filename = os.path.basename(path_part)
            if filename not in stats_by_file:
                stats_by_file[filename] = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}

            cat = "failed" if outcome == "error" else outcome
            stats_by_file[filename][cat] += 1
            stats_by_file[filename]["total"] += 1

    if not stats_by_file:
        return

    preferred_order = [
        ("test_auth.py", "Authentication"),
        ("test_commissioner.py", "Commissioner"),
        ("test_commissioner_officer.py", "Commissioner Officer"),
        ("test_officer.py", "Officer"),
        ("test_facilities.py", "Facilities"),
        ("test_bills.py", "Bills"),
        ("test_citizen.py", "Citizen"),
        ("test_public.py", "Public"),
    ]

    ordered_modules = []
    known_files = set()

    for fname, title in preferred_order:
        if fname in stats_by_file:
            ordered_modules.append((fname, title))
            known_files.add(fname)

    for fname in sorted(stats_by_file.keys()):
        if fname not in known_files:
            title = fname.removesuffix(".py")
            if title.startswith("test_"):
                title = title[5:]
            title = title.replace("_", " ").title()
            ordered_modules.append((fname, title))

    tr = terminalreporter
    tr.ensure_newline()
    tr.write_line("=" * 50)
    tr.write_line("Module Summary")
    tr.write_line("=" * 50)
    tr.write_line("")

    overall_total = 0
    overall_passed = 0
    overall_failed = 0
    overall_skipped = 0

    for fname, title in ordered_modules:
        counts = stats_by_file[fname]
        tr.write_line(title)
        tr.write_line(f"File: {fname}")
        tr.write_line(f"Total : {counts['total']}")
        tr.write_line(f"Passed: {counts['passed']}")
        tr.write_line(f"Failed: {counts['failed']}")
        tr.write_line(f"Skipped: {counts['skipped']}")
        tr.write_line("")

        overall_total += counts["total"]
        overall_passed += counts["passed"]
        overall_failed += counts["failed"]
        overall_skipped += counts["skipped"]

    tr.write_line("=" * 50)
    tr.write_line("Overall Regression Summary")
    tr.write_line("=" * 50)
    tr.write_line("")
    tr.write_line(f"Total Tests : {overall_total}")
    tr.write_line(f"Passed      : {overall_passed}")
    tr.write_line(f"Failed      : {overall_failed}")
    tr.write_line(f"Skipped     : {overall_skipped}")
