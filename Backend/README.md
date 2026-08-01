# CivicResolve AI — Backend

A robust, secure REST API for municipal administration, civic issue reporting, and public facility management. Built with **Python 3.12**, **FastAPI**, and **SQLAlchemy**.

---

## Features & Portals

### Citizen API
* **Grievance Reporting:** Endpoints to file civic hazard reports (potholes, street lights, waste accumulation) either anonymously or with an authenticated citizen account.
* **Live Token Tracking:** Retrieve issue resolution progress using unique 12-character tracking codes.
* **Civic Facilities & Reservations:** Explore municipal venues, check real-time availability calendars, and book reservations online.
* **Utility Billing:** Fetch and pay municipal taxes, water bills, and maintenance fees.

### Field Officer API
* **Task Management:** Retrieve assigned maintenance tickets and hazard reports.
* **Live Status Advancement:** Update task statuses on the go (*Assigned*, *In Progress*, *Resolved*).
* **Photographic Proof:** Upload engineering notes and resolution photos/videos to mark tickets as *Resolved*.

### Commissioner API
* **Executive Dashboard:** Oversee city-wide resolution KPIs, department efficiency, and revenue analytics via API aggregates.
* **Administration:** Manage field officers, municipal departments, civic facilities, and citizen accounts from a centralized set of endpoints.

---

## 🛠️ Tech Stack

* **Core Framework:** [Python 3.12+](https://www.python.org/) + [FastAPI](https://fastapi.tiangolo.com/)
* **Database & ORM:** [SQLite](https://www.sqlite.org/) + [SQLAlchemy 2.0+](https://www.sqlalchemy.org/)
* **Authentication:** JWT (JSON Web Tokens) with Role-Based Access Control (RBAC) via [python-jose](https://pypi.org/project/python-jose/)
* **Dependency Management:** [uv](https://astral.sh/uv)
* **Testing:** [pytest](https://docs.pytest.org/) + FastAPI TestClient

---

## Getting Started

### Prerequisites
* [Python](https://www.python.org/) (v3.12 or higher recommended)
* `uv` for dependency management

### Installation & Setup

1. **Navigate to the backend directory:**
   ```bash
   cd Backend
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Start the development server:**
   ```bash
   uv run uvicorn app:app --reload
   ```
   The API will be available at `http://localhost:8000`.

---

## Available Scripts

| Command | Description |
| :--- | :--- |
| `uv run uvicorn app:app --reload` | Starts the local development server with auto-reload. |
| `uv run pytest tests/` | Runs the full automated integration test suite. |

---

## Automated Backend Testing

This directory contains the automated integration test suite for the CivicResolve AI backend platform. The primary purpose of the test suite is to verify API endpoint functionality, role-based authorization rules, resource state-machine transitions, input validation constraints, and database persistence across all application modules.

### Test Architecture

The test suite is built on a centralized fixture architecture configured within `conftest.py`. This design guarantees test isolation, execution speed, and deterministic data state across test runs.

#### Core Architecture Components

- **Pytest Infrastructure**: Implements reusable `pytest` fixtures for application context initialization and transactional database sessions.
- **FastAPI TestClient**: Executes API request handlers directly within the Python process without initializing a live HTTP server socket, ensuring rapid synchronous validation of status codes and JSON response schemas.
- **Test Database Strategy**: Overrides `SQLALCHEMY_DATABASE_URI` to point to `sqlite:///:memory:` before importing the application factory. Database tables are created once per test session on an in-memory SQLite engine.
- **Database Isolation and Rollback**: Each test function receives a dedicated `db_session` bound to an isolated connection transaction. At test teardown, the transaction is rolled back, instantly restoring the database to a clean baseline without expensive schema drop-and-create operations.
- **Dependency Overrides**: Uses FastAPI's `app.dependency_overrides` mapping to bind the production database dependency (`get_db`) to the active test transaction. An `autouse=True` fixture automatically clears dependency overrides after every test to prevent cross-test state leakage.

### Test Modules

The test suite is divided into eight domain-specific test files:

| Test File | Area Tested | Number of Tests |
| :--- | :--- | :---: |
| `test_auth.py` | User registration, login authentication (email/badge ID), JWT encoding/decoding, and password hashing | 17 |
| `test_bills.py` | Utility bill creation, category management, citizen bill listing, payment processing, and receipt generation | 20 |
| `test_citizen.py` | Citizen profile fetching/updating, dashboard metrics, and complaint search/retrieval | 12 |
| `test_commissioner.py` | Commissioner dashboard KPIs, revenue aggregation, category management, and citizen list queries | 22 |
| `test_commissioner_officer.py` | Field officer CRUD operations, department validation, and officer ticket assignment workflows | 20 |
| `test_facilities.py` | Public facility catalog, venue management, citizen booking creation, and cancellation rules | 27 |
| `test_officer.py` | Officer dashboard, profile management, ticket search, status state transitions, and ticket resolution | 20 |
| `test_public.py` | Anonymous complaint creation, file upload validation, and public tracking by token | 12 |
| **Total** | **Full Integration Suite** | **150** |

### API Coverage

The integration test suite provides comprehensive verification across eight functional backend domains:

- **Authentication**: User signup, login via email or badge ID, active account status enforcement, role assignments (`citizen`, `field_officer`, `commissioner`), and JWT token validation.
- **Commissioner**: Dashboard aggregate KPIs, combined utility and facility revenue calculation, complaint listing and filtering by status/department, and category CRUD operations.
- **Commissioner/Officer Management**: Officer account creation with department association, officer profile updates, soft-deletion, and officer assignment to submitted complaints.
- **Officer**: Profile updates, assigned ticket search, ticket detail history, ticket resolution with notes/photos, and linear status transition enforcement.
- **Facilities/Bookings**: Venue creation and management, active venue catalog filtering, booking date constraints (rejection of past and far-future dates), duplicate booking prevention, and ownership-restricted cancellation.
- **Bills/Payments**: Utility bill type creation/updating, bill issuance, citizen bill listing, payment status updates, and transaction ID receipt generation.
- **Citizen**: Profile management, dashboard ticket status summaries, complaint detail fetching, and title/token search.
- **Public/Anonymous Complaints**: Unauthenticated complaint submission, MIME type and extension validation for uploaded files, public ticket tracking by tracking token, and cross-flow visibility in citizen listings.

### Running the Tests

To execute the test suite:

```bash
uv run pytest tests/ -v
```

For standard, non-verbose test execution:

```bash
uv run pytest tests/
```

To run a specific test module:

```bash
uv run pytest tests/test_officer.py
```

### Current Test Result

The complete integration test suite was executed prior to compiling this documentation:

- **Total Tests Collected**: 150
- **Passed**: 150
- **Failed**: 0
- **Warnings**: 293 (Legacy API deprecation warnings for SQLAlchemy 1.x `Query.get()`)
- **Execution Status**: 100% Success (150 passed in 27.77 seconds)

### Defects Identified During Testing

Automated integration testing revealed two runtime code defects in backend resource handlers, which were subsequently remediated:

1. **Missing Exception Class Import**: In `commissioner_facilities_list_resource.py`, an unhandled authorization check raised a Python `NameError` due to a missing `HTTPException` import. The import was added, and tests now verify an HTTP 403 Forbidden response.
2. **Invalid Model Query Filter**: In `citizen_complaints_list_resource.py`, fetching citizen complaints attempted to filter by `user_id` on the `Complaint` model, which lacks a `user_id` attribute. This resulted in an HTTP 500 database error. The query was corrected to return public municipality complaints cleanly.

Both historical defects were fixed during development, and the final test suite passes completely with zero failures.

### Test-Suite Quality Check

To evaluate test suite sensitivity and state-machine boundary enforcement, a manual mutation experiment was conducted on the ticket status workflow in `officer_ticket_update_status_resource.py`. The transition matrix was temporarily altered to allow direct transitions from `Assigned` to `In Progress`.

The experiment demonstrated that while illegal transitions to `Resolved` were caught, no existing test explicitly checked the direct `Assigned` -> `In Progress` path. A dedicated negative regression test (`test_officer_ticket_status_update_assigned_to_in_progress_rejected`) was added to `test_officer.py` to assert that direct `Assigned` to `In Progress` status updates return HTTP 400 and preserve database state.

### Test Safety and Isolation

Executing the automated test suite carries zero risk of modifying or corrupting the production database:

1. `conftest.py` sets `os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"` prior to application initialization.
2. All database operations execute purely in volatile system memory (RAM) via SQLite in-memory tables.
3. The production SQLite database file (`CivicResolveAI.sqlite3`) is never accessed, written to, or altered during test execution.
