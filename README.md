# Healthcare Stroke Management System

A secure, web-based Flask application designed to help healthcare professionals record, manage, and analyze patient data
to assess stroke risk.
Built with a strong focus on security, usability, and data privacy, the system supports role-based access for clinicians and
administrator in a hospital setting.

## Features

- Secure User Authentication

- Secure Patient Data Management (Demographics, Medical History, Lifestyle)

- Admin Dashboard for reviewing system users and users records

- Clinician Dashboard for reviewing patients and managing patient records

- Secure Session Handling & Input Validation

- SQLite DB for user record and authentication

- MongoDB for patient record management

- CRUD on users and patients

- Zero Trust Architecture and OWASP-aligned security practices

## System Architecture

#### The application follows a three-layered architecture aligned with SSDLC principles:

| Layer                  | Description                                            | Security Controls                                                                                                                                |
| ---------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Presentation Layer** | Flask HTML templates (Jinja2), forms, and Bootstrap UI | Input validation, CSRF protection, XSS prevention                                                                                                |
| **Application Layer**  | Flask backend (business logic, RBAC, authentication)   | RBAC, session management, exception handling, patient record encryption at rest                                                                  |
| **Data Layer**         | SQLite (Auth), MongoDB (Patients Record)               | Encryption-at-rest (password, activation tokens, patient medical records), least privilege DB access, integrity checks, SQL injection prevention |

## Tech Stack

| Category           | Technology                                                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **Framework**      | Flask (Python 3.11)                                                                                              |
| **Frontend**       | HTML5, Bootstrap 5, Jinja2 Templates                                                                             |
| **Databases**      | SQLite (auth), MongoDB (patients record)                                                                         |
| **Authentication** | session, bcrypt, CSRF                                                                                            |
| **Security**       | CSRF, XSS prevention, bcrypt, AES-256, Encryption at rest, input validation, RBAC, environment-based secret keys |
| **Environment**    | Python Virtual env (`venv`)                                                                                      |
| **Dev Tools**      | Black (formatter), Pytest & Unittest (testing)                                                                   |

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/CS-LTU/com7033-assignment-julianaifionu.git

# Go to project directory
cd com7033-assignment-julianaifionu
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv

source venv/bin/activate # macOS/Linux

source venv/Scripts/activate # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Create a `.env` file in the **root** of the project.
2. Copy the contents of `.env.example` into your new `.env` file.
3. Update the following values:

- **MONGO_URI** — your MongoDB connection string
- **STROKE_APP_SECRET_KEY** — a secure, randomly generated secret key (hex (32 bytes)) or for testing purpose, you may use the default value

NOTE: For development or testing, you may keep the default admin credentials and secret key or modify them as needed:

## Run the Application

```bash
# ensure you are in the project root
python app.py
```

Access it at 👉 http://localhost:3000/

## UI Functionality Test

The application has three main roles: **Admin**, **Clinician**, and **Auditor**. Below are the steps and expected functionalities for each role.

---

### Pre-requisite
- Login as an admin (the admin account is seeded automatically when the app starts and SQLite tables are created).  
- Use the admin credentials set in the environment variables (`ADMIN_USERNAME` and `ADMIN_PASSWORD`).

---

### 1. Admin User
- Can **create new users** and assign roles (e.g., clinician, auditor).  
- Can **invite users**.  
- Can **delete users**, but **cannot delete the admin account**.  
- Can **view user statistics**.  
- Cannot perform any actions on patients (RBAC enforced).

---

### 2. Clinician User
- Can **create patients**.  
- Can **perform CRUD operations** on patient records.  
- Patient records **store sensitive medical information encrypted at rest**.  
- Can **view and analyze patient statistics**.  
- Cannot perform any actions on users (RBAC enforced).

---

### 3. Auditor
- Can **view system logs only**.  
- Cannot perform any actions on users or patient records (RBAC enforced).



## Run all Tests

```bash
pytest -q
```

## Entity Relationship Diagram for SQLite DB

![ERD](screenshots/erd.png)

## MongoDB Schema Diagram

**Collection:** `patients`

| Field             | Type          | Description                            |
| ----------------- | ------------- | -------------------------------------- |
| \_id              | ObjectId      | Primary key                            |
| first_name        | string        | Patient's first name                   |
| last_name         | string        | Patient's last name                    |
| gender            | string        | Gender                                 |
| age               | int           | Age (derived from DOB)                 |
| hypertension      | int (0/1)     | Hypertension indicator                 |
| heart_disease     | int (0/1)     | Heart disease indicator                |
| ever_married      | string        | Marital status                         |
| work_type         | string        | Type of work                           |
| residence_type    | string        | Urban/Rural                            |
| avg_glucose_level | float         | Glucose level                          |
| bmi               | float/null    | Body Mass Index (nullable)             |
| smoking_status    | string        | Smoking category                       |
| stroke            | int (0/1)     | Stroke history indicator               |
| created_by        | int           | Foreign reference to SQLite `users.id` |
| created_at        | datetime      | Timestamp when created                 |
| updated_at        | datetime/null | Timestamp when updated                 |

---

**Collection:** `logs`

| Field   | Type     | Description                     |
| ------- | -------- | ------------------------------- |
| \_id    | ObjectId | Primary key                     |
| action  | string   | Description of the action taken |
| details | object   | Metadata about the action       |
| ts      | datetime | Timestamp of the logged event   |

## Issues

If you find a bug or want to suggest an improvement:

1. Go to the **Issues** tab of the repository.
2. Click **New Issue**.
3. Describe the problem clearly (what happened, expected behaviour, steps to reproduce).
4. Add screenshots or logs if useful.
5. Submit the issue.

Your feedback helps improve the project!

## License

This project is released under the MIT License — free to use, modify, and distribute with attribution.

## Acknowledgements

World Health Organization (WHO) for the dataset

Flask communities for excellent documentation

LTU for the course module

Developed by [Juliana Ifionu](https://www.linkedin.com/in/julianaifionu/) as part of a secure software development
project under SSDLC principles.
