# Mini Telecom Commissioning & Provisioning Platform

## Overview

The Mini Telecom Commissioning & Provisioning Platform is a lightweight backend service built with FastAPI. It simulates the lifecycle of telecom customer accounts and service lines, providing a structured workflow for service activation (commissioning).

This platform addresses the problem of managing subscription-based services by enforcing strict state transitions, role-based access control (RBAC), and a comprehensive audit trail for all administrative actions. It serves as a foundational Service Provisioning & Commissioning system.

## Features

- **Authentication & Role-Based Access Control**: Secure JWT-based authentication supporting Admin and Operator roles.
- **Account Management**: Full lifecycle management for customer accounts, including creation, updates, and status tracking (`ACTIVE`, `SUSPENDED`, `CLOSED`).
- **Line Management**: Management of service lines (e.g., SIM cards or virtual subscriptions) associated with customer accounts.
- **Commissioning Workflow**: A simulated activation process that transitions lines from `PROVISIONED` to `ACTIVE` with enforced business rules.
- **Validation**: Strict input validation using Pydantic schemas and business logic validation for state transitions.
- **Audit Logging**: Comprehensive recording of all state-changing actions, capturing the actor, action type, resource ID, and data diffs.
- **API Documentation**: Automated documentation via OpenAPI (Swagger) and an exported Postman collection.
- **System Health Monitoring**: Health check endpoint validating service and database connectivity.

## Architecture Overview

### High-Level System Design

The application follows a modular, layered architecture to ensure separation of concerns and maintainability.

- **API Layer (`app/api/`)**: Defines RESTful endpoints and handles HTTP request/response cycles.
- **Service Layer (`app/services/`)**: Contains core business logic and enforces domain rules.
- **Data Access Layer (`app/models/`)**: Defines the database schema using SQLAlchemy ORM.
- **Schema Layer (`app/schemas/`)**: Provides data validation and serialization via Pydantic.
- **Core Layer (`app/core/`)**: Manages cross-cutting concerns such as security, configuration, logging, and application state.

### Authentication & Authorization

Authentication is implemented using OAuth2 Password Flow with JWT tokens.

- **Access Tokens**: Short-lived JWTs containing user identity and role claims.
- **Refresh Tokens**: Stored in the database and rotated upon use to provide secure session extension.
- **RBAC**: Access to administrative endpoints (e.g., account creation and commissioning) is restricted to the `ADMIN` role.

### Commissioning Workflow

The commissioning process represents a critical business flow:

1. A line is created in the `PROVISIONED` state.
2. The `commission` endpoint is called.
3. The system validates the line status and initiates a simulated provisioning delay (2 seconds).
4. Upon successful completion, the line transitions to the `ACTIVE` state.
5. All steps are recorded in the audit trail.

### Data Storage

The application uses **SQLite** for data persistence. This provides a zero-configuration, file-based database suitable for development and lightweight service environments.

### Validation & Logging

- **Validation**: Every request is validated against Pydantic models. Custom validators enforce business rules such as valid MSISDN formats and allowed status transitions.
- **Logging**: Uses Loguru for structured logging. Logs are output to the console for real-time monitoring and written to rotating files in the `logs/` directory for long-term retention.

## Tech Stack

- **Language**: Python 3.14+
- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Security**: JWT (python-jose), bcrypt (passlib)
- **Logging**: Loguru
- **Documentation**: OpenAPI 3.1 / Postman Collection

## Setup Instructions

### Prerequisites

- Python 3.14 or higher
- `pip` (Python package manager)

### Environment Variables

The application uses `.env.example` as a template for configuration. Before running the application, copy the example file to create your environment configuration:

```bash
cp .env.example .env
```

Adjust the values in `.env` as needed (e.g., `SECRET_KEY`, `DEBUG` mode).

### Run with Docker (Recommended)

The project includes a `Dockerfile` and `docker-compose.yml` for containerized execution.

```bash
docker compose up --build
```

The API will be available at:

```bash
http://localhost:8000
```

### Local Setup

### 1. Install Dependencies

```bash
python -m venv .venv

# Activate environment
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

### 2. Database Setup & Seeding

The database is automatically initialized and seeded with sample data on first run in development mode (`PROD=False`).

To manually trigger seeding:

```bash
python -m app.db.init_db
```

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```bash
http://localhost:8000
```

### 4. Access API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Documentation

Comprehensive documentation files are provided in the `docs/` folder:

- **OpenAPI Spec**: `docs/openapi.json`
- **Postman Collection**: `docs/postman_collection.json`

### Importing into Postman

1. Open Postman.
2. Click **Import**.
3. Drag and drop `docs/postman_collection.json`.
4. Configure the `baseUrl` collection variable to `http://localhost:8000`.

## Core Workflows

### Authentication

1. **Login**: `POST /auth/login`.
2. **Tokens**: Response includes an `access_token` and `refresh_token`.
3. **Usage**: Include the access token in the `Authorization` header as a Bearer token:

```bash
Authorization: Bearer <token>
```

#### Roles

- **ADMIN**: Can manage accounts, create lines, and perform commissioning.
- **OPERATOR**: Can view accounts and lines only.

### Account Lifecycle

- **Create**: `POST /accounts/` (Admin)
- **View**: `GET /accounts/{id}`
- **Update**: `PUT /accounts/{id}` (Admin)
- **Statuses**: `ACTIVE`, `SUSPENDED`, `CLOSED`.

### Line Lifecycle

- **Create**: `POST /accounts/{id}/lines` (Admin). Initial state: `PROVISIONED`.
- **Commission**: `POST /lines/{id}/commission` (Admin). Transitions `PROVISIONED` -> `ACTIVE`.
- **Suspend/Activate**: `PATCH /lines/{id}/status` (Admin).
- **Remove**: `DELETE /lines/{id}` (Admin). Transitions status to `DELETED`.

## Validation & Error Handling

### Input Validation

- Email fields require a valid email format.
- MSISDNs must be unique across the platform.
- IDs must be valid UUIDs.

### Business Rules

- Status transitions are enforced via a state machine
- A `DELETED` line cannot transition to another state.
- Commissioning is only allowed for lines in the `PROVISIONED` state.

### Error Responses

All errors return a consistent JSON structure:

```json
{
  "error": "GenericErrorName",
  "message": "Detailed error description"
}
```

## Logging

The platform implements a dual logging strategy:

- **Console Output**: Colorized, human-readable logs for development.
- **File Output**: JSON-serialized logs stored in `logs/` with 10MB rotation and 30-day retention.
- **Audit Logging**: High-impact actions are persisted in the SQL `audits` table, including actor identity and state diffs for accountability.

## Assumptions

- **Ownership**: Each service line belongs to exactly one customer account.
- **Provisioning**: External network provisioning is simulated with a 2-second delay; no real-world HLR/HSS integration is implemented.
- **Identifiers**: MSISDNs are provided manually rather than being automatically assigned from a pool.
- **Infrastructure**: SQLite is used for this exercise; production environments would require PostgreSQL or another RDBMS.
- **Interface**: A Graphical User Interface is not required; the solution is delivered as an API-only platform.

## Future Improvements

- **Async Provisioning**: Implementation of Celery/Redis for non-blocking commissioning.
- **Audit Filter/Export**: API endpoints to query and export audit logs.
- **Number Pool Management**: Automated MSISDN assignment from a managed pool.
- **Frontend Dashboard**: A React-based management console.
