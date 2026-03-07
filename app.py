import os
import uuid
import random
import smtplib
import ssl
from email.message import EmailMessage
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_from_directory,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env (EMAIL_USER, EMAIL_PASS)
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)

# secret key from environment
app.secret_key = os.environ.get("SECRET_KEY")

# PostgreSQL config (Render will provide DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

db = SQLAlchemy(app)

# Email credentials from environment
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


# ---------- MODELS ----------
class Admin(db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200))


class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.admin_id"))
    name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    alt_phone = db.Column(db.String(20))
    alt_relation = db.Column(db.String(50))
    marital_status = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))
    gender = db.Column(db.String(20))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    address = db.Column(db.Text)
    photo = db.Column(db.String(255))
    password = db.Column(db.String(200))


# ---------- HELPERS ----------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def generate_admin_code(name: str, phone: str) -> str:
    name_part = name.strip().lower()[:4] if name else "admin"
    digits = "".join(ch for ch in phone if ch.isdigit()) if phone else ""
    phone_part = digits[-4:] if len(digits) >= 4 else digits
    if not phone_part:
        phone_part = "0000"
    return f"{name_part}@{phone_part}"


def current_admin():
    admin_id = session.get("admin_id")
    if not admin_id:
        return None
    return Admin.query.get(admin_id)


def current_employee():
    emp_id = session.get("employee_id")
    if not emp_id:
        return None
    return Employee.query.get(emp_id)


def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def send_otp_email(to_email: str, otp: str) -> bool:
    if not EMAIL_USER or not EMAIL_PASS:
        print("EMAIL_USER or EMAIL_PASS not set")
        return False

    msg = EmailMessage()
    msg["Subject"] = "EMS Password Reset OTP"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(
        f"Your OTP for resetting your EMS password is: {otp}\n\n"
        "This code is valid for a short time. If you did not request this, please ignore this email."
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False


# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("home.html")


# ---- COMPANY / ADMIN REGISTRATION ----
@app.route("/create_company", methods=["GET", "POST"])
def create_company():
    if request.method == "POST":
        company_name = request.form.get("company_name")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password_raw = request.form.get("password")

        if not (company_name and name and email and phone and password_raw):
            flash("Please fill all fields.", "danger")
            return redirect(url_for("create_company"))

        if Admin.query.filter_by(email=email).first():
            flash("Admin email already exists.", "danger")
            return redirect(url_for("create_company"))

        password_hashed = generate_password_hash(password_raw)

        admin_code = generate_admin_code(name, phone)

        new_admin = Admin(
            company_name=company_name,
            name=name,
            email=email,
            phone=phone,
            password=password_hashed,
        )
        db.session.add(new_admin)
        db.session.commit()

        flash("Company & Admin created successfully!", "success")

        return render_template(
            "company_success.html",
            admin=new_admin,
            admin_code=admin_code,
        )

    return render_template("create_company.html")


# ---- ADMIN LOGIN ----
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password_raw = request.form.get("password")

        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password_raw):
            session.clear()
            session["admin_id"] = admin.admin_id
            flash("Logged in as Admin.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")


# ---- ADMIN DASHBOARD ----
@app.route("/admin_dashboard")
def admin_dashboard():
    admin = current_admin()
    if not admin:
        flash("Please login as admin.", "danger")
        return redirect(url_for("admin_login"))

    q = request.args.get("q", "").strip()

    query = Employee.query.filter_by(admin_id=admin.admin_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Employee.name.ilike(like),
                Employee.email.ilike(like),
                Employee.phone.ilike(like),
            )
        )
    employees = query.order_by(Employee.id.desc()).all()

    admin_code = generate_admin_code(admin.name, admin.phone)

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        employees=employees,
        q=q,
        admin_code=admin_code,
    )


# ---- ADMIN ADD EMPLOYEE ----
@app.route("/admin_add_employee", methods=["GET", "POST"])
def admin_add_employee():
    admin = current_admin()
    if not admin:
        flash("Please login as admin.", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password_raw = request.form.get("password")

        if not (name and email and password_raw):
            flash("Name, Email, Password are required.", "danger")
            return redirect(url_for("admin_add_employee"))

        photo = request.files.get("photo")
        filename = None
        if photo and allowed_file(photo.filename):
            safe_name = f"{uuid.uuid4().hex}_{photo.filename}"
            filename = safe_name
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        emp = Employee(
            admin_id=admin.admin_id,
            name=name,
            email=email,
            phone=phone,
            photo=filename,
            password=generate_password_hash(password_raw),
        )

        db.session.add(emp)
        db.session.commit()

        flash("Employee added successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add_employee.html", admin=admin)


# ---- FORGOT PASSWORD (OTP) ----
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        role = request.form.get("role")

        user = (
            Admin.query.filter_by(email=email).first()
            if role == "admin"
            else Employee.query.filter_by(email=email).first()
        )

        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("forgot_password"))

        otp = generate_otp()
        sent = send_otp_email(email, otp)

        if not sent:
            flash("Failed to send OTP email.", "danger")
            return redirect(url_for("forgot_password"))

        session["reset_email"] = email
        session["reset_role"] = role
        session["reset_otp"] = otp

        flash("OTP sent to your email.", "success")
        return redirect(url_for("verify_otp"))

    return render_template("forgot_password.html")


# ---- VERIFY OTP ----
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered = request.form.get("otp")

        if entered == session.get("reset_otp"):
            session["reset_verified"] = True
            return redirect(url_for("reset_password"))

        flash("Invalid OTP", "danger")

    return render_template("verify_otp.html")


# ---- RESET PASSWORD ----
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_pass = request.form.get("password")

        email = session.get("reset_email")
        role = session.get("reset_role")

        hashed = generate_password_hash(new_pass)

        if role == "admin":
            admin = Admin.query.filter_by(email=email).first()
            admin.password = hashed
        else:
            emp = Employee.query.filter_by(email=email).first()
            emp.password = hashed

        db.session.commit()

        session.clear()

        flash("Password updated", "success")
        return redirect(url_for("home"))

    return render_template("reset_password.html")


# ---- LOGOUT ----
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---- SERVE UPLOADS ----
@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
