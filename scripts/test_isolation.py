"""Test: Verify tenant isolation — users cannot access other orgs' data"""
import urllib.request
import json
import time

API = "http://localhost:8000"
TS = str(int(time.time()))

def post(url, body):
    req = urllib.request.Request(f"{API}{url}", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())

def get(url):
    return json.loads(urllib.request.urlopen(f"{API}{url}").read())

def get_expect_error(url, expected_code):
    try:
        urllib.request.urlopen(f"{API}{url}")
        print(f"  FAIL: expected {expected_code} but got 200")
        return False
    except urllib.error.HTTPError as e:
        if e.code == expected_code:
            detail = json.loads(e.read()).get("detail", "")
            print(f"  PASS: got {e.code}: {detail}")
            return True
        else:
            print(f"  FAIL: expected {expected_code} but got {e.code}")
            return False

# Setup: Create two users in separate orgs
alice = post("/api/auth/signup", {"email": f"alice_{TS}@test.com", "name": "Alice", "password": "test1234", "organization_name": "Org A"})
bob = post("/api/auth/signup", {"email": f"bob_{TS}@test.com", "name": "Bob", "password": "test1234", "organization_name": "Org B"})

print(f"Alice: org={alice['organization_name']}")
print(f"Bob:   org={bob['organization_name']}")
print()

# Test 1: Alice can list her own org's connections
print("=== TEST 1: Alice lists HER org's connections ===")
try:
    result = get(f"/api/connections/org/{alice['organization_id']}?user_id={alice['user_id']}")
    print(f"  PASS: Alice sees {len(result)} connections in her org")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Bob CANNOT list Alice's org's connections
print("\n=== TEST 2: Bob tries to list ALICE's org connections ===")
get_expect_error(f"/api/connections/org/{alice['organization_id']}?user_id={bob['user_id']}", 403)

# Test 3: Request without user_id should fail (422 - missing required param)
print("\n=== TEST 3: List connections without user_id ===")
get_expect_error(f"/api/connections/org/{alice['organization_id']}", 422)

# Test 4: Bob lists his own org (should work)
print("\n=== TEST 4: Bob lists HIS org's connections ===")
try:
    result = get(f"/api/connections/org/{bob['organization_id']}?user_id={bob['user_id']}")
    print(f"  PASS: Bob sees {len(result)} connections in his org")
except Exception as e:
    print(f"  FAIL: {e}")

print("\n=== ALL TENANT ISOLATION TESTS COMPLETE ===")
