"""
Minimal Global Pytest Configuration for CivicResolve AI Backend.

Provides core infrastructure required by all test modules:
1. Isolated test database URI override.
2. Model registry pre-loading for SQLAlchemy relationships.
3. Session-wide FastAPI application and in-memory SQLite engine.
4. Function-scoped transactional database session isolation.
5. Automatic dependency_overrides cleanup after every test.
6. Shared TestClient fixture with get_db dependency override.
"""

import os
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Force in-memory SQLite for tests before app configuration is loaded
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

# Application & DB Extensions
from app import create_app
from application.extensions.db_extn import Base, get_db

# Pre-load all SQLAlchemy models so relationship mappers register on Base.metadata
import application.helpers.models  # noqa: F401


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Session-scoped FastAPI application instance."""
    return create_app()


@pytest.fixture(scope="session")
def db_engine():
    """Session-scoped in-memory SQLite database engine with all tables created."""
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
    """Function-scoped isolated database session wrapped in a transaction rollback."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def autocleanup_dependency_overrides(app: FastAPI) -> Generator[None, None, None]:
    """Automatically resets FastAPI dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient configured with get_db overridden to use db_session."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    pytest hook to append module-wise summary and overall regression summary
    to the terminal output.
    """
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

