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
