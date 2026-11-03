# CarePoint Hospital Management System

CarePoint HMS is a Flask + MySQL hospital management application built strictly on the supplied ER diagram's original 14 entities. No `app_user` table or additional database entity is used.

## Roles and access

- **Citizen:** self-registers, signs in using email and password, submits appointment requests, views their own appointments, medical history, prescriptions and emergency cases.
- **Administrator:** signs in using credentials in `.env`; manages hospital records, doctors, staff, departments, appointments, medicines, beds, ambulances, drivers, emergency cases and reports.
- **Hospital staff:** staff records and work assignments are managed by the administrator. Individual staff login is not provided because the fixed ER diagram has no staff username/password attributes. The administrator/staff team can use the administrator-managed interface.

Citizen appointment requests are initially saved as `Booked`. Only the administrator can confirm, complete, cancel or otherwise manage appointment records.

## Requirements

- Python 3.10+
- MySQL 8.0+
- VS Code (recommended)

## Fresh installation

1. Create/open a MySQL connection in MySQL Workbench.
2. Open `database/schema.sql` and execute it on a fresh installation. **This script drops and recreates the 14 project tables**, so do not run it on a database containing records you need to keep.
3. Copy `.env.example` to `.env`.
4. Edit `.env` and set your MySQL password, a private `SECRET_KEY`, `ADMIN_USERNAME`, and a strong `ADMIN_PASSWORD`.
5. In VS Code, open the project folder and select Terminal → New Terminal.
6. Run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

7. Open http://127.0.0.1:5000

## Existing database

Do not run `schema.sql` against an existing database if you need to preserve its data. This ERD-only build has no `upgrade.sql` migration and does not use `app_user`. Back up your database before any schema changes.

## Demo data

The fresh-install schema includes starter hospital, department, doctor, medicine, staff, driver, bed, appointment, emergency-case and 50 fictional citizen records.

## Security notes

- Citizen passwords are stored as Werkzeug password hashes in `citizen.password_hash`.
- Administrator credentials are read from `.env`, not stored in a new database table.
- Keep `.env` private and never commit it.
- This is an academic demonstration project; production clinical deployment requires security, privacy, audit, backup and regulatory review.
