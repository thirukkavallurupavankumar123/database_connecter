"""Live demo script — walks through the full ARGO platform flow."""

import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = "http://127.0.0.1:8000"


def api(method: str, path: str, body: dict | None = None):
    data = json.dumps(body).encode() if body else None
    req = Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        res = urlopen(req)
        return json.loads(res.read().decode())
    except HTTPError as e:
        return {"error": e.code, "detail": json.loads(e.read().decode())}


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ── 1. Health check ──────────────────────────────────────────
section("1. Health Check")
print(json.dumps(api("GET", "/health"), indent=2))

# ── 2. Create Organization ───────────────────────────────────
section("2. Create Organization")
org = api("POST", "/api/organizations/", {"name": "ARGO Demo Corp"})
print(json.dumps(org, indent=2))
ORG_ID = org["id"]

# ── 3. Create User ───────────────────────────────────────────
section("3. Create User")
user = api("POST", f"/api/organizations/{ORG_ID}/users", {
    "email": "demo@argocorp.com",
    "name": "Pavan Kumar",
    "organization_id": ORG_ID,
})
print(json.dumps(user, indent=2))
USER_ID = user["id"]

# ── 4. List Organization Users ───────────────────────────────
section("4. List Users in Org")
users = api("GET", f"/api/organizations/{ORG_ID}/users")
print(f"  Found {len(users)} user(s)")
for u in users:
    print(f"  - {u['name']} ({u['email']}) [id: {u['id']}]")

# ── 5. Test Connect Session (Query Page Flow) ────────────────
section("5. Connect Session (Query Page Flow)")
session = api("POST", "/api/query/connect", {"user_id": USER_ID})
print(f"  User: {session['user_name']}")
print(f"  Org:  {session['organization_name']}")
print(f"  Available connections: {len(session['connections'])}")
if session["connections"]:
    for c in session["connections"]:
        print(f"    - {c['name']} ({c['db_type']} @ {c['host']}/{c['database_name']})")
else:
    print("  (No connections yet — add one via the Connections page)")

# ── 6. List All Organizations ────────────────────────────────
section("6. All Organizations")
orgs = api("GET", "/api/organizations/")
for o in orgs:
    print(f"  - {o['name']} [id: {o['id']}]")

# ── 7. API Docs ──────────────────────────────────────────────
section("7. Interactive API Docs")
print(f"  Swagger UI:  {BASE}/docs")
print(f"  ReDoc:       {BASE}/redoc")

# ── Summary ──────────────────────────────────────────────────
section("DEMO COMPLETE")
print(f"""
  Organization ID: {ORG_ID}
  User ID:         {USER_ID}
  User Email:      demo@argocorp.com

  Use these in the frontend:
  1. Go to http://localhost:3000/connections
     - Enter Org ID: {ORG_ID}
     - Add a real database connection (PostgreSQL/MySQL/SQL Server)

  2. Go to http://localhost:3000/query
     - Enter User ID: {USER_ID}
     - Click Connect
     - Pick your database from the dropdown
     - Ask questions in plain English!

  3. Go to http://localhost:3000/history
     - Enter User ID: {USER_ID}
     - See all past queries
""")
