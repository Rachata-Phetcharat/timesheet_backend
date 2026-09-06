import urllib.request
import urllib.parse
import json

base_url = "http://localhost:8000"

req = urllib.request.Request(
    f"{base_url}/auth/login",
    data=json.dumps({"email": "admin@timesheet.com", "password": "admin1234"}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())
    token = data["access_token"]

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

try:
    req = urllib.request.Request(f"{base_url}/attendance/clock-in", data=json.dumps({"notes": "test"}).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        print("Clock in status:", response.status)
        print("Clock in response:", response.read().decode())
except urllib.error.HTTPError as e:
    print("Clock in status:", e.code)
    print("Clock in response:", e.read().decode())
