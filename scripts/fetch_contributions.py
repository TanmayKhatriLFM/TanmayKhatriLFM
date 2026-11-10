#!/usr/bin/env python3
"""Fetch the last year of contributions into data/contributions.json."""
import json, os, urllib.request

USER = os.environ.get("GH_USER", "TanmayKhatriLFM")
Q = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
    headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json"})
res = json.load(urllib.request.urlopen(req))
weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
os.makedirs("data", exist_ok=True)
json.dump({"days": days}, open("data/contributions.json", "w"))
print(len(days), "days")
