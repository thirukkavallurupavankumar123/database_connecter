#!/usr/bin/env python
"""Test full MySQL flow: login → list connections → fetch schema → query"""
import urllib.request
import json

API = "http://localhost:8000"

def post(path, data):
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read())

def get(path):
    req = urllib.request.Request(f"{API}{path}")
    return json.loads(urllib.request.urlopen(req).read())

# 1. Login
print("=== STEP 1: Login ===")
user = post("/api/auth/login", {
    "email": "final_test_1772967302@render.com",
    "password": "secure1234"
})
print(f"  User: {user['user_name']}")
print(f"  Org: {user['organization_name']}")
user_id = user["user_id"]
org_id = user["organization_id"]

# 2. List connections
print("\n=== STEP 2: List Connections ===")
conns = get(f"/api/connections/org/{org_id}?user_id={user_id}")
print(f"  Found {len(conns)} connection(s)")
for c in conns:
    print(f"    - {c['name']} ({c['db_type']}): {c['database_name']}")
    conn_id = c["id"]

# 3. Get schema
print("\n=== STEP 3: Fetch MySQL Schema ===")
schema = get(f"/api/connections/{conn_id}/schema?user_id={user_id}")
tables = schema.get("tables", [])
print(f"  Found {len(tables)} table(s)")
for t in tables[:10]:
    print(f"    - {t['name']}: {len(t['columns'])} columns")

# 4. Query (ask natural language)
print("\n=== STEP 4: Test Natural Language Query ===")
try:
    result = post("/api/query/ask", {
        "connection_id": conn_id,
        "user_id": user_id,
        "question": "Show me the first 5 rows of any table"
    })
    print(f"  SQL Generated: {result.get('sql', 'N/A')[:100]}...")
    print(f"  Rows returned: {len(result.get('data', []))}")
except urllib.error.HTTPError as e:
    print(f"  Query error: {e.code} - {json.loads(e.read()).get('detail', 'Unknown')}")

print("\n=== ALL TESTS COMPLETE ===")
