# SMG Enterprise Resource Planning (ERP) System

**Visionary Quantitative Trading & Operations Portal**

This repository contains the **Backend Microservices Architecture** for the SMG ERP. It is designed to handle high-performance internal operations, including Identity Management (RBAC), Leave Automation, and Asynchronous Financial Processing (Salary Slip Generation).

## Tech Stack

* **Core Framework:** Django 6.0 (Python 3.12) & Django REST Framework (DRF)
* **Database:** PostgreSQL (Production) / SQLite (Dev)
* **Asynchronous Task Queue:** Celery 5.6
* **Message Broker:** Redis 7.0 (Alpine)
* **Cloud Infrastructure:** AWS (S3, SES, SNS)
* **Containerization:** Docker & Docker Compose
* **Security:** JWT Authentication, Throttling, RBAC, WhiteNoise

---

## System Architecture

The system is containerized into three orchestrated services:

1. **`web`**: The Django API Server (Gunicorn). Handles HTTP requests, Authentication, and Business Logic.
2. **`worker`**: The Background Processor. Handles heavy tasks like PDF Generation and Email Notifications off the main thread.
3. **`redis`**: The In-Memory Data Structure Store. Acts as the message broker between `web` and `worker`.

---

## ☁️ Infrastructure Setup Guide (AWS & Docker)

Before running the code, you must configure the cloud environment. Follow these steps to set up your own AWS and Docker accounts.

### 1. Docker Setup
* **Download:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your OS (Windows/Mac/Linux).
* **Verify:** Open a terminal and run `docker --version`. Ensure the Docker Engine is running.

### 2. AWS Account & IAM Configuration
The system uses AWS for file storage and notifications.
1.  **Create Account:** Sign up at [aws.amazon.com](https://aws.amazon.com/).
2.  **Create IAM User:**
    * Go to **IAM Dashboard** > **Users** > **Create User**.
    * Name it `smg-backend-user`.
    * **Permissions:** Attach the following policies directly:
        * `AmazonS3FullAccess` (For Media Storage)
        * `AmazonSNSFullAccess` (For SMS Alerts)
        * `AmazonSESFullAccess` (For Email Notifications)
    * **Credentials:** After creation, go to the **Security Credentials** tab and generate an **Access Key**.
    * **Save:** Copy the `Access Key ID` and `Secret Access Key` immediately. You will need these for the `.env` file.

### 3. S3 Bucket Setup (Media Storage)
1.  Go to the **S3 Console** and click **Create Bucket**.
2.  **Bucket Name:** Choose a unique name (e.g., `smg-erp-media-prod`).
3.  **Region:** Select `Asia Pacific (Mumbai) ap-south-1` (or your preferred region).
4.  **Public Access:** Uncheck "Block all public access" (Required for the frontend to access profile pictures directly).
    * *Note: A warning will appear; acknowledge that the bucket is public.*
5.  Click **Create Bucket**.

### 4. SES & SNS Setup (Notifications)
* **SES (Email):**
    * Go to **Amazon SES** > **Verified Identities**.
    * Click **Create Identity** > Select **Email Address**.
    * Enter the email you want the system to send *from* (e.g., `admin@smg.com`) and verify it.
    * *Important:* If your account is in "Sandbox Mode", you must also verify every email address you intend to *test with* (the recipient emails).
* **SNS (SMS):**
    * In "Sandbox Mode", you must specifically add verified phone numbers in the **SNS Sandbox** menu to send SMS messages to them during testing.

---

## Quick Start (Deployment)

### 1. Clone & Configure

```bash
git clone <your-repo-url>
cd services/core-django

```

### 2. Environment Variables (.env)

Create a `.env` file in the root directory. **Copy this exact format** and fill in your details from the Infrastructure Setup step:

```ini
# --- General Settings ---
DEBUG=True
SECRET_KEY=super-secret-key-change-in-prod
ALLOWED_HOSTS=127.0.0.1,localhost
# Frontend URL for CORS (React/Next.js)
CORS_ALLOWED_ORIGINS=http://localhost:3000

# --- Database & Broker ---
# In Docker, the host is the service name 'redis'
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# --- AWS Configuration (Required) ---
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=abcd12345xxxxxxxxxxxxxxxxxxxx
AWS_REGION=ap-south-1

# --- AWS S3 (Storage) ---
AWS_STORAGE_BUCKET_NAME=your-unique-bucket-name
AWS_S3_REGION_NAME=ap-south-1

# --- AWS SES (Email) ---
# Must match a verified identity in your AWS SES Console
DEFAULT_FROM_EMAIL=your-verified-email@domain.com

```

### 3. Launch System

Run the entire architecture with a single command:

```bash
docker-compose up --build

```

* **API:** Live at `http://localhost:8000`
* **Admin Panel:** Live at `http://localhost:8000/admin/`

### 4. Create Super Admin

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