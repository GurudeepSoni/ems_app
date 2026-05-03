# 🧑‍💼 EMPLOYEE MANAGEMENT SYSTEM (EMS)

***A production-ready web application built using Flask and PostgreSQL to manage employee records with secure authentication and admin-controlled access.***

---

## 🔗 ***LIVE DEMO***

- 🌐 ***Web App:*** http://16.171.152.105:5000/admin_login  
- 📂 ***Repository:*** https://github.com/GurudeepSoni/ems_app  

---

## 🚀 ***FEATURES***

- 🔐 ***Secure Authentication***
  - Password hashing for secure login  
  - OTP-based password recovery via email  

- 🧾 ***Employee Management***
  - Full CRUD operations (Add, Edit, Delete, View)  
  - Handles 100+ employee records efficiently  

- 🖼️ ***Profile Management***
  - Upload and manage employee profile photos  

- 🧑‍💻 ***Admin Dashboard***
  - Centralized panel for all operations  

- 🔑 ***Access Control***
  - Admin access code required for registration  
  - Supports multiple users  

---

## 🛠️ ***TECH STACK***

- ***Backend:*** Python (Flask)  
- ***Frontend:*** HTML, CSS  
- ***Database:*** PostgreSQL  
- ***Authentication:*** Password Hashing + OTP Verification  

---

## ⚙️ ***INSTALLATION***

```bash
git clone https://github.com/GurudeepSoni/ems_app.git
cd ems_app
pip install -r requirements.txt
python app.py
🔐 CONFIGURATION

Create a .env file or update config:

SECRET_KEY=your_secret_key
DATABASE_URL=your_postgresql_url
EMAIL_USER=your_email
EMAIL_PASS=your_email_password
📁 PROJECT STRUCTURE
ems_app/
├── static/
├── templates/
├── app.py
├── models.py
├── routes.py
├── config.py
└── requirements.txt
☁️ DEPLOYMENT

Deployed on AWS EC2 using:

Gunicorn
Nginx
PostgreSQL
📅 DURATION

Nov 2026 – Dec 2026

📌 FUTURE IMPROVEMENTS
Role-based access control
Advanced search & filters
REST API integration
UI improvements
