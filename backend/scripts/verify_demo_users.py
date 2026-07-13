import json
import urllib.request

BASE = "http://localhost:8000"
PASS = "nexo1234"
USERS = [
    ("local.agricultor@nexo.test", "farmer"),
    ("local.perito@nexo.test", "tech"),
    ("local.cooperativa@nexo.test", "tech"),
]

for email, exp_role in USERS:
    req = urllib.request.Request(
        BASE + "/api/v1/auth/login",
        data=json.dumps({"email": email, "password": PASS}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        tok = json.loads(resp.read())
    req2 = urllib.request.Request(
        BASE + "/api/v1/users/me",
        headers={"Authorization": "Bearer " + tok["access_token"]},
    )
    with urllib.request.urlopen(req2) as resp:
        profile = json.loads(resp.read())
    ok = "OK" if profile["role"] == exp_role else "FAIL"
    print(
        f"[{ok}] {email} -> role={profile['role']}, "
        f"siex_module={profile.get('has_siex_module')}, "
        f"siex_enterprise={profile.get('has_siex_enterprise')}"
    )
