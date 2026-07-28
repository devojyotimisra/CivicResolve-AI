# Automated Backend Testing

This directory contains the automated integration test suite for the CivicResolve AI backend. The suite verifies API endpoint behavior, role-based authorization, input validation, ticket state transitions, and database persistence across the main backend modules.

## Technologies Used

- **Python 3.12+**
- **pytest** — test discovery, execution, assertions, and fixtures
- **FastAPI TestClient / Starlette** — in-process HTTP testing of FastAPI routes
- **SQLAlchemy 2.0+** — ORM and database session management
- **SQLite** — isolated in-memory database used during testing
- **uv** — project environment and dependency management

## Test Architecture

Shared test infrastructure is defined in `conftest.py`. It provides the FastAPI application, test database, database sessions, and HTTP test client used by the individual test modules.

### Database Isolation

Tests use an in-memory SQLite database:

`sqlite:///:memory:`

The database tables are created for the test session. Each test receives a database session bound to a transaction, which is rolled back after the test completes. This prevents test data from persisting between test cases.

### FastAPI Dependency Overrides

FastAPI's `app.dependency_overrides` mechanism is used to replace the application's normal `get_db` dependency with the test database session.

Dependency overrides are cleared after each test so that changes made by one test do not affect subsequent tests.

### API Testing

FastAPI's `TestClient` executes requests directly against the application without requiring a separately running Uvicorn server.

Tests therefore exercise the API routing and application logic while remaining independent of an external HTTP server.

## Directory Structure

```text
tests/
├── __init__.py
├── conftest.py
├── test_auth.py
├── test_commissioner.py
├── test_commissioner_officer.py
├── test_officer.py
├── test_facilities.py
├── test_bills.py
├── test_citizen.py
└── test_public.py
```

## Test Modules

The suite is divided into eight domain-specific test modules.

| Test File | Area Tested | Tests |
| --- | --- | ---: |
| `test_auth.py` | Registration, login, authentication, roles, and credentials | 17 |
| `test_bills.py` | Bill types, bill issuance, citizen bill listing, payments, and receipts | 20 |
| `test_citizen.py` | Citizen dashboard, profile, complaints, and search | 12 |
| `test_commissioner.py` | Dashboard, complaints, categories, citizens, search, and profile | 22 |
| `test_commissioner_officer.py` | Officer creation, update, deletion, listing, and ticket assignment | 20 |
| `test_facilities.py` | Facility management, citizen bookings, and cancellation | 27 |
| `test_officer.py` | Officer dashboard, profile, tickets, status transitions, and resolution | 20 |
| `test_public.py` | Anonymous complaint submission and public complaint tracking | 12 |
| **Total** | **Backend Integration Suite** | **150** |

## API Coverage

The test suite covers eight main areas of the backend:

- **Authentication** — signup, login using supported credentials, account validation, role handling, and authentication behavior.
- **Commissioner** — dashboard metrics, complaint monitoring, department/category management, citizen listing, search, and profile operations.
- **Commissioner / Officer Management** — officer creation, department association, profile updates, deletion, listing, and complaint assignment.
- **Officer** — dashboard, profile management, ticket search and details, status transitions, and ticket resolution.
- **Facilities / Bookings** — facility creation and management, citizen facility access, booking validation, duplicate-booking checks, and cancellation.
- **Bills / Payments** — bill type management, bill issuance, citizen bill retrieval, payment processing, and receipt generation.
- **Citizen** — dashboard, profile management, complaint retrieval, complaint details, and search.
- **Public / Anonymous Complaints** — anonymous complaint submission, upload validation, tracking-token generation, and public complaint tracking.

## Running the Tests

From the repository root:

```bash
cd Backend
uv sync
uv run pytest tests/ -v
```

For a normal test run:

```bash
uv run pytest tests/
```

To execute an individual module:

```bash
uv run pytest tests/test_officer.py
```

## Current Test Result

The complete suite was executed before preparing this documentation.

- **Total tests:** 150
- **Passed:** 150
- **Failed:** 0
- **Warnings:** 293
- **Execution time:** 27.77 seconds

Most reported warnings are associated with legacy SQLAlchemy `Query.get()` usage in the existing backend code.

## Defects Identified During Testing

Automated testing exposed backend defects during development. These defects were investigated and corrected before the final regression run.

### Commissioner Facility Authorization

The commissioner facility-list resource attempted to raise `HTTPException` for an authenticated non-commissioner user, but `HTTPException` was not imported.

This caused the authorization branch to raise a Python `NameError` instead of returning the intended HTTP 403 response.

The missing import was added, and the corresponding authorization path is now covered by a regression test.

### Citizen Complaint Listing

The citizen complaint-list resource attempted to filter `Complaint` records using a `user_id` attribute that does not exist in the current `Complaint` model.

The resource also referenced response attributes that did not match the ORM model:

- `tracking_token` instead of `token`
- `priority` instead of `severity`

The complaint-list implementation was aligned with the existing complaint schema and public civic-report architecture. Regression tests now exercise this endpoint successfully.

These were development-time defects. The current test suite contains no failing tests related to them.

## Test-Suite Quality Check

A manual mutation experiment was performed to check whether the test suite could detect changes to important backend behavior.

The officer ticket state-transition configuration normally requires the workflow:

```text
Assigned → En Route → On Site → In Progress → Resolved
```

During the experiment, the backend was temporarily modified to also permit a direct transition from:

```text
Assigned → In Progress
```

The existing tests continued to pass because they checked another invalid transition (`Assigned → Resolved`) but did not explicitly test this particular state-machine boundary.

This exposed a test-coverage gap.

A regression test named:

`test_officer_ticket_status_update_assigned_to_in_progress_rejected`

was subsequently added to `test_officer.py`.

The test verifies that:

1. `Assigned → In Progress` is rejected with HTTP 400.
2. The complaint remains in the `Assigned` state after the rejected request.

The temporary production-code mutation was reverted after the experiment. Mutation testing is not part of the automated test execution; it was used manually to evaluate the sensitivity of the suite.

## Test Safety and Isolation

The automated tests are configured to use an isolated in-memory SQLite database rather than the application's normal database.

Before the FastAPI application is initialized, `conftest.py` sets:

```python
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
```

Test database operations therefore execute against the temporary in-memory SQLite database.

Each test runs within its own database transaction, and the transaction is rolled back during teardown. FastAPI dependency overrides are also cleared after every test.

This keeps test data isolated from both other test cases and the application's normal database.