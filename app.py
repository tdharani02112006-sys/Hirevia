from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "hirevia_secret_key"

DATABASE = "hirevia.db"


# -----------------------------
# DATABASE
# -----------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    # -----------------------------
    # USERS
    # -----------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # -----------------------------
    # PROFILES
    # -----------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            phone TEXT,
            location TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            about TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Make sure profile columns exist
    columns = conn.execute(
        "PRAGMA table_info(profiles)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    required_columns = {
        "phone": "TEXT",
        "location": "TEXT",
        "skills": "TEXT",
        "education": "TEXT",
        "experience": "TEXT",
        "about": "TEXT"
    }

    for column_name, column_type in required_columns.items():

        if column_name not in column_names:

            conn.execute(
                f"ALTER TABLE profiles ADD COLUMN {column_name} {column_type}"
            )

    # -----------------------------
    # COMPANIES
    # -----------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            location TEXT,
            description TEXT,
            logo TEXT,
            company_type TEXT,
            industry TEXT,
            founded_year TEXT,
            company_size TEXT,
            founder TEXT,
            mission TEXT,
            vision TEXT,
            culture TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            pincode TEXT,
            branches TEXT,
            phone TEXT,
            website TEXT,
            hr_name TEXT,
            hr_phone TEXT,
            linkedin TEXT,
            instagram TEXT,
            facebook TEXT,
            other_social TEXT,
            skills_hiring TEXT,
            working_hours TEXT,
            employee_count TEXT
        )
    """)

    # Add new company profile columns to an existing Hirevia database.
    company_columns = conn.execute(
        "PRAGMA table_info(companies)"
    ).fetchall()

    company_column_names = [column["name"] for column in company_columns]

    required_company_columns = {
        "logo": "TEXT",
        "company_type": "TEXT",
        "industry": "TEXT",
        "founded_year": "TEXT",
        "company_size": "TEXT",
        "founder": "TEXT",
        "mission": "TEXT",
        "vision": "TEXT",
        "culture": "TEXT",
        "address": "TEXT",
        "city": "TEXT",
        "state": "TEXT",
        "country": "TEXT",
        "pincode": "TEXT",
        "branches": "TEXT",
        "phone": "TEXT",
        "website": "TEXT",
        "hr_name": "TEXT",
        "hr_phone": "TEXT",
        "linkedin": "TEXT",
        "instagram": "TEXT",
        "facebook": "TEXT",
        "other_social": "TEXT",
        "skills_hiring": "TEXT",
        "working_hours": "TEXT",
        "employee_count": "TEXT"
    }

    for column_name, column_type in required_company_columns.items():
        if column_name not in company_column_names:
            conn.execute(
                f"ALTER TABLE companies ADD COLUMN {column_name} {column_type}"
            )

    # -----------------------------
    # JOBS
    # -----------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            salary TEXT,
            job_type TEXT,
            experience TEXT,
            vacancies INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # -----------------------------
    # APPLICATIONS
    # -----------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER,
            company_id INTEGER,
            job_title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            applied_date TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Under Review',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # Add new columns to old applications table
    application_columns = conn.execute(
        "PRAGMA table_info(applications)"
    ).fetchall()

    application_column_names = [
        column["name"] for column in application_columns
    ]

    if "job_id" not in application_column_names:

        conn.execute(
            "ALTER TABLE applications ADD COLUMN job_id INTEGER"
        )

    if "company_id" not in application_column_names:

        conn.execute(
            "ALTER TABLE applications ADD COLUMN company_id INTEGER"
        )

    conn.commit()
    conn.close()


# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():

    return render_template("home.html")


# -----------------------------
# LOGIN
# -----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ? AND password = ?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")


# -----------------------------
# REGISTER
# -----------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, password)
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Email already registered"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# -----------------------------
# PROFILE
# -----------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        location = request.form.get("location")
        education = request.form.get("education")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        about = request.form.get("about")

        try:

            conn.execute(
                """
                UPDATE users
                SET name = ?, email = ?
                WHERE id = ?
                """,
                (
                    name,
                    email,
                    session["user_id"]
                )
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO profiles
                (
                    user_id,
                    phone,
                    location,
                    skills,
                    education,
                    experience,
                    about
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    phone,
                    location,
                    skills,
                    education,
                    experience,
                    about
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Email already registered"

        conn.close()

        session["user_name"] = name

        return redirect("/dashboard")

    conn.close()

    return render_template("profile.html")


# =====================================================
# COMPANY / RECRUITER SYSTEM
# =====================================================

# -----------------------------
# COMPANY REGISTER
# -----------------------------

@app.route("/company-register", methods=["GET", "POST"])
def company_register():

    if request.method == "POST":

        # Basic company details
        company_name = request.form.get("company_name")
        email = request.form.get("email")
        password = request.form.get("password")
        location = request.form.get("location")
        description = request.form.get("description")

        # Extended company profile details.
        # These are optional for now, so the existing registration page
        # will continue to work even before we update its form.
        logo = request.form.get("logo")
        company_type = request.form.get("company_type") or "Private"
        industry = request.form.get("industry") or "IT & Software"
        founded_year = request.form.get("founded_year")
        company_size = request.form.get("company_size")
        founder = request.form.get("founder")
        mission = request.form.get("mission")
        vision = request.form.get("vision")
        culture = request.form.get("culture")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")
        pincode = request.form.get("pincode")
        branches = request.form.get("branches")
        phone = request.form.get("phone")
        website = request.form.get("website")
        hr_name = request.form.get("hr_name")
        hr_phone = request.form.get("hr_phone")
        linkedin = request.form.get("linkedin")
        instagram = request.form.get("instagram")
        facebook = request.form.get("facebook")
        other_social = request.form.get("other_social")
        skills_hiring = request.form.get("skills_hiring")
        working_hours = request.form.get("working_hours")
        employee_count = request.form.get("employee_count")

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO companies
                (
                    company_name,
                    email,
                    password,
                    location,
                    description,
                    logo,
                    company_type,
                    industry,
                    founded_year,
                    company_size,
                    founder,
                    mission,
                    vision,
                    culture,
                    address,
                    city,
                    state,
                    country,
                    pincode,
                    branches,
                    phone,
                    website,
                    hr_name,
                    hr_phone,
                    linkedin,
                    instagram,
                    facebook,
                    other_social,
                    skills_hiring,
                    working_hours,
                    employee_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_name,
                    email,
                    password,
                    location,
                    description,
                    logo,
                    company_type,
                    industry,
                    founded_year,
                    company_size,
                    founder,
                    mission,
                    vision,
                    culture,
                    address,
                    city,
                    state,
                    country,
                    pincode,
                    branches,
                    phone,
                    website,
                    hr_name,
                    hr_phone,
                    linkedin,
                    instagram,
                    facebook,
                    other_social,
                    skills_hiring,
                    working_hours,
                    employee_count
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Company email already registered"

        conn.close()

        return redirect("/company-login")

    return render_template("company_register.html")


# -----------------------------
# COMPANY LOGIN
# -----------------------------

@app.route("/company-login", methods=["GET", "POST"])
def company_login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        company = conn.execute(
            """
            SELECT *
            FROM companies
            WHERE email = ? AND password = ?
            """,
            (email, password)
        ).fetchone()

        conn.close()

        if company:

            session["company_id"] = company["id"]
            session["company_name"] = company["company_name"]

            return redirect("/company-dashboard")

        return "Invalid company email or password"

    return render_template("company_login.html")


# -----------------------------
# COMPANY DASHBOARD
# -----------------------------

@app.route("/company-dashboard")
def company_dashboard():

    if "company_id" not in session:

        return redirect("/company-login")

    return render_template(
        "company_dashboard.html",
        company_name=session["company_name"]
    )


# -----------------------------
# COMPANY PROFILE
# -----------------------------

@app.route("/company-profile")
def company_profile():

    # This route is for the logged-in company to view its own profile.
    if "company_id" not in session:
        return redirect("/company-login")

    return redirect(f"/company/{session['company_id']}")


@app.route("/company/<int:company_id>")
def public_company_profile(company_id):

    # Public company profile.
    # Any job seeker can open a company's profile by its database ID.
    conn = get_db()

    company = conn.execute(
        """
        SELECT *
        FROM companies
        WHERE id = ?
        """,
        (company_id,)
    ).fetchone()

    if not company:
        conn.close()
        return "Company not found", 404

    company_jobs = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE company_id = ?
        ORDER BY id DESC
        """,
        (company_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "company_profile.html",
        company=company,
        company_jobs=company_jobs
    )


@app.route("/companies")
def companies():

    # Public list of all registered companies.
    conn = get_db()

    company_list = conn.execute(
        """
        SELECT *
        FROM companies
        ORDER BY company_name ASC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "companies.html",
        companies=company_list
    )


# -----------------------------
# POST JOB
# -----------------------------

@app.route("/post-job", methods=["GET", "POST"])
def post_job():

    if "company_id" not in session:

        return redirect("/company-login")

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        location = request.form.get("location")
        salary = request.form.get("salary")
        job_type = request.form.get("job_type")
        experience = request.form.get("experience")
        vacancies = request.form.get("vacancies")

        if not vacancies:
            vacancies = 1

        conn = get_db()

        conn.execute(
            """
            INSERT INTO jobs
            (
                company_id,
                title,
                description,
                location,
                salary,
                job_type,
                experience,
                vacancies
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["company_id"],
                title,
                description,
                location,
                salary,
                job_type,
                experience,
                vacancies
            )
        )

        conn.commit()
        conn.close()

        return redirect("/company-jobs")

    return render_template("post_job.html")


# -----------------------------
# COMPANY JOBS
# -----------------------------

@app.route("/company-jobs")
def company_jobs():

    if "company_id" not in session:

        return redirect("/company-login")

    conn = get_db()

    jobs_list = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE company_id = ?
        ORDER BY id DESC
        """,
        (session["company_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "company_jobs.html",
        jobs=jobs_list
    )


# =====================================================
# JOB SEEKER SIDE
# =====================================================

# -----------------------------
# FIND A JOB
# -----------------------------

@app.route("/jobs")
def jobs():

    if "user_id" not in session:

        return redirect("/login")

    return render_template("job.html")


@app.route("/find-job")
def find_job():

    if "user_id" not in session:

        return redirect("/login")

    return render_template("job.html")


@app.route("/find_job")
def find_job_page():

    if "user_id" not in session:

        return redirect("/login")

    return render_template("job.html")


@app.route("/job")
def job():

    if "user_id" not in session:

        return redirect("/login")

    return render_template("job.html")


# -----------------------------
# SAVE APPLICATION
# -----------------------------

def save_application():

    if "user_id" not in session:

        return redirect("/login")

    job_id = request.values.get("job_id")
    job_title = request.values.get("job_title")
    company = request.values.get("company")
    location = request.values.get("location")
    company_id = request.values.get("company_id")

    # If job_id is provided, get real job/company information
    if job_id:

        conn = get_db()

        job_data = conn.execute(
            """
            SELECT
                jobs.*,
                companies.company_name
            FROM jobs
            JOIN companies
            ON jobs.company_id = companies.id
            WHERE jobs.id = ?
            """,
            (job_id,)
        ).fetchone()

        conn.close()

        if job_data:

            job_title = job_data["title"]
            company = job_data["company_name"]
            location = job_data["location"]
            company_id = job_data["company_id"]

    # Default values for existing old job cards
    if not job_title:

        job_title = "Software Developer"

    if not company:

        company = "Hirevia Company"

    if not location:

        location = "Chennai"

    conn = get_db()

    conn.execute(
        """
        INSERT INTO applications
        (
            user_id,
            job_id,
            company_id,
            job_title,
            company,
            location,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            job_id,
            company_id,
            job_title,
            company,
            location,
            "Under Review"
        )
    )

    conn.commit()
    conn.close()

    return redirect("/applications")


# -----------------------------
# APPLY ROUTES
# -----------------------------

@app.route("/apply", methods=["GET", "POST"])
def apply():

    return save_application()


@app.route("/apply-job", methods=["GET", "POST"])
def apply_job():

    return save_application()


@app.route("/apply_job", methods=["GET", "POST"])
def apply_job_page():

    return save_application()


@app.route("/apply-now", methods=["GET", "POST"])
def apply_now():

    return save_application()


@app.route("/apply_now", methods=["GET", "POST"])
def apply_now_page():

    return save_application()


# -----------------------------
# MY APPLICATIONS
# -----------------------------

@app.route("/applications")
def applications():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    application_list = conn.execute(
        """
        SELECT *
        FROM applications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=application_list
    )


@app.route("/my-applications")
def my_applications():

    return applications()


@app.route("/my_applications")
def my_applications_page():

    return applications()


# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# -----------------------------
# START APPLICATION
# -----------------------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)