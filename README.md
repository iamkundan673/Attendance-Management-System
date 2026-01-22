Attendance Management System

The Attendance Management System (AMS) is a backend-driven platform designed to streamline internal workforce operations.
It enables user attendance tracking, leave approvals, holiday schedules, and automated absence handling.
The system applies IP-based validation, task automation, and schedule-based processing to reduce manual administrative effort.

Features

User attendance tracking

Leave management

Holiday management

IP-based attendance validation

Automatic absent marking

Automated attendance processing

PostgreSQL database support

Technology Stack

Backend Framework: Django (DRF for APIs)

ORM: Django ORM (supports migrations, indexing, constraints)

Security Considerations:

    -IP Validation

    -Token-based authentication

    -Admin privilege enforcement

Database: PostgreSQL

Language: Python

Deployment Ready: Works in both development & production

System Requirements

Python 3.x

PostgreSQL

Pip & Virtual Environment tools (optional)

Project Structure
attendance-management-system/
├── Account/
├── ams/
├── leave/
├── myproject/
├── requirements.txt
└── manage.py

Installation & Setup
1. Clone the Repository
git clone <repository-url>
cd attendance-management-system

2. Create and Activate Virtual Environment (Optional)
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Configure Database

Create a PostgreSQL database and update the database configuration in settings.py.

5. Apply Migrations
python manage.py migrate

6. Run the Development Server
python manage.py runserver

API Endpoints:
 [text](ams/urls/admin.py)
 [text](ams/urls/auth.py)
 [text](ams/urls/notification.py)
 [text](ams/urls/user.py)
 

Usage

Once the server is running:

Attendance validation is IP-based.

Automatic absence marking processes unattended entries.

Leave and holiday modules are managed through backend/admin endpoints.