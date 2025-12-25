# SMG Enterprise Resource Planning (ERP) System

**Visionary Quantitative Trading & Operations Portal**

This repository contains the **Backend Microservices Architecture** for the SMG ERP. It is designed to handle high-performance internal operations, including Identity Management (RBAC), Leave Automation, and Asynchronous Financial Processing (Salary Slip Generation).

## Tech Stack

* **Core Framework:** Django 6.0 (Python 3.12) & Django REST Framework (DRF)
* **Database:** PostgreSQL (Production) / SQLite (Dev)
* **Asynchronous Task Queue:** Celery 5.6
* **Message Broker:** Redis 7.0 (Alpine)
* **Containerization:** Docker & Docker Compose
* **Security:** JWT Authentication, Throttling, RBAC, WhiteNoise

---

## System Architecture

The system is containerized into three orchestrated services:

1. **`web`**: The Django API Server (Gunicorn). Handles HTTP requests, Authentication, and Business Logic.
2. **`worker`**: The Background Processor. Handles heavy tasks like PDF Generation and Email Notifications off the main thread.
3. **`redis`**: The In-Memory Data Structure Store. Acts as the message broker between `web` and `worker`.

---

## Quick Start (One-Click Deployment)

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 1. Clone & Configure

```bash
git clone <your-repo-url>
cd services/core-django

```

Create a `.env` file in the root directory:

```ini
DEBUG=True
SECRET_KEY=super-secret-key-change-in-prod
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

```

### 2. Launch System

Run the entire architecture with a single command:

```bash
docker-compose up --build

```

* **API:** Live at `http://localhost:8000`
* **Admin Panel:** Live at `http://localhost:8000/admin/`

### 3. Create Super Admin

To access the dashboard, generate a superuser inside the running container:

```bash
docker-compose exec web python manage.py createsuperuser

```

---

## Testing Strategy

The system includes automated Unit Tests ensuring RBAC and Financial logic integrity.

**Run Tests inside Docker:**

```bash
docker-compose exec web python manage.py test

```

*Current Status: 8/8 Critical Tests Passing (Identity, Finance, Operations).*

---

## Key API Endpoints

| Module | Method | Endpoint | Description |
| --- | --- | --- | --- |
| **Identity** | POST | `/api/v1/auth/login/` | JWT Login (Returns Access/Refresh Tokens) |
| **Identity** | POST | `/api/v1/auth/register/` | Public Intern Registration |
| **Operations** | POST | `/api/v1/operations/leave/apply/` | Apply for Leave (Interns Only) |
| **Operations** | POST | `/api/v1/operations/leave/{id}/decide/` | Approve/Reject Leave (Admins Only) |
| **Finance** | POST | `/api/v1/finance/salary/generate/` | **Async:** Trigger PDF Salary Slips |

---

*Built with ❤️ by Trombokendu*
