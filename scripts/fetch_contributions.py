#!/usr/bin/env python3
"""Fetch real account data into data/contributions.json and data/profile.json."""
import json, os, re, urllib.request, urllib.error

USER = os.environ.get("GH_USER", "TanmayKhatriLFM")
TOKEN = os.environ["GITHUB_TOKEN"]
H = {"Authorization": "bearer " + TOKEN, "Accept": "application/vnd.github+json"}


def call(url, data=None):
    req = urllib.request.Request(url, data=data, headers={**H, "Content-Type": "application/json"})
    return urllib.request.urlopen(req)


# contribution calendar (GraphQL)
Q = """query($u:String!){user(login:$u){createdAt contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
res = json.load(call("https://api.github.com/graphql", json.dumps({"query": Q, "variables": {"u": USER}}).encode()))
u = res["data"]["user"]
days = [{"date": d["date"], "count": d["contributionCount"]}
        for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
os.makedirs("data", exist_ok=True)
json.dump({"days": days}, open("data/contributions.json", "w"))

# repos + commit counts (REST; per_page=1 and read the last page from the Link header)
repos = []
for r in json.load(call(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")):
    if r["name"].lower() == USER.lower():
        continue  # the profile repo itself
    try:
        resp = call(f"https://api.github.com/repos/{USER}/{r['name']}/commits?per_page=1")
        link = resp.headers.get("Link", "")
        m = re.search(r'[?&]page=(\d+)>; rel="last"', link)
        commits = int(m.group(1)) if m else len(json.load(resp))
    except urllib.error.HTTPError:
        commits = 0  # empty repository
    repos.append({"name": r["name"], "language": r["language"], "commits": commits, "pushed_at": r["pushed_at"],
                  "fork": r["fork"], "stars": r["stargazers_count"], "description": r["description"]})
json.dump({"login": USER, "created_at": u["createdAt"], "repos": repos}, open("data/profile.json", "w"), indent=1)
print(len(days), "days,", len(repos), "repos")
