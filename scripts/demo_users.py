"""Demo: Create users with separate/shared organizations"""
import urllib.request
import json

API = "http://localhost:8000/api/auth"

def signup(email, name, password, org_name=None, org_id=None):
    body = {"email": email, "name": name, "password": password}
    if org_name:
        body["organization_name"] = org_name
    if org_id:
        body["organization_id"] = org_id
    req = urllib.request.Request(
        f"{API}/signup",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())

def login(email, password):
    req = urllib.request.Request(
        f"{API}/login",
        data=json.dumps({"email": email, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())

# --- User 1: Creates "Alpha Corp" ---
u1 = signup("alice@alpha.com", "Alice Johnson", "alice123", org_name="Alpha Corp")
print("=== USER 1 (Alice) - Creates Alpha Corp ===")
for k, v in u1.items():
    print(f"  {k}: {v}")

# --- User 2: Creates "Beta Inc" ---
u2 = signup("bob@beta.com", "Bob Smith", "bob12345", org_name="Beta Inc")
print("\n=== USER 2 (Bob) - Creates Beta Inc ===")
for k, v in u2.items():
    print(f"  {k}: {v}")

# --- User 3: Joins Alice's "Alpha Corp" ---
u3 = signup("charlie@alpha.com", "Charlie Brown", "charlie1", org_id=u1["organization_id"])
print("\n=== USER 3 (Charlie) - Joins Alpha Corp ===")
for k, v in u3.items():
    print(f"  {k}: {v}")

# --- Comparison ---
print("\n" + "=" * 55)
print("ORG ID COMPARISON:")
print(f"  Alice   org: {u1['organization_id']}  ({u1['organization_name']})")
print(f"  Bob     org: {u2['organization_id']}  ({u2['organization_name']})")
print(f"  Charlie org: {u3['organization_id']}  ({u3['organization_name']})")
print(f"\n  Alice & Bob same org?     {u1['organization_id'] == u2['organization_id']}")
print(f"  Alice & Charlie same org? {u1['organization_id'] == u3['organization_id']}")

# --- Login test ---
print("\n=== LOGIN TEST (Bob) ===")
login_res = login("bob@beta.com", "bob12345")
for k, v in login_res.items():
    print(f"  {k}: {v}")
