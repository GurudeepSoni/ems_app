from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import random
##port smtplib
##import ssl
##from email.message import EmailMessage
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
import resend 


# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env (EMAIL_USER, EMAIL_PASS)
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
app.secret_key = "super-secret-key-change-me"

# PostgreSQL config
# password gunnu@123  =>  gunnu%40123 (URL encoded)


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

db = SQLAlchemy(app)

# Email credentials from .env
##EMAIL_USER = os.getenv("MAIL_USERNAME")
##EMAIL_PASS = os.getenv("MAIL_PASSWORD")
resend.api_key = os.getenv("RESEND_API_KEY")



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
    """
    Rule:
      - lowercase
      - first 4 letters of name
      - '@'
      - last 4 digits of phone
    Example: name='Missunderstand', phone='9876543210' -> 'miss@3210'
    """
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


##import smtplib
##from email.mime.text import MIMEText
##from email.mime.multipart import MIMEMultipart
import resend
import os

##res

# def send_otp_email(to_email, otp):
#     if not EMAIL_USER or not EMAIL_PASS:
#         print("❌ Email credentials missing")
#         return False

#     subject = "EMS Password Reset OTP"
#     body = f"""
# Hello,

# Your OTP for password reset is:

# 🔐 {otp}

# This OTP is valid for 5 minutes.
# Do not share it with anyone.

# — EMS Team
# """

#     msg = MIMEMultipart()
#     msg["From"] = EMAIL_USER
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.attach(MIMEText(body, "plain"))

#     try:
#         server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
#         server.ehlo()
#         server.starttls()
#         server.ehlo()
#         server.login(EMAIL_USER, EMAIL_PASS)
#         server.send_message(msg)
#         server.quit()
#         return True
#     except Exception as e:
#         print("❌ Email send error:", e)
#         return False

def send_otp_email(to_email, otp):
    try:
        resend.Emails.send({
            "from": "EMS <onboarding@gmail.com>",
            "to": [to_email],
            "subject": "EMS Password Reset OTP",
            "html": f"""
                <h2>Password Reset OTP</h2>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This OTP is valid for 5 minutes.</p>
            """
        })
        return True
    except Exception as e:
        print("❌ Resend error:", e)
        return False





# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("home.html")


# ---- OPTION A: COMPANY / ADMIN REGISTRATION ----
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

        # check email unique
        if Admin.query.filter_by(email=email).first():
            flash("Admin email already exists.", "danger")
            return redirect(url_for("create_company"))

        password_hashed = generate_password_hash(password_raw)

        # generate admin code from name + phone
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
        # show admin code, email, company name on success page
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

    # compute admin_code again for display
    admin_code = generate_admin_code(admin.name, admin.phone)

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        employees=employees,
        q=q,
        admin_code=admin_code,
    )


# ---- ADMIN: ADD EMPLOYEE ----
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
        alt_phone = request.form.get("alt_phone")
        alt_relation = request.form.get("alt_relation")
        marital_status = request.form.get("marital_status")
        blood_group = request.form.get("blood_group")
        gender = request.form.get("gender")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        password_raw = request.form.get("password")

        if not (name and email and password_raw):
            flash("Name, Email, Password are required.", "danger")
            return redirect(url_for("admin_add_employee"))

        if Employee.query.filter_by(email=email).first():
            flash("Employee email already exists.", "danger")
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
            alt_phone=alt_phone,
            alt_relation=alt_relation,
            marital_status=marital_status,
            blood_group=blood_group,
            gender=gender,
            city=city,
            state=state,
            address=address,
            photo=filename,
            password=generate_password_hash(password_raw),
        )
        db.session.add(emp)
        db.session.commit()
        flash("Employee added successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add_employee.html", admin=admin)


# ---- ADMIN: EDIT EMPLOYEE ----
@app.route("/admin_edit_employee/<int:emp_id>", methods=["GET", "POST"])
def admin_edit_employee(emp_id):
    admin = current_admin()
    if not admin:
        flash("Please login as admin.", "danger")
        return redirect(url_for("admin_login"))

    emp = Employee.query.get_or_404(emp_id)
    if emp.admin_id != admin.admin_id:
        flash("You cannot edit employees from another admin.", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        emp.name = request.form.get("name")
        emp.phone = request.form.get("phone")
        emp.alt_phone = request.form.get("alt_phone")
        emp.alt_relation = request.form.get("alt_relation")
        emp.marital_status = request.form.get("marital_status")
        emp.blood_group = request.form.get("blood_group")
        emp.gender = request.form.get("gender")
        emp.city = request.form.get("city")
        emp.state = request.form.get("state")
        emp.address = request.form.get("address")

        photo = request.files.get("photo")
        if photo and allowed_file(photo.filename):
            safe_name = f"{uuid.uuid4().hex}_{photo.filename}"
            emp.photo = safe_name
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], safe_name))

        db.session.commit()
        flash("Employee updated.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_edit_employee.html", admin=admin, emp=emp)


# ---- ADMIN: DELETE EMPLOYEE ----
@app.route("/admin_delete_employee/<int:emp_id>")
def admin_delete_employee(emp_id):
    admin = current_admin()
    if not admin:
        flash("Please login as admin.", "danger")
        return redirect(url_for("admin_login"))

    emp = Employee.query.get_or_404(emp_id)
    if emp.admin_id != admin.admin_id:
        flash("You cannot delete employees from another admin.", "danger")
        return redirect(url_for("admin_dashboard"))

    db.session.delete(emp)
    db.session.commit()
    flash("Employee deleted.", "info")
    return redirect(url_for("admin_dashboard"))


# ---- ADMIN: DELETE COMPANY + ADMIN + EMPLOYEES ----
@app.route("/admin_delete_company", methods=["POST"])
def admin_delete_company():
    admin = current_admin()
    if not admin:
        flash("Please login as admin.", "danger")
        return redirect(url_for("admin_login"))

    # delete all employees under this admin
    Employee.query.filter_by(admin_id=admin.admin_id).delete()
    # delete admin record
    db.session.delete(admin)
    db.session.commit()

    session.clear()
    flash("Company, admin profile and all employees deleted.", "info")
    return redirect(url_for("home"))


# ---- EMPLOYEE REGISTRATION (OPTION 2) ----
@app.route("/employee_register", methods=["GET", "POST"])
def employee_register():
    if request.method == "POST":
        admin_code = request.form.get("admin_code")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        alt_phone = request.form.get("alt_phone")
        alt_relation = request.form.get("alt_relation")
        marital_status = request.form.get("marital_status")
        blood_group = request.form.get("blood_group")
        gender = request.form.get("gender")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        password_raw = request.form.get("password")

        if not (admin_code and name and email and password_raw):
            flash("Admin ID, Name, Email, Password are required.", "danger")
            return redirect(url_for("employee_register"))

        # find admin by generating code for each admin and matching
        admins = Admin.query.all()
        matched_admin = None
        for a in admins:
            if generate_admin_code(a.name, a.phone) == admin_code.strip().lower():
                matched_admin = a
                break

        if not matched_admin:
            flash("Invalid Admin ID.", "danger")
            return redirect(url_for("employee_register"))

        if Employee.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("employee_register"))

        photo = request.files.get("photo")
        filename = None
        if photo and allowed_file(photo.filename):
            safe_name = f"{uuid.uuid4().hex}_{photo.filename}"
            filename = safe_name
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        emp = Employee(
            admin_id=matched_admin.admin_id,
            name=name,
            email=email,
            phone=phone,
            alt_phone=alt_phone,
            alt_relation=alt_relation,
            marital_status=marital_status,
            blood_group=blood_group,
            gender=gender,
            city=city,
            state=state,
            address=address,
            photo=filename,
            password=generate_password_hash(password_raw),
        )
        db.session.add(emp)
        db.session.commit()
        flash("Registration successful. Please login as employee.", "success")
        return redirect(url_for("employee_login"))

    return render_template("employee_register.html")


# ---- EMPLOYEE LOGIN ----
@app.route("/employee_login", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        email = request.form.get("email")
        password_raw = request.form.get("password")

        emp = Employee.query.filter_by(email=email).first()
        if emp and check_password_hash(emp.password, password_raw):
            session.clear()
            session["employee_id"] = emp.id
            flash("Logged in as employee.", "success")
            return redirect(url_for("employee_dashboard"))

        flash("Invalid employee credentials.", "danger")
    return render_template("employee_login.html")


# ---- EMPLOYEE DASHBOARD ----
@app.route("/employee_dashboard")
def employee_dashboard():
    emp = current_employee()
    if not emp:
        flash("Please login as employee.", "danger")
        return redirect(url_for("employee_login"))
    return render_template("employee_dashboard.html", emp=emp)


# ---- EMPLOYEE EDIT PROFILE ----
@app.route("/employee_edit", methods=["GET", "POST"])
def employee_edit():
    emp = current_employee()
    if not emp:
        flash("Please login as employee.", "danger")
        return redirect(url_for("employee_login"))

    if request.method == "POST":
        emp.name = request.form.get("name")
        emp.phone = request.form.get("phone")
        emp.alt_phone = request.form.get("alt_phone")
        emp.alt_relation = request.form.get("alt_relation")
        emp.marital_status = request.form.get("marital_status")
        emp.blood_group = request.form.get("blood_group")
        emp.gender = request.form.get("gender")
        emp.city = request.form.get("city")
        emp.state = request.form.get("state")
        emp.address = request.form.get("address")

        photo = request.files.get("photo")
        if photo and allowed_file(photo.filename):
            safe_name = f"{uuid.uuid4().hex}_{photo.filename}"
            emp.photo = safe_name
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], safe_name))

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("employee_dashboard"))

    return render_template("employee_edit.html", emp=emp)


# ---- FORGOT PASSWORD (REQUEST OTP) ----
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        role = request.form.get("role")  # 'admin' or 'employee'

        if role == "admin":
            user = Admin.query.filter_by(email=email).first()
        else:
            user = Employee.query.filter_by(email=email).first()

        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for("forgot_password"))

        otp = generate_otp(6)
        sent = send_otp_email(email, otp)
        if not sent:
            flash("Failed to send OTP email. Check email settings.", "danger")
            return redirect(url_for("forgot_password"))

        # store reset info in session
        session["reset_email"] = email
        session["reset_role"] = role
        session["reset_otp"] = otp

        flash("OTP sent to your email.", "success")
        return redirect(url_for("verify_otp"))

    # allow pre-select role via query param
    role = request.args.get("role", "employee")
    return render_template("forgot_password.html", role=role)


# ---- VERIFY OTP ----
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if "reset_email" not in session or "reset_otp" not in session:
        flash("Password reset session expired. Try again.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        entered = request.form.get("otp", "").strip()
        if entered == session.get("reset_otp"):
            session["reset_verified"] = True
            flash("OTP verified. Please set a new password.", "success")
            return redirect(url_for("reset_password"))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for("verify_otp"))

    return render_template("verify_otp.html")


# ---- RESET PASSWORD ----
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if (
        "reset_email" not in session
        or "reset_role" not in session
        or not session.get("reset_verified")
    ):
        flash("Password reset session expired. Try again.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_pass = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not new_pass or new_pass != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password"))

        email = session["reset_email"]
        role = session["reset_role"]
        hashed = generate_password_hash(new_pass)

        if role == "admin":
            admin = Admin.query.filter_by(email=email).first()
            if admin:
                admin.password = hashed
        else:
            emp = Employee.query.filter_by(email=email).first()
            if emp:
                emp.password = hashed

        db.session.commit()

        # clear reset session
        session.pop("reset_email", None)
        session.pop("reset_role", None)
        session.pop("reset_otp", None)
        session.pop("reset_verified", None)

        flash("Password updated. Please login.", "success")
        return redirect(url_for("home"))

    return render_template("reset_password.html")


# ---- LOGOUT ----
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("home"))


# ---- SERVE UPLOADS ----
@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    # don't call db.create_all() because tables already exist via SQL
    app.run(debug=True)













