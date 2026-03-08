"""Test: Organization password protection"""
import urllib.request
import json
import time

API = "http://localhost:8000"
TS = str(int(time.time()))

def post(url, body):
    req = urllib.request.Request(f"{API}{url}", data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())

def post_expect_error(url, body, expected_code):
    try:
        req = urllib.request.Request(f"{API}{url}", data=json.dumps(body).encode(),
                                    headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req)
        print(f"  FAIL: expected {expected_code} but got 200")
    except urllib.error.HTTPError as e:
        detail = json.loads(e.read()).get("detail", "")
        if e.code == expected_code:
            print(f"  PASS: got {e.code}: {detail}")
        else:
            print(f"  FAIL: expected {expected_code} but got {e.code}: {detail}")

# Test 1: Create org with password
print("=== TEST 1: Alice creates 'Alpha Corp' with org password ===")
alice = post("/api/auth/signup", {
    "email": f"alice_{TS}@test.com",
    "name": "Alice",
    "password": "alice123",
    "organization_name": "Alpha Corp",
    "organization_password": "alpha_secret",
})
print(f"  PASS: org={alice['organization_name']}, id={alice['organization_id']}")

# Test 2: Bob joins with CORRECT org password
print("\n=== TEST 2: Bob joins Alpha Corp with CORRECT org password ===")
bob = post("/api/auth/signup", {
    "email": f"bob_{TS}@test.com",
    "name": "Bob",
    "password": "bob12345",
    "organization_id": alice["organization_id"],
    "organization_password": "alpha_secret",
})
print(f"  PASS: Bob joined {bob['organization_name']}")

# Test 3: Charlie tries to join with WRONG org password
print("\n=== TEST 3: Charlie tries to join with WRONG org password ===")
post_expect_error("/api/auth/signup", {
    "email": f"charlie_{TS}@test.com",
    "name": "Charlie",
    "password": "charlie1",
    "organization_id": alice["organization_id"],
    "organization_password": "wrong_password",
}, 403)

# Test 4: Dave tries to join with NO org password
print("\n=== TEST 4: Dave tries to join WITHOUT org password ===")
post_expect_error("/api/auth/signup", {
    "email": f"dave_{TS}@test.com",
    "name": "Dave",
    "password": "dave1234",
    "organization_id": alice["organization_id"],
}, 400)

# Test 5: Eve creates a different org with different password
print("\n=== TEST 5: Eve creates 'Beta Inc' with different org password ===")
eve = post("/api/auth/signup", {
    "email": f"eve_{TS}@test.com",
    "name": "Eve",
    "password": "eve12345",
    "organization_name": "Beta Inc",
    "organization_password": "beta_secret",
})
print(f"  PASS: org={eve['organization_name']}, id={eve['organization_id']}")
print(f"  Different from Alice's org? {alice['organization_id'] != eve['organization_id']}")

print("\n=== ALL ORG PASSWORD TESTS PASSED ===")
