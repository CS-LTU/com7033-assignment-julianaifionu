# Healthcare Stroke Management System

A secure, web-based Flask application designed to help healthcare professionals record, manage, and analyze patient data
to assess stroke risk.
Built with a strong focus on security, usability, and data privacy, the system supports role-based access for clinicians and
administrator in a hospital setting.

## Features

- Secure User Authentication

- Patient Data Management (Demographics, Medical History, Lifestyle)

- Admin Dashboard for reviewing system users and users records

- Clinician Dashboard for reviewing predictions and managing patient records

- Secure Session Handling & Input Validation

- Zero Trust Architecture and OWASP-aligned security practices

## System Architecture

#### The application follows a three-layered architecture aligned with SSDLC principles:

| Layer                  | Description                                            | Security Controls                                                                                                                        |
| ---------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Presentation Layer** | Flask HTML templates (Jinja2), forms, and Bootstrap UI | Input validation, CSRF protection                                                                                                        |
| **Application Layer**  | Flask backend (business logic, RBAC, authentication)   | RBAC, session management, exception handling                                                                                             |
| **Data Layer**         | SQLite (Auth), MongoDB (Patients Record)               | Encryption-at-rest (password, activation tokens), least privilege DB access, integrity checks, injection (SQL injection, XSS) prevention |

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

venv\Scripts\activate # Windows
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
- **STROKE_APP_SECRET_KEY** — a secure, randomly generated secret key

For development or testing, you may keep the default admin credentials or modify them as needed:

## Run the Application

```bash
# ensure you are in the project root
python app.py
```

Access it at 👉 http://localhost:3000/

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

## License

This project is released under the MIT License — free to use, modify, and distribute with attribution.

## Acknowledgements

World Health Organization (WHO) for the dataset

Flask communities for excellent documentation

LTU for the course module

Developed by [Juliana Ifionu](https://www.linkedin.com/in/julianaifionu/) as part of a secure software development
project under SSDLC principles.
