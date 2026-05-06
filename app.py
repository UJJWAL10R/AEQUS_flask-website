import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-before-production")
app.config["DATABASE"] = os.getenv(
    "DATABASE_PATH", os.path.join(app.root_path, "tv_status.db")
)

DEFAULT_USERS = [
    {
        "name": "System Admin",
        "email": "admin@tvstatus.local",
        "password": "Admin@123",
        "role": "Admin",
        "permission_level": "Admin",
        "locations": "ALL",
        "is_active": 1,
    },
    {
        "name": "ANO Operations",
        "email": "ano.ops@tvstatus.local",
        "password": "Ano@123",
        "role": "Operator",
        "permission_level": "Operator",
        "locations": "LE (Mounted),ANO (Floor Side)",
        "is_active": 1,
    },
    {
        "name": "Assembly Viewer",
        "email": "assembly.viewer@tvstatus.local",
        "password": "View@123",
        "role": "Viewer",
        "permission_level": "Viewer",
        "locations": "Assembly",
        "is_active": 1,
    },
    {
        "name": "Ujjwal Rajpal",
        "email": "ujjwal.rajpal@aequs.com",
        "password": "ujjwal10R@",
        "role": "Jr. Software Engineer",
        "permission_level": "Admin",
        "locations": "ALL",
        "is_active": 1,
    },
    {
        "name": "Jaysinh Chavda",
        "email": "Jaysinh.Chavda@aequs.com",
        "password": "jc-14724",
        "role": "Management Trainee",
        "permission_level": "Admin",
        "locations": "ALL",
        "is_active": 1,
    },
    {
        "name": "Mohita Chandiramani",
        "email": "Mohita.Chandiramani@aequs.com",
        "password": "15374",
        "role": "Manager",
        "permission_level": "Admin",
        "locations": "ALL",
        "is_active": 1,
    },
]
 
DEFAULT_TV_RECORDS = [
    {
        "tv_id": "Ano Treatment",
        "location": "LE (Mounted)",
        "content_name": "WET_LAB_TRENDS",
        "template_type": "PICKCELL",
        "layout_composition": "Full Screen",
        "deployed_date": "20-Apr-2026",
        "deployed_time": "09:10 AM",
        "tv_status": "ONLINE",
        "last_online": "Today",
        "ping_status": "PING REQUEST",
        "last_ping_time": "10:32 AM",
        "deployed_status": "Deployed",
        "remarks": "Healthy screen and current content synced.",
    },
    {
        "tv_id": "ACP3-ANOTV",
        "location": "ANO (Floor Side)",
        "content_name": "ANO_DAILY_UPDATES (KPOV-LB, KPIV-S1, ANO106, ANO-Temp)",
        "template_type": "PICKCELL",
        "layout_composition": "Full Screen",
        "deployed_date": "29-Apr-2026",
        "deployed_time": "11:10 AM",
        "tv_status": "ONLINE",
        "last_online": "Today",
        "ping_status": "PING REQUEST",
        "last_ping_time": "10:36 AM",
        "deployed_status": "Deployed",
        "remarks": "Healthy screen and current content synced.",
    },
    {
        "tv_id": "Flash QDIM",
        "location": "ANO (Floor Side)",
        "content_name": "AIO (KPOV-LB, KPIV-S1, ANO106, ANO-Temp)",
        "template_type": "PICKCELL",
        "layout_composition": "4 Layout Screen",
        "deployed_date": "23-Apr-2026",
        "deployed_time": "04:15 PM",
        "tv_status": "OFFLINE",
        "last_online": "5 Days Ago",
        "ping_status": "PING REQUEST",
        "last_ping_time": "09:58 AM",
        "deployed_status": "Deployed",
        "remarks": "Intermittent panel signal under observation.",
    },
    {
        "tv_id": "Assembly - OQC",
        "location": "Assembly",
        "content_name": "PROJECT_ALPHA_OQC",
        "template_type": "PICKCELL",
        "layout_composition": "Full Screen",
        "deployed_date": "03-Apr-2026",
        "deployed_time": "10:00 AM",
        "tv_status": "OFFLINE",
        "last_online": "26 Days Ago",
        "ping_status": "PING REQUEST",
        "last_ping_time": "10:34 AM",
        "deployed_status": "Deployed",
        "remarks": "Awaiting line-sides hardware inspection.",
    },
]

DEFAULT_POWERBI_REPORTS = [
    {
        "name": "Ano Dashboard 105 Application",
        "url": "https://app.powerbi.com/groups/07228872-ff92-42d9-ab91-1116ce17b076/reports/a3530cdb-548b-45d5-a1b8-2747c4f4ba26/4cfea5d3771eeb47ab10?experience=power-bi&clientSideAuth=0",
        "category": "ANO",
    },
    {
        "name": "Ano Dashboard 106",
        "url": "https://app.powerbi.com/groups/07228872-ff92-42d9-ab91-1116ce17b076/reports/80a1cd94-2f47-413f-82b1-0925b041fac6/5120bdcaab3f36cf94de?experience=power-bi&clientSideAuth=0",
        "category": "ANO",
    },
    {
        "name": "Ano Dashboard 107 Application (Wet Lab Trend Charts)",
        "url": "https://app.powerbi.com/groups/07228872-ff92-42d9-ab91-1116ce17b076/reports/b9fddd4d-e63d-408c-9317-8ad0730ad937/bdab09556340317bada0?experience=power-bi&clientSideAuth=0",
        "category": "ANO",
    },
    {
        "name": "Ano Live SCADA Temperature",
        "url": "https://app.powerbi.com/groups/07228872-ff92-42d9-ab91-1116ce17b076/reports/853d542c-b72f-4d36-aa28-45223f1f9bd4/72b441b7a5f19cf346a9?experience=power-bi&clientSideAuth=0",
        "category": "SCADA",
    },
    {
        "name": "KPIV Dashboard",
        "url": "https://app.powerbi.com/groups/07228872-ff92-42d9-ab91-1116ce17b076/reports/13431330-2de8-4726-9930-12f11e8509e6/b6cf6b04699c30656495?experience=power-bi&clientSideAuth=0",
        "category": "KPI",
    },
    {
        "name": "KPOV Dashboard LB",
        "url": "https://app.powerbi.com/groups/7a4cb31c-22df-4e29-943f-78786b635164/reports/471f112f-9dd3-4f49-89e2-0e76410b34f0/79ad63691290d5d21ea2?ctid=0e0f5bfc-3e6d-414f-8e75-abead7e01789&experience=power-bi&clientSideAuth=0",
        "category": "KPI",
    },
]

DEFAULT_TV_REPORT_MAP = {
    "Ano Treatment": [
        "Ano Dashboard 107 Application (Wet Lab Trend Charts)",
    ],
    "ACP3-ANOTV": [
        "Ano Dashboard 105 Application",
    ],
    "Flash QDIM": [
        "Ano Dashboard 106",
        "Ano Live SCADA Temperature",
        "KPIV Dashboard",
        "KPOV Dashboard LB",
    ],
}

PERMISSION_LEVEL_OPTIONS = ["Admin", "Operator", "Viewer"]
TV_STATUS_OPTIONS = ["ONLINE", "OFFLINE", "MAINTENANCE"]
PING_STATUS_OPTIONS = ["PING REQUEST", "PING FAILED", "PORT BLOCKED"]
DEPLOY_STATUS_OPTIONS = ["Deployed", "Pending", "Failed", "Rollback"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            permission_level TEXT,
            locations TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    user_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(users)").fetchall()
    }
    if "permission_level" not in user_columns:
        db.execute("ALTER TABLE users ADD COLUMN permission_level TEXT")
        db.execute(
            """
            UPDATE users
            SET permission_level = CASE
                WHEN role IN ('Admin', 'Operator', 'Viewer') THEN role
                ELSE 'Viewer'
            END
            WHERE permission_level IS NULL OR permission_level = ''
            """
        )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tv_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tv_id TEXT NOT NULL UNIQUE,
            location TEXT NOT NULL,
            content_name TEXT NOT NULL,
            template_type TEXT NOT NULL,
            layout_composition TEXT NOT NULL,
            deployed_date TEXT NOT NULL,
            deployed_time TEXT NOT NULL,
            tv_status TEXT NOT NULL,
            last_online TEXT NOT NULL,
            ping_status TEXT NOT NULL,
            last_ping_time TEXT NOT NULL,
            deployed_status TEXT NOT NULL,
            remarks TEXT NOT NULL,
            updated_by TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS powerbi_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tv_report_assignments (
            tv_record_id INTEGER NOT NULL,
            report_id INTEGER NOT NULL,
            assigned_at TEXT NOT NULL,
            PRIMARY KEY (tv_record_id, report_id),
            FOREIGN KEY (tv_record_id) REFERENCES tv_records(id) ON DELETE CASCADE,
            FOREIGN KEY (report_id) REFERENCES powerbi_reports(id) ON DELETE CASCADE
        )
        """
    )

    user_count = db.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
    if user_count == 0:
        now = timestamp_now()
        for user in DEFAULT_USERS:
            db.execute(
                """
                INSERT INTO users (name, email, password_hash, role, permission_level, locations, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user["name"],
                    user["email"],
                    generate_password_hash(user["password"]),
                    user["role"],
                    user["permission_level"],
                    user["locations"],
                    user["is_active"],
                    now,
                    now,
                ),
            )

    tv_count = db.execute("SELECT COUNT(*) AS count FROM tv_records").fetchone()["count"]
    if tv_count == 0:
        now = timestamp_now()
        for row in DEFAULT_TV_RECORDS:
            db.execute(
                """
                INSERT INTO tv_records (
                    tv_id, location, content_name, template_type, layout_composition,
                    deployed_date, deployed_time, tv_status, last_online, ping_status,
                    last_ping_time, deployed_status, remarks, updated_by, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["tv_id"],
                    row["location"],
                    row["content_name"],
                    row["template_type"],
                    row["layout_composition"],
                    row["deployed_date"],
                    row["deployed_time"],
                    row["tv_status"],
                    row["last_online"],
                    row["ping_status"],
                    row["last_ping_time"],
                    row["deployed_status"],
                    row["remarks"],
                    "System seed",
                    now,
                ),
            )

    setting_count = db.execute(
        "SELECT COUNT(*) AS count FROM app_settings WHERE key = 'powerbi_embed_url'"
    ).fetchone()["count"]
    if setting_count == 0:
        db.execute(
            """
            INSERT INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
            """,
            ("powerbi_embed_url", "", timestamp_now()),
        )
    report_count = db.execute("SELECT COUNT(*) AS count FROM powerbi_reports").fetchone()["count"]
    if report_count == 0:
        now = timestamp_now()
        for report in DEFAULT_POWERBI_REPORTS:
            db.execute(
                """
                INSERT INTO powerbi_reports (name, url, category, is_active, created_at, updated_at)
                VALUES (?, ?, ?, 1, ?, ?)
                """,
                (report["name"], report["url"], report["category"], now, now),
            )
    seed_default_powerbi_assignments()
    db.commit()


def timestamp_now():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def parse_locations(raw_locations):
    if not raw_locations:
        return []
    locations = [item.strip() for item in raw_locations.split(",") if item.strip()]
    return locations or []


def serialize_locations(locations):
    cleaned = [item.strip() for item in locations if item.strip()]
    return ",".join(cleaned) if cleaned else "ALL"


def query_user_by_email(email):
    if not email:
        return None
    return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or not user["is_active"]:
        session.clear()
        return None
    return normalize_user(user)


def normalize_user(user_row):
    user = dict(user_row)
    user["permission_level"] = user.get("permission_level") or user["role"]
    user["locations_list"] = parse_locations(user["locations"])
    user["is_admin"] = user["permission_level"] == "Admin"
    user["scope_label"] = (
        "All locations"
        if "ALL" in user["locations_list"]
        else ", ".join(user["locations_list"]) or "No assigned scope"
    )
    return user


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = current_user()
        if not user:
            return redirect(url_for("login"))
        if not user["is_admin"]:
            flash("Only admins can perform that action.", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped_view


def visible_rows_for(user, query="", status="all"):
    db = get_db()
    rows = [dict(row) for row in db.execute("SELECT * FROM tv_records ORDER BY tv_id").fetchall()]
    visible_rows = []
    search_query = query.lower().strip()

    for row in rows:
        allowed = "ALL" in user["locations_list"] or row["location"] in user["locations_list"]
        if not allowed:
            continue
        if status != "all" and row["tv_status"].lower() != status:
            continue

        haystack = " ".join(
            [
                row["tv_id"],
                row["location"],
                row["content_name"],
                row["template_type"],
                row["layout_composition"],
                row["remarks"],
            ]
        ).lower()
        if search_query and search_query not in haystack:
            continue
        visible_rows.append(row)

    return visible_rows


def build_kpis(rows):
    total = len(rows)
    online = sum(1 for row in rows if row["tv_status"] == "ONLINE")
    offline = sum(1 for row in rows if row["tv_status"] == "OFFLINE")
    maintenance = sum(1 for row in rows if row["tv_status"] == "MAINTENANCE")
    ping_healthy = sum(1 for row in rows if row["ping_status"] == "PING REQUEST")

    return [
        {
            "label": "Visible TVs",
            "value": total,
            "meta": "Records in current access scope",
            "class_name": "glass-blue",
            "icon": "bi-grid-1x2",
        },
        {
            "label": "Online",
            "value": online,
            "meta": f"{round((online / total) * 100) if total else 0}% healthy screens",
            "class_name": "glass-green",
            "icon": "bi-broadcast-pin",
        },
        {
            "label": "Offline",
            "value": offline,
            "meta": "Needs intervention or restart",
            "class_name": "glass-red",
            "icon": "bi-wifi-off",
        },
        {
            "label": "Maintenance",
            "value": maintenance,
            "meta": f"{ping_healthy} LAN checks currently healthy",
            "class_name": "glass-gold",
            "icon": "bi-tools",
        },
    ]


def build_distribution(rows, key):
    counts = {}
    for row in rows:
        label = row.get(key) or "Unknown"
        counts[label] = counts.get(label, 0) + 1
    return counts


def detect_content_type(row):
    content = (row.get("content_name") or "").upper()
    layout = (row.get("layout_composition") or "").upper()

    if "TREND" in content:
        return "Trend Board"
    if "UPDATE" in content:
        return "Daily Update"
    if "OQC" in content or "QUALITY" in content:
        return "Quality Dashboard"
    if "AIO" in content or "KPI" in content or "KPOV" in content:
        return "Composite KPI Wall"
    if "4 LAYOUT" in layout:
        return "Multi-Panel Feed"
    return "Standard Feed"


def build_analytics(rows):
    content_types = {}
    for row in rows:
        content_type = detect_content_type(row)
        content_types[content_type] = content_types.get(content_type, 0) + 1

    return {
        "status": build_distribution(rows, "tv_status"),
        "connectivity": build_distribution(rows, "ping_status"),
        "locations": build_distribution(rows, "location"),
        "template_types": build_distribution(rows, "template_type"),
        "content_types": content_types,
        "layout_types": build_distribution(rows, "layout_composition"),
    }


def build_dashboard_details(rows, analytics):
    total = len(rows)
    deployed = sum(1 for row in rows if row["deployed_status"] == "Deployed")
    pending = sum(1 for row in rows if row["deployed_status"] == "Pending")
    failed = sum(1 for row in rows if row["deployed_status"] == "Failed")
    stale = sum(1 for row in rows if row["last_online"] not in {"Today", "Now"} and row["tv_status"] != "ONLINE")
    multi_layout = sum(1 for row in rows if "4" in row["layout_composition"] or "Multi" in row["layout_composition"])
    ping_healthy = sum(1 for row in rows if row["ping_status"] == "PING REQUEST")
    dominant_content = max(
        analytics["content_types"].items(), key=lambda item: item[1], default=("No data", 0)
    )[0]

    return {
        "deployed": deployed,
        "pending": pending,
        "failed": failed,
        "stale": stale,
        "multi_layout": multi_layout,
        "unique_locations": len(analytics["locations"]),
        "ping_health_pct": round((ping_healthy / total) * 100) if total else 0,
        "deployment_pct": round((deployed / total) * 100) if total else 0,
        "dominant_content": dominant_content,
        "records": total,
    }


def dashboard_context(user, query="", status="all"):
    rows = visible_rows_for(user, query=query, status=status)
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
    active_users = db.execute(
        "SELECT COUNT(*) AS count FROM users WHERE is_active = 1"
    ).fetchone()["count"]
    analytics = build_analytics(rows)
    spotlight = rows[0] if rows else None
    admin_records = all_tv_records() if user["is_admin"] else []
    tv_ids = [row["id"] for row in rows]
    mapped_tv_ids = sorted({*tv_ids, *[record["id"] for record in admin_records]})
    reports_by_tv = assigned_reports_for_tvs(mapped_tv_ids)

    return {
        "user": user,
        "rows": rows,
        "kpis": build_kpis(rows),
        "analytics": analytics,
        "dashboard_details": build_dashboard_details(rows, analytics),
        "spotlight": spotlight,
        "spotlight_content_type": detect_content_type(spotlight) if spotlight else "No feed",
        "spotlight_reports": reports_by_tv.get(spotlight["id"], []) if spotlight else [],
        "scope": user["scope_label"],
        "search": query,
        "status": status,
        "snapshot_time": timestamp_now(),
        "permission_level_options": PERMISSION_LEVEL_OPTIONS,
        "tv_status_options": TV_STATUS_OPTIONS,
        "ping_status_options": PING_STATUS_OPTIONS,
        "deploy_status_options": DEPLOY_STATUS_OPTIONS,
        "locations": all_locations(),
        "users": all_users() if user["is_admin"] else [],
        "all_records": admin_records,
        "total_users": total_users,
        "active_users": active_users,
        "powerbi_embed_url": get_setting("powerbi_embed_url", ""),
        "powerbi_reports": all_powerbi_reports(),
        "reports_by_tv": reports_by_tv,
    }


def all_locations():
    db = get_db()
    rows = db.execute("SELECT DISTINCT location FROM tv_records ORDER BY location").fetchall()
    return [row["location"] for row in rows]


def all_users():
    db = get_db()
    rows = db.execute("SELECT * FROM users ORDER BY role, name").fetchall()
    return [normalize_user(row) for row in rows]


def all_tv_records():
    db = get_db()
    rows = db.execute("SELECT * FROM tv_records ORDER BY tv_id").fetchall()
    return [dict(row) for row in rows]


def all_powerbi_reports():
    rows = get_db().execute(
        "SELECT * FROM powerbi_reports WHERE is_active = 1 ORDER BY category, name"
    ).fetchall()
    return [dict(row) for row in rows]


def assigned_reports_for_tvs(tv_record_ids):
    if not tv_record_ids:
        return {}
    placeholders = ",".join("?" for _ in tv_record_ids)
    rows = get_db().execute(
        f"""
        SELECT a.tv_record_id, r.id, r.name, r.url, r.category
        FROM tv_report_assignments a
        JOIN powerbi_reports r ON r.id = a.report_id
        WHERE a.tv_record_id IN ({placeholders}) AND r.is_active = 1
        ORDER BY r.category, r.name
        """,
        tuple(tv_record_ids),
    ).fetchall()
    grouped = {record_id: [] for record_id in tv_record_ids}
    for row in rows:
        grouped[row["tv_record_id"]].append(dict(row))
    return grouped


def assign_reports_to_tv(tv_record_id, report_ids):
    db = get_db()
    db.execute("DELETE FROM tv_report_assignments WHERE tv_record_id = ?", (tv_record_id,))
    now = timestamp_now()
    for report_id in report_ids:
        db.execute(
            """
            INSERT OR IGNORE INTO tv_report_assignments (tv_record_id, report_id, assigned_at)
            VALUES (?, ?, ?)
            """,
            (tv_record_id, report_id, now),
        )
    db.commit()


def seed_default_powerbi_assignments():
    db = get_db()
    assignment_count = db.execute(
        "SELECT COUNT(*) AS count FROM tv_report_assignments"
    ).fetchone()["count"]
    if assignment_count:
        return

    reports = {
        row["name"]: row["id"]
        for row in db.execute("SELECT id, name FROM powerbi_reports WHERE is_active = 1").fetchall()
    }
    tvs = {
        row["tv_id"]: row["id"]
        for row in db.execute("SELECT id, tv_id FROM tv_records").fetchall()
    }

    now = timestamp_now()
    for tv_name, report_names in DEFAULT_TV_REPORT_MAP.items():
        tv_record_id = tvs.get(tv_name)
        if not tv_record_id:
            continue
        for report_name in report_names:
            report_id = reports.get(report_name)
            if not report_id:
                continue
            db.execute(
                """
                INSERT OR IGNORE INTO tv_report_assignments (tv_record_id, report_id, assigned_at)
                VALUES (?, ?, ?)
                """,
                (tv_record_id, report_id, now),
            )
    db.commit()


def get_setting(key, default=""):
    row = get_db().execute(
        "SELECT value FROM app_settings WHERE key = ?", (key,)
    ).fetchone()
    return row["value"] if row else default


@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "theme_options": ["dark", "light"],
        "detect_content_type": detect_content_type,
    }


@app.route("/", methods=["GET", "POST"])
def login():
    user = current_user()
    if user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        user_row = query_user_by_email(email)

        if (
            not user_row
            or not user_row["is_active"]
            or not check_password_hash(user_row["password_hash"], password)
        ):
            flash("Invalid credentials. Try one of the seeded demo accounts.", "error")
            return render_template("login.html", demo_users=DEFAULT_USERS)

        session["user_id"] = user_row["id"]
        return redirect(url_for("dashboard"))

    return render_template("login.html", demo_users=DEFAULT_USERS)


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    query = request.args.get("search", "").strip()
    status = request.args.get("status", "all").strip().lower()
    if status not in {"all", "online", "offline", "maintenance"}:
        status = "all"
    return render_template("dashboard.html", active_page="dashboard", **dashboard_context(user, query, status))


@app.route("/analytics")
@login_required
def analytics():
    user = current_user()
    query = request.args.get("search", "").strip()
    status = request.args.get("status", "all").strip().lower()
    if status not in {"all", "online", "offline", "maintenance"}:
        status = "all"
    return render_template("analytics.html", active_page="analytics", **dashboard_context(user, query, status))


@app.route("/powerbi")
@login_required
def powerbi():
    user = current_user()
    context = dashboard_context(user)
    grouped_reports = []
    for tv in context["rows"]:
        grouped_reports.append(
            {
                "tv": tv,
                "reports": context["reports_by_tv"].get(tv["id"], []),
            }
        )

    selected_tv_id = request.args.get("tv", type=int)
    selected_report_id = request.args.get("report", type=int)
    selected_embed = ""
    selected_report_name = ""

    if grouped_reports:
        if selected_tv_id is None:
            selected_tv_id = grouped_reports[0]["tv"]["id"]
        selected_group = next(
            (group for group in grouped_reports if group["tv"]["id"] == selected_tv_id),
            grouped_reports[0],
        )
        selected_tv_id = selected_group["tv"]["id"]
        reports = selected_group["reports"]
        if reports:
            selected_report = next(
                (report for report in reports if report["id"] == selected_report_id),
                reports[0],
            )
            selected_report_id = selected_report["id"]
            selected_embed = selected_report["url"]
            selected_report_name = selected_report["name"]

    return render_template(
        "powerbi.html",
        active_page="powerbi",
        grouped_reports=grouped_reports,
        selected_tv_id=selected_tv_id,
        selected_report_id=selected_report_id,
        selected_embed=selected_embed,
        selected_report_name=selected_report_name,
        **context,
    )


@app.route("/powerbi-public")
def powerbi_public():
    powerbi_embed_url = get_setting("powerbi_embed_url", "")
    rows = all_tv_records()
    reports_by_tv = assigned_reports_for_tvs([row["id"] for row in rows])
    grouped_reports = [{"tv": tv, "reports": reports_by_tv.get(tv["id"], [])} for tv in rows]
    selected_tv_id = request.args.get("tv", type=int)
    selected_report_id = request.args.get("report", type=int)
    selected_embed = ""
    selected_report_name = ""

    if grouped_reports:
        if selected_tv_id is None:
            selected_tv_id = grouped_reports[0]["tv"]["id"]
        selected_group = next(
            (group for group in grouped_reports if group["tv"]["id"] == selected_tv_id),
            grouped_reports[0],
        )
        selected_tv_id = selected_group["tv"]["id"]
        reports = selected_group["reports"]
        if reports:
            selected_report = next(
                (report for report in reports if report["id"] == selected_report_id),
                reports[0],
            )
            selected_report_id = selected_report["id"]
            selected_embed = selected_report["url"]
            selected_report_name = selected_report["name"]

    return render_template(
        "powerbi_public.html",
        powerbi_embed_url=powerbi_embed_url,
        grouped_reports=grouped_reports,
        selected_tv_id=selected_tv_id,
        selected_report_id=selected_report_id,
        selected_embed=selected_embed,
        selected_report_name=selected_report_name,
    )


@app.route("/admin/users/create", methods=["POST"])
@admin_required
def create_user():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    permission_level = request.form.get("permission_level", "Viewer").strip()
    custom_role = request.form.get("custom_role", "").strip()
    role = custom_role or permission_level
    locations = request.form.getlist("locations")
    all_locations_access = request.form.get("all_locations") == "on"

    if not name or not email or not password:
        flash("Name, email, and password are required for new users.", "error")
        return redirect(url_for("dashboard"))
    if permission_level not in PERMISSION_LEVEL_OPTIONS:
        flash("Selected permission level is not valid.", "error")
        return redirect(url_for("dashboard"))
    if query_user_by_email(email):
        flash("A user with that email already exists.", "error")
        return redirect(url_for("dashboard"))

    location_scope = ["ALL"] if all_locations_access or permission_level == "Admin" else locations
    if not location_scope:
        flash("Choose at least one location for non-admin users.", "error")
        return redirect(url_for("dashboard"))

    now = timestamp_now()
    get_db().execute(
        """
        INSERT INTO users (name, email, password_hash, role, permission_level, locations, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (
            name,
            email,
            generate_password_hash(password),
            role,
            permission_level,
            serialize_locations(location_scope),
            now,
            now,
        ),
    )
    get_db().commit()
    flash("New user created successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/users/<int:user_id>/update", methods=["POST"])
@admin_required
def update_user(user_id):
    db = get_db()
    existing = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not existing:
        flash("User record not found.", "error")
        return redirect(url_for("dashboard"))

    name = request.form.get("name", "").strip()
    permission_level = request.form.get(
        "permission_level", existing["permission_level"] or existing["role"]
    ).strip()
    custom_role = request.form.get("custom_role", "").strip()
    role = custom_role or permission_level
    password = request.form.get("password", "").strip()
    locations = request.form.getlist("locations")
    all_locations_access = request.form.get("all_locations") == "on"
    is_active = 1 if request.form.get("is_active") == "on" else 0

    if not name:
        flash("User name cannot be blank.", "error")
        return redirect(url_for("dashboard"))
    if permission_level not in PERMISSION_LEVEL_OPTIONS:
        flash("Selected permission level is not valid.", "error")
        return redirect(url_for("dashboard"))

    location_scope = ["ALL"] if all_locations_access or permission_level == "Admin" else locations
    if not location_scope:
        flash("Choose at least one location for non-admin users.", "error")
        return redirect(url_for("dashboard"))

    password_hash = existing["password_hash"]
    if password:
        password_hash = generate_password_hash(password)

    db.execute(
        """
        UPDATE users
        SET name = ?, password_hash = ?, role = ?, permission_level = ?, locations = ?, is_active = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            name,
            password_hash,
            role,
            permission_level,
            serialize_locations(location_scope),
            is_active,
            timestamp_now(),
            user_id,
        ),
    )
    db.commit()
    flash("User details updated.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/settings/powerbi", methods=["POST"])
@admin_required
def update_powerbi_settings():
    embed_url = request.form.get("powerbi_embed_url", "").strip()
    db = get_db()
    db.execute(
        """
        INSERT INTO app_settings (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """,
        ("powerbi_embed_url", embed_url, timestamp_now()),
    )
    db.commit()
    flash("Power BI embed link updated.", "success")
    return redirect(url_for("powerbi"))


@app.route("/admin/tvs/<int:record_id>/reports", methods=["POST"])
@admin_required
def update_tv_reports(record_id):
    db = get_db()
    existing = db.execute("SELECT id FROM tv_records WHERE id = ?", (record_id,)).fetchone()
    if not existing:
        flash("TV record not found.", "error")
        return redirect(url_for("dashboard"))

    valid_report_ids = {report["id"] for report in all_powerbi_reports()}
    selected_ids = []
    for raw_value in request.form.getlist("report_ids"):
        try:
            report_id = int(raw_value)
        except (TypeError, ValueError):
            continue
        if report_id in valid_report_ids:
            selected_ids.append(report_id)

    assign_reports_to_tv(record_id, selected_ids)
    flash("TV report assignments updated.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/tvs/create", methods=["POST"])
@admin_required
def create_tv():
    payload = extract_tv_payload(request.form)
    if not payload["tv_id"] or not payload["location"] or not payload["content_name"]:
        flash("TV ID, location, and content name are required.", "error")
        return redirect(url_for("dashboard"))

    db = get_db()
    if db.execute("SELECT id FROM tv_records WHERE tv_id = ?", (payload["tv_id"],)).fetchone():
        flash("A TV with that ID already exists.", "error")
        return redirect(url_for("dashboard"))

    cursor = db.execute(
        """
        INSERT INTO tv_records (
            tv_id, location, content_name, template_type, layout_composition,
            deployed_date, deployed_time, tv_status, last_online, ping_status,
            last_ping_time, deployed_status, remarks, updated_by, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["tv_id"],
            payload["location"],
            payload["content_name"],
            payload["template_type"],
            payload["layout_composition"],
            payload["deployed_date"],
            payload["deployed_time"],
            payload["tv_status"],
            payload["last_online"],
            payload["ping_status"],
            payload["last_ping_time"],
            payload["deployed_status"],
            payload["remarks"],
            current_user()["name"],
            timestamp_now(),
        ),
    )
    db.commit()
    valid_report_ids = {report["id"] for report in all_powerbi_reports()}
    selected_ids = []
    for raw_value in request.form.getlist("report_ids"):
        try:
            report_id = int(raw_value)
        except (TypeError, ValueError):
            continue
        if report_id in valid_report_ids:
            selected_ids.append(report_id)
    assign_reports_to_tv(cursor.lastrowid, selected_ids)
    flash("TV record added.", "success")
    return redirect(url_for("dashboard"))


@app.route("/admin/tvs/<int:record_id>/update", methods=["POST"])
@admin_required
def update_tv(record_id):
    db = get_db()
    existing = db.execute("SELECT * FROM tv_records WHERE id = ?", (record_id,)).fetchone()
    if not existing:
        flash("TV record not found.", "error")
        return redirect(url_for("dashboard"))

    payload = extract_tv_payload(request.form)
    if not payload["tv_id"] or not payload["location"] or not payload["content_name"]:
        flash("TV ID, location, and content name are required.", "error")
        return redirect(url_for("dashboard"))

    duplicate = db.execute(
        "SELECT id FROM tv_records WHERE tv_id = ? AND id != ?", (payload["tv_id"], record_id)
    ).fetchone()
    if duplicate:
        flash("Another TV already uses that ID.", "error")
        return redirect(url_for("dashboard"))

    db.execute(
        """
        UPDATE tv_records
        SET tv_id = ?, location = ?, content_name = ?, template_type = ?, layout_composition = ?,
            deployed_date = ?, deployed_time = ?, tv_status = ?, last_online = ?, ping_status = ?,
            last_ping_time = ?, deployed_status = ?, remarks = ?, updated_by = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            payload["tv_id"],
            payload["location"],
            payload["content_name"],
            payload["template_type"],
            payload["layout_composition"],
            payload["deployed_date"],
            payload["deployed_time"],
            payload["tv_status"],
            payload["last_online"],
            payload["ping_status"],
            payload["last_ping_time"],
            payload["deployed_status"],
            payload["remarks"],
            current_user()["name"],
            timestamp_now(),
            record_id,
        ),
    )
    db.commit()
    valid_report_ids = {report["id"] for report in all_powerbi_reports()}
    selected_ids = []
    for raw_value in request.form.getlist("report_ids"):
        try:
            report_id = int(raw_value)
        except (TypeError, ValueError):
            continue
        if report_id in valid_report_ids:
            selected_ids.append(report_id)
    assign_reports_to_tv(record_id, selected_ids)
    flash("TV record updated.", "success")
    return redirect(url_for("dashboard"))


def extract_tv_payload(form):
    return {
        "tv_id": form.get("tv_id", "").strip(),
        "location": form.get("location", "").strip(),
        "content_name": form.get("content_name", "").strip(),
        "template_type": form.get("template_type", "").strip() or "PICKCELL",
        "layout_composition": form.get("layout_composition", "").strip() or "Full Screen",
        "deployed_date": form.get("deployed_date", "").strip() or "-",
        "deployed_time": form.get("deployed_time", "").strip() or "-",
        "tv_status": form.get("tv_status", "ONLINE").strip(),
        "last_online": form.get("last_online", "").strip() or "-",
        "ping_status": form.get("ping_status", "PING REQUEST").strip(),
        "last_ping_time": form.get("last_ping_time", "").strip() or "-",
        "deployed_status": form.get("deployed_status", "Deployed").strip(),
        "remarks": form.get("remarks", "").strip() or "No remarks added.",
    }


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
