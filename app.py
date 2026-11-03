import os
from datetime import date, datetime
from decimal import Decimal
from functools import wraps

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from config.db import get_connection

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 28800

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def roles_required(*roles):
    def deco(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if session.get("role") not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return deco

@app.before_request
def security_guard():
    if request.endpoint in ("login", "register", "static") or request.path == "/health":
        return
    if not session.get("user_id"):
        return redirect(url_for("login", next=request.path))
    if request.method == "POST":
        import hmac
        if not session.get("_csrf") or not hmac.compare_digest(session["_csrf"], request.form.get("_csrf", "")):
            abort(400, "Invalid form security token.")

@app.context_processor
def security_context():
    import secrets
    session.setdefault("_csrf", secrets.token_urlsafe(32))
    return {"csrf_token": session["_csrf"], "current_user": session.get("username"),
            "current_role": session.get("role"), "role_modules": ROLE_MODULES.get(session.get("role"), set())}


# Tables and editable fields follow the supplied ER diagram.
# Foreign keys are represented as dropdowns populated from the referenced table.
MODULES = {
    "citizen": {
        "title": "Citizens", "pk": "citizen_id",
        "fields": [
            ("name","Full name","text",True),("phone","Phone","tel",False),
            ("email","Email","email",False),("address","Address","textarea",False),
            ("date_of_birth","Date of birth","date",False),("gender","Gender","select:Male,Female,Other",False),
            ("medical_history","Medical history","textarea",False),
        ]},
    "medical_history": {
        "title":"Medical History","pk":"history_id",
        "fields":[("citizen_id","Citizen","fk:citizen:citizen_id:name",True),
                  ("condition","Condition","text",True),("allergies","Allergies","textarea",False),
                  ("chronic_issues","Chronic issues","textarea",False),("notes","Notes","textarea",False)]},
    "appointment": {
        "title":"Appointments","pk":"appointment_id",
        "fields":[("citizen_id","Citizen","fk:citizen:citizen_id:name",True),
                  ("doctor_id","Doctor","fk:doctor:doctor_id:name",True),
                  ("hospital_id","Hospital","fk:hospital:hospital_id:name",True),
                  ("department_id","Department","fk:department:department_id:name",True),
                  ("appointment_date","Appointment date","datetime-local",True),
                  ("status","Status","select:Booked,Confirmed,Completed,Cancelled",True),
                  ("document_time","Document / visit time","time",False),("reason","Reason","textarea",False)]},
    "doctor": {
        "title":"Doctors","pk":"doctor_id",
        "fields":[("name","Doctor name","text",True),("specialization","Specialization","text",True),
                  ("phone","Phone","tel",False),("department_id","Department","fk:department:department_id:name",False),
                  ("experience_years","Experience (years)","number",False),
                  ("availability_status","Availability","select:Available,Unavailable,On Leave",True)]},
    "department": {
        "title":"Departments","pk":"department_id",
        "fields":[("name","Department name","text",True),("description","Description","textarea",False),
                  ("head_doctor_id","Head doctor","fk:doctor:doctor_id:name",False)]},
    "prescription": {
        "title":"Prescriptions","pk":"prescription_id",
        "fields":[("appointment_id","Appointment","fk:appointment:appointment_id:appointment_id",True),
                  ("doctor_id","Doctor","fk:doctor:doctor_id:name",True),
                  ("medicine_id","Medicine","fk:medicine:medicine_id:name",True),
                  ("dosage","Dosage","text",True),("advice","Advice","textarea",False),("date","Date","date",True)]},
    "medicine": {
        "title":"Medicines","pk":"medicine_id",
        "fields":[("name","Medicine name","text",True),("generic_name","Generic name","text",False),
                  ("dosage_form","Dosage form","text",False),("description","Description","textarea",False)]},
    "hospital": {
        "title":"Hospitals","pk":"hospital_id",
        "fields":[("name","Hospital name","text",True),("type","Type","text",False),
                  ("location","Location","textarea",False),("phone","Phone","tel",False),
                  ("total_beds","Total beds","number",False),("facilities","Facilities","textarea",False),
                  ("contact_person","Contact person","text",False),("city_id","City","fk:city:city_id:name",False)]},
    "bed": {
        "title":"Beds","pk":"bed_id",
        "fields":[("hospital_id","Hospital","fk:hospital:hospital_id:name",True),
                  ("bed_type","Bed type","text",True),("status","Status","select:Available,Occupied,Maintenance",True)]},
    "staff": {
        "title":"Staff","pk":"staff_id",
        "fields":[("hospital_id","Hospital","fk:hospital:hospital_id:name",True),
                  ("name","Staff name","text",True),("role","Role","text",True),("shift","Shift","select:Morning,Evening,Night,Rotational",False)]},
    "city": {
        "title":"Cities","pk":"city_id",
        "fields":[("name","City name","text",True),("area","Area / region","text",False)]},
    "driver": {
        "title":"Drivers","pk":"driver_id",
        "fields":[("name","Driver name","text",True),("phone","Phone","tel",False),
                  ("license_no","License number","text",True),
                  ("availability_status","Availability","select:Available,Unavailable",False)]},
    "ambulance": {
        "title":"Ambulances","pk":"ambulance_id",
        "fields":[("vehicle_no","Vehicle number","text",True),("driver_id","Driver","fk:driver:driver_id:name",False),
                  ("staff_id","Assigned staff","fk:staff:staff_id:name",False),("location","Location","text",False),
                  ("phone","Phone","tel",False),("case_id","Emergency case","fk:emergency_case:case_id:case_id",False)]},
    "emergency_case": {
        "title":"Emergency Cases","pk":"case_id",
        "fields":[("citizen_id","Citizen","fk:citizen:citizen_id:name",True),
                  ("type","Case type","text",True),("severity","Severity","select:Low,Medium,High,Critical",True),
                  ("description","Description","textarea",False),("time_reported","Time reported","datetime-local",False),
                  ("status","Status","select:Reported,Assigned,In Progress,Resolved,Closed",True)]},
}



# Authentication follows the supplied 14-entity ERD exactly.
# Admin credentials come from .env; citizen credentials use citizen.email/password_hash.
ROLE_MODULES = {
    "admin": set(MODULES.keys()),
    "citizen": {"appointment", "medical_history", "prescription", "emergency_case"},
}
ROLE_WRITES = {
    "admin": set(MODULES.keys()),
    "citizen": {"appointment", "emergency_case"},
}
def enforce_module_access(table, write=False):
    role = session.get("role")
    allowed = ROLE_WRITES if write else ROLE_MODULES
    if role not in allowed or table not in allowed[role]:
        abort(403)

# Safe SQL identifiers: only names declared in MODULES are accepted.
def query_all(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()

def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        result = cur.lastrowid
        cur.close()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def module_or_404(table):
    if table not in MODULES:
        abort(404)
    return MODULES[table]

def get_options(field_type):
    if not field_type.startswith("fk:"):
        return []
    _, table, pk, label = field_type.split(":")
    if table not in MODULES:
        return []
    return query_all(f"SELECT `{pk}` AS id, `{label}` AS label FROM `{table}` ORDER BY 2")

def form_fields(table, values=None):
    values = values or {}
    result = []
    for name, label, kind, required in MODULES[table]["fields"]:
        result.append({
            "name": name, "label": label, "kind": kind, "required": required,
            "value": values.get(name, ""),
            "options": get_options(kind) if kind.startswith("fk:") else [],
        })
    return result

def clean_value(kind, value):
    value = value.strip() if isinstance(value, str) else value
    if value == "":
        return None
    if kind == "password":
        return generate_password_hash(value)
    if kind == "datetime-local":
        return value.replace("T", " ") + (":00" if len(value) == 16 else "")
    return value

@app.context_processor
def inject_globals():
    return {"modules": MODULES}

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        identity = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "")
        if identity == admin_username and admin_password and password == admin_password:
            session.clear()
            session.update(user_id="admin", username=admin_username, role="admin")
            session.permanent = True
            return redirect(request.args.get("next") or url_for("dashboard"))
        # Citizen email is the login identifier; no extra username/table is needed.
        rows = query_all("SELECT citizen_id,name,email,password_hash FROM citizen WHERE email=%s LIMIT 1", (identity,))
        if rows and rows[0].get("password_hash") and check_password_hash(rows[0]["password_hash"], password):
            session.clear()
            session.update(user_id=f"citizen:{rows[0]['citizen_id']}", username=rows[0]["name"],
                           role="citizen", citizen_id=rows[0]["citizen_id"])
            session.permanent = True
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Invalid email/username or password.", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Public citizen registration stored only in the ERD's citizen entity."""
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip().lower() or None
        address = request.form.get("address", "").strip() or None
        dob = request.form.get("date_of_birth", "").strip() or None
        gender = request.form.get("gender", "Other")
        if len(name) < 2:
            flash("Please enter your full name.", "error")
        elif not email:
            flash("Email is required because it is your login ID.", "error")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif gender not in ("Male", "Female", "Other"):
            flash("Please select a valid gender.", "error")
        else:
            conn = get_connection()
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO citizen(name,phone,email,address,date_of_birth,gender,password_hash) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                            (name, phone, email, address, dob, gender, generate_password_hash(password)))
                conn.commit()
                cur.close()
                flash("Citizen account created. Sign in using your email and password.", "success")
                return redirect(url_for("login"))
            except mysql.connector.IntegrityError:
                conn.rollback()
                flash("That email address is already registered. Please sign in or use another email.", "error")
            except mysql.connector.Error as e:
                conn.rollback()
                flash("Registration failed: " + e.msg, "error")
            finally:
                conn.close()
    return render_template("register.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def dashboard():
    counts = {}
    for table, meta in MODULES.items():
        if table not in ROLE_MODULES.get(session.get("role"), set()):
            continue
        try:
            counts[table] = query_all(f"SELECT COUNT(*) AS n FROM `{table}`")[0]["n"]
        except mysql.connector.Error:
            counts[table] = "—"
    recent = []
    try:
        recent = query_all("""SELECT a.appointment_id, c.name AS citizen, d.name AS doctor,
                              a.appointment_date, a.status
                              FROM appointment a
                              LEFT JOIN citizen c ON c.citizen_id=a.citizen_id
                              LEFT JOIN doctor d ON d.doctor_id=a.doctor_id
                              ORDER BY a.appointment_date DESC LIMIT 8""")
    except mysql.connector.Error:
        pass
    if session.get("role") == "citizen":
        recent = query_all("""SELECT a.appointment_id,c.name citizen,d.name doctor,a.appointment_date,a.status
            FROM appointment a LEFT JOIN citizen c ON c.citizen_id=a.citizen_id
            LEFT JOIN doctor d ON d.doctor_id=a.doctor_id WHERE a.citizen_id=%s
            ORDER BY a.appointment_date DESC LIMIT 8""", (session.get("citizen_id"),))
    elif session.get("role") == "doctor" and session.get("doctor_id"):
        recent = query_all("""SELECT a.appointment_id,c.name citizen,d.name doctor,a.appointment_date,a.status
            FROM appointment a LEFT JOIN citizen c ON c.citizen_id=a.citizen_id
            LEFT JOIN doctor d ON d.doctor_id=a.doctor_id WHERE a.doctor_id=%s
            ORDER BY a.appointment_date DESC LIMIT 8""", (session.get("doctor_id"),))
    return render_template("dashboard.html", counts=counts, recent=recent)

@app.route("/modules")
@login_required
def module_index():
    return render_template("modules.html")

@app.route("/<table>")
@login_required
def list_records(table):
    meta = module_or_404(table)
    enforce_module_access(table)
    search = request.args.get("q", "").strip()
    pk = meta["pk"]
    display_fields = [f[0] for f in meta["fields"][:4]]
    select_cols = [f"`{pk}`"]
    for col in display_fields:
        select_cols.append(f"`{col}`")
    where = ""
    params = []
    role = session.get("role")
    if role == "citizen":
        citizen_id = session.get("citizen_id")
        if not citizen_id:
            abort(403, "Citizen account is not linked to a citizen record.")
        if table == "appointment":
            where = " WHERE `citizen_id`=%s"; params.append(citizen_id)
        elif table == "medical_history":
            where = " WHERE `citizen_id`=%s"; params.append(citizen_id)
        elif table == "emergency_case":
            where = " WHERE `citizen_id`=%s"; params.append(citizen_id)
        elif table == "prescription":
            where = " WHERE `appointment_id` IN (SELECT appointment_id FROM appointment WHERE citizen_id=%s)"
            params.append(citizen_id)
    elif role == "doctor":
        doctor_id = session.get("doctor_id")
        if not doctor_id:
            abort(403, "Doctor account is not linked to a doctor record.")
        if table == "appointment":
            where = " WHERE `doctor_id`=%s"; params.append(doctor_id)
        elif table == "prescription":
            where = " WHERE `doctor_id`=%s"; params.append(doctor_id)
        elif table == "medical_history":
            where = " WHERE `citizen_id` IN (SELECT citizen_id FROM appointment WHERE doctor_id=%s)"
            params.append(doctor_id)
        elif table == "citizen":
            where = " WHERE `citizen_id` IN (SELECT citizen_id FROM appointment WHERE doctor_id=%s)"
            params.append(doctor_id)
    if search:
        searchable = [pk] + display_fields
        search_clause = "(" + " OR ".join(f"CAST(`{c}` AS CHAR) LIKE %s" for c in searchable) + ")"
        where = (where + " AND " if where else " WHERE ") + search_clause
        params += [f"%{search}%"] * len(searchable)
    rows = query_all(f"SELECT {', '.join(select_cols)} FROM `{table}`{where} ORDER BY `{pk}` DESC LIMIT 250", params)
    columns = [pk] + display_fields
    return render_template("list.html", table=table, meta=meta, rows=rows, columns=columns, search=search)

@app.route("/<table>/new", methods=["GET","POST"])
@roles_required("admin", "citizen")
def create_record(table):
    meta = module_or_404(table)
    enforce_module_access(table, write=True)
    fields = form_fields(table)
    if session.get("role") == "citizen" and table == "appointment":
        fields = [f for f in fields if f["name"] != "status"]
    if request.method == "POST":
        names, values = [], []
        insert_fields = form_fields(table)
        for f in insert_fields:
            raw_value = request.form.get(f["name"], "")
            if session.get("role") == "citizen" and f["name"] == "citizen_id":
                raw_value = str(session.get("citizen_id") or "")
            if session.get("role") == "citizen" and table == "appointment" and f["name"] == "status":
                raw_value = "Booked"
            if session.get("role") == "doctor" and f["name"] == "doctor_id":
                raw_value = str(session.get("doctor_id") or "")
            value = clean_value(f["kind"], raw_value)
            if f["required"] and value is None:
                flash(f'{f["label"]} is required.', "error")
                return render_template("form.html", table=table, meta=meta, fields=form_fields(table, request.form), editing=False)
            if f["kind"] == "password" and value is None:
                continue
            names.append(f["name"]); values.append(value)
        try:
            cols = ", ".join(f"`{n}`" for n in names)
            placeholders = ", ".join(["%s"] * len(names))
            execute(f"INSERT INTO `{table}` ({cols}) VALUES ({placeholders})", values)
            flash(f'{meta["title"][:-1] if meta["title"].endswith("s") else meta["title"]} added successfully.', "success")
            return redirect(url_for("list_records", table=table))
        except mysql.connector.Error as e:
            flash(f"Database error: {e.msg}", "error")
    return render_template("form.html", table=table, meta=meta, fields=fields, editing=False)

@app.route("/<table>/<int:record_id>/edit", methods=["GET","POST"])
@roles_required("admin", "citizen")
def edit_record(table, record_id):
    meta = module_or_404(table)
    enforce_module_access(table, write=True)
    pk = meta["pk"]
    current = query_all(f"SELECT * FROM `{table}` WHERE `{pk}`=%s", (record_id,))
    if not current:
        abort(404)
    current = current[0]
    if session.get("role") == "citizen" and table == "appointment":
        abort(403, "Citizens can submit appointment requests but cannot edit or approve them. Please contact hospital staff for changes.")
    if session.get("role") == "citizen":
        owner_id = session.get("citizen_id")
        if table in ("appointment", "medical_history", "emergency_case") and current.get("citizen_id") != owner_id:
            abort(403)
        if table == "prescription" and not query_all("SELECT appointment_id FROM appointment WHERE appointment_id=%s AND citizen_id=%s", (current.get("appointment_id"), owner_id)):
            abort(403)
    if session.get("role") == "doctor" and table in ("appointment", "prescription") and current.get("doctor_id") != session.get("doctor_id"):
        abort(403)
    fields = form_fields(table, current)
    if request.method == "POST":
        sets, values = [], []
        for f in fields:
            raw = request.form.get(f["name"], "")
            if session.get("role") == "citizen" and f["name"] == "citizen_id":
                raw = str(session.get("citizen_id") or "")
            if session.get("role") == "doctor" and f["name"] == "doctor_id":
                raw = str(session.get("doctor_id") or "")
            if f["kind"] == "password" and not raw:
                continue
            value = clean_value(f["kind"], raw)
            if f["required"] and value is None:
                flash(f'{f["label"]} is required.', "error")
                return render_template("form.html", table=table, meta=meta, fields=form_fields(table, request.form), editing=True, record_id=record_id)
            sets.append(f'`{f["name"]}`=%s'); values.append(value)
        try:
            execute(f"UPDATE `{table}` SET {', '.join(sets)} WHERE `{pk}`=%s", values+[record_id])
            flash("Record updated successfully.", "success")
            return redirect(url_for("list_records", table=table))
        except mysql.connector.Error as e:
            flash(f"Database error: {e.msg}", "error")
    return render_template("form.html", table=table, meta=meta, fields=fields, editing=True, record_id=record_id)

@app.route("/<table>/<int:record_id>/delete", methods=["POST"])
@roles_required("admin")
def delete_record(table, record_id):
    meta = module_or_404(table)
    enforce_module_access(table, write=True)
    try:
        execute(f"DELETE FROM `{table}` WHERE `{meta['pk']}`=%s", (record_id,))
        flash("Record deleted successfully.", "success")
    except mysql.connector.Error as e:
        flash(f"Cannot delete this record because it is linked to other records. Details: {e.msg}", "error")
    return redirect(url_for("list_records", table=table))

@app.route("/calendar")
@login_required
def calendar():
    rows = query_all("""SELECT a.appointment_id,a.appointment_date,a.status,c.name citizen,d.name doctor,h.name hospital
        FROM appointment a LEFT JOIN citizen c ON c.citizen_id=a.citizen_id
        LEFT JOIN doctor d ON d.doctor_id=a.doctor_id LEFT JOIN hospital h ON h.hospital_id=a.hospital_id
        WHERE (%s='admin' OR (%s='citizen' AND a.citizen_id=%s) OR (%s='doctor' AND a.doctor_id=%s) OR %s='staff')
        ORDER BY a.appointment_date LIMIT 500""",
        (session.get("role"), session.get("role"), session.get("citizen_id"),
         session.get("role"), session.get("doctor_id"), session.get("role")))
    return render_template("calendar.html", appointments=rows)

@app.route("/reports")
@roles_required("admin")
def reports():
    status = query_all("SELECT status,COUNT(*) total FROM appointment GROUP BY status")
    monthly = query_all("""SELECT DATE_FORMAT(appointment_date,'%Y-%m') month,COUNT(*) total
        FROM appointment GROUP BY DATE_FORMAT(appointment_date,'%Y-%m') ORDER BY month DESC LIMIT 12""")
    counts = {t: query_all(f"SELECT COUNT(*) n FROM `{t}`")[0]["n"] for t in MODULES}
    return render_template("reports.html", status=status, monthly=monthly, counts=counts)

@app.route("/health")
def health():
    try:
        query_all("SELECT 1")
        return {"status":"ok", "database":"connected"}
    except Exception as e:
        return {"status":"error", "message":str(e)}, 503

@app.errorhandler(mysql.connector.Error)
def db_error(error):
    return render_template("error.html", message=f"Database connection failed: {error.msg}"), 503

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true", host="127.0.0.1", port=5000)
