import requests

API_KEY = "rnd_ItkSEWCGyTe0920g3qIdZrHdvUeO"

H = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
BASE = "https://api.render.com/v1"

# 1. Workspaces zote unazoweza kuziona
owners = requests.get(f"{BASE}/owners?limit=100", headers=H).json()
print("WORKSPACES ZAKO:")
for o in owners:
    print(f"  - {o['owner']['name']}  ({o['owner']['id']})")
print()

# 2. Services ZOTE kila workspace (na pagination)
for o in owners:
    oid = o["owner"]["id"]
    print(f"════ Workspace: {o['owner']['name']} ════")
    cursor = ""
    while True:
        url = f"{BASE}/services?ownerId={oid}&limit=100" + (f"&cursor={cursor}" if cursor else "")
        batch = requests.get(url, headers=H).json()
        if not batch:
            break
        for item in batch:
            svc = item["service"]
            doms = requests.get(
                f"{BASE}/services/{svc['id']}/custom-domains?limit=50", headers=H
            ).json()
            names = [d["customDomain"]["name"] for d in doms]
            flag = " ⚠️" if any("jamiitek.com" in n for n in names) else ""
            print(f"  {svc['name']} ({svc['id']}) [{svc.get('suspended','?')}]{flag}")
            for n in names:
                print(f"      → {n}")
        cursor = batch[-1].get("cursor", "")
        if len(batch) < 100 or not cursor:
            break
    print()