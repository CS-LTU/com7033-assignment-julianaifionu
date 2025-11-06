# Project Planning

## Stakeholders

| Role       | Description                                          |
|------------|------------------------------------------------------|
| **Nurse**  | Create, Read, Update, Delete patient data            |
| **Doctor** | Views analytics                                      |
| **Admin**  | Manages user accounts and access permissions and los |

## Security Highlights

- Environment-based Secret Key (not hardcoded)

- Session Token Security with role-based payloads

- CSRF protection for all form submissions

- Secure Password Hashing (bcrypt)

- Role-Based Access Control (RBAC) for Nurses, Doctors, Admin

- Input Sanitization and Validation

- At-Rest Encryption for sensitive data

- Audit Logging for access events