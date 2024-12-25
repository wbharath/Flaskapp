# Flask Art Management Application

This is a Flask web application for managing an art collection, designed for NSCC Art Foundation. The application provides functionality for adding, updating, and viewing art entries, including information about artists, values, and images of the art pieces.

## Features

- User authentication (login, registration)
- **Form Sanitization**: Inputs are sanitized using `bleach` to prevent Cross-Site Scripting (XSS) attacks.
- **Image Uploads**: Art images are uploaded securely.
- Manage Art section accessible only by the **Webmaster** role.
- Role-based access control for managing sensitive features.
- **Rate Limiting** (upcoming): To protect sensitive routes like login and form submissions from DoS attacks.
- **Logging and Monitoring** (upcoming): To detect and respond to security incidents, like failed login attempts and unusual activity.

## Tech Stack

- **Backend**: Flask (Python), Flask-SQLAlchemy, Flask-WTF, MySQL
- **Frontend**: HTML, CSS (Bootstrap), JavaScript (for modals, form interactivity)
- **Database**: MySQL
- **Security**: Form sanitization (using `bleach`), role-based access, and (upcoming) rate limiting and logging

---
