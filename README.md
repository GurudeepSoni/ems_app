Employee Management System (EMS)

A Flask-based web application to manage employee records with secure authentication and admin-controlled access.

Features
Admin dashboard for managing employees
Add, edit, delete, and view employee details
Profile photo upload support
Secure login with password hashing
OTP-based password recovery via email
Admin access code for employee registration
Supports 100+ employee records
Tech Stack
Python (Flask)
HTML, CSS
PostgreSQL
Installation
git clone https://github.com/your-username/ems-project.git
cd ems-project
pip install -r requirements.txt
python app.py
Configuration

Update your database and email settings in config.py or use environment variables:

DATABASE_URL=your_postgresql_url
SECRET_KEY=your_secret_key
EMAIL_USER=your_email
EMAIL_PASS=your_email_password
Usage
Run the app and open http://127.0.0.1:5000/
Login as admin
Manage employees from the dashboard
Deployment

Deployed on AWS (EC2 + PostgreSQL)

Project Structure
EMS/
├── static/
├── templates/
├── app.py
├── models.py
├── routes.py
├── config.py
└── requirements.txt
