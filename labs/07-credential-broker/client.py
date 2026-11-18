import json
from urllib.request import Request, urlopen


payload = {
    "repository": "opsworld30/sandbox-demo",
    "branch": "agent/lab-07",
    "commit": "0123456789abcdef0123456789abcdef01234567",
}
request = Request(
    "http://127.0.0.1:8765/git/push",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(request, timeout=3) as response:
    body = response.read().decode()
    print(body)
    if "ghp_FAKE" in body:
        raise SystemExit("ERROR: credential leaked in response")
