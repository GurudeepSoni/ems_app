🧑‍💼 Employee Management System (EMS)

A production-ready web application built using Flask and PostgreSQL to manage employee records with secure authentication and an admin-controlled system.

🔗 Live Demo
🌐 Web App: http://16.171.152.105:5000/admin_login
📂 Repository: https://github.com/GurudeepSoni/ems_app
🚀 Key Features
🔐 Secure Authentication
Password hashing for data security
OTP-based password recovery via email
🧾 Employee Management
Full CRUD operations (Add, Edit, Delete, View)
Efficient handling of 100+ employee records
🖼️ Profile Management
Employee profile photo upload and storage
🧑‍💻 Admin Dashboard
Centralized control panel for all operations
🔑 Access Control
Admin access code required for employee registration
Multi-user support
🛠️ Tech Stack
Backend: Python (Flask)
Frontend: HTML, CSS
Database: PostgreSQL
Authentication: Password Hashing + OTP Email Verification
⚙️ Installation & Setup
git clone https://github.com/GurudeepSoni/ems_app.git
cd ems_app
pip install -r requirements.txt
python app.py
🔐 Environment Configuration

Create a .env file or update your config:

SECRET_KEY=your_secret_key
DATABASE_URL=your_postgresql_url
EMAIL_USER=your_email
EMAIL_PASS=your_email_password
📁 Project Structure
ems_app/
├── static/        # CSS, images, uploads
├── templates/     # HTML templates
├── app.py         # Main application
├── models.py      # Database models
├── routes.py      # Routes & logic
├── config.py      # Configuration
└── requirements.txt
☁️ Deployment

Deployed on AWS EC2 with:

Gunicorn (WSGI server)
Nginx (reverse proxy)
PostgreSQL database

Ensures 24/7 availability and scalability.

📅 Project Duration

Nov 2026 – Dec 2026

📌 Future Improvements
Role-based access control (Admin / Employee)
Advanced filtering & search
REST API support
UI/UX enhancements
