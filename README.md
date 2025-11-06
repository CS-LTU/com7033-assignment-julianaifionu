# Stroke Prediction Dashboard

A secure, web-based Flask application designed to help healthcare professionals record, manage, and analyze patient data
to assess stroke risk.
Built with a strong focus on security, usability, and data privacy, the system supports role-based access for nurses and
administrators in a hospital setting.

## Features

- 🔐 Secure User Authentication (Nurses, Doctor, Admin)

- 🧾 Patient Data Management (Demographics, Medical History, Lifestyle)

- 📊 Doctor Dashboard for reviewing predictions and managing patient records

- 💬 Nurse Panel for updating patient medical and lab information

- 🛡️ Secure Session Handling & Input Validation

- 💡 Zero Trust Architecture and OWASP-aligned security practices

## System Architecture

#### The application follows a three-layered architecture aligned with SSDLC principles:

| Layer                  | Description                                            | Security Controls                                               |
|------------------------|--------------------------------------------------------|-----------------------------------------------------------------|
| **Presentation Layer** | Flask HTML templates (Jinja2), forms, and Bootstrap UI | Input validation, CSRF protection                               |
| **Application Layer**  | Flask backend (business logic, RBAC, authentication)   | RBAC, session management, exception handling, JWT validation    |
| **Data Layer**         | SQLite (Auth), MongoDB (Medical, Analytics)            | Encryption-at-rest, least privilege DB access, integrity checks |

## Tech Stack

| Category           | Technology                                                |
|--------------------|-----------------------------------------------------------|
| **Framework**      | Flask (Python 3.11)                                       |
| **Frontend**       | HTML5, Bootstrap 5, Jinja2 Templates                      |
| **Databases**      | SQLite (auth), MongoDB (medical)                          |
| **Authentication** | Flask-WTF, WTForms, bcrypt                                |
| **Security**       | CSRF, XSS protection, RBAC, environment-based secret keys |
| **Environment**    | Python Virtualenv (`venv`)                                |
| **Dev Tools**      | Black (formatter), Pytest (testing)                       |

## Installation & Setup

```bash
# Clone the Repository
git clone https://github.com/CS-LTU/com7033-assignment-julianaifionu.git
cd com7033-assignment-julianaifionu

# Create & Activate Virtual Environment
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# Install Dependencies
pip install -r requirements.txt

# Configure Environment Variables
export STROKE_APP_SECRET_KEY="your_random_secret_key"
```

## Run the Application

```bash
flask --app app run --debug
```

Access it at 👉 http://127.0.0.1:3000

## License

This project is released under the MIT License — free to use, modify, and distribute with attribution.

## Acknowledgements

World Health Organization (WHO) for the dataset

Flask communities for excellent documentation

LTU for the course module

Developed by [Juliana Ifionu](https://www.linkedin.com/in/julianaifionu/) as part of a secure software development
project under SSDLC principles.