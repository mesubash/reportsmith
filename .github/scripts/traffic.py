#!/usr/bin/env python3
"""Append GitHub traffic (clones, views, referrers) to CSV files.

GitHub keeps traffic for 14 days. Run daily; each run rewrites the rows for
the dates GitHub still reports (its latest numbers win) and keeps older rows.

  GH_TOKEN=... python3 traffic.py owner/repo <out-dir>
"""
import csv
import datetime
import json
import os
import sys
import urllib.request


def get(repo, path, token):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/traffic/{path}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "User-Agent": "reportsmith-traffic"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def merge(path, key, header, new_rows):
    rows = {}
    if os.path.exists(path):
        with open(path, newline="") as f:
            rows = {tuple(r[k] for k in key): r for r in csv.DictReader(f)}
    for r in new_rows:
        rows[tuple(str(r[k]) for k in key)] = {h: str(r[h]) for h in header}
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: tuple(r[k] for k in key)))
    return len(rows)


def daily(clones, views):
    days = {}
    for c in clones.get("clones", []):
        days.setdefault(c["timestamp"][:10], {}).update(clones=c["count"], unique_clones=c["uniques"])
    for v in views.get("views", []):
        days.setdefault(v["timestamp"][:10], {}).update(views=v["count"], unique_views=v["uniques"])
    return [{"date": d, "clones": x.get("clones", 0), "unique_clones": x.get("unique_clones", 0),
             "views": x.get("views", 0), "unique_views": x.get("unique_views", 0)} for d, x in days.items()]


def badges(daily_csv, out):
    """shields.io endpoint files with all-time totals, for README badges."""
    with open(daily_csv, newline="") as f:
        rows = list(csv.DictReader(f))
    for field, label in (("clones", "clones"), ("views", "views")):
        total = sum(int(r[field]) for r in rows)
        with open(os.path.join(out, f"badge-{field}.json"), "w") as f:
            json.dump({"schemaVersion": 1, "label": label, "message": f"{total:,}", "color": "58a6ff"}, f)


def main():
    repo, out = sys.argv[1], sys.argv[2]
    token = os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GH_TOKEN is not set. Add a TRAFFIC_TOKEN secret: fine-grained token, this repo only, "
                 "Administration: read-only.")
    os.makedirs(out, exist_ok=True)
    n = merge(os.path.join(out, "daily.csv"), ["date"],
              ["date", "clones", "unique_clones", "views", "unique_views"],
              daily(get(repo, "clones", token), get(repo, "views", token)))
    today = datetime.date.today().isoformat()
    refs = [{"date": today, "referrer": r["referrer"], "count": r["count"], "uniques": r["uniques"]}
            for r in get(repo, "popular/referrers", token)]
    merge(os.path.join(out, "referrers.csv"), ["date", "referrer"], ["date", "referrer", "count", "uniques"], refs)
    badges(os.path.join(out, "daily.csv"), out)
    print(f"daily.csv: {n} days; referrers today: {len(refs)}")


if __name__ == "__main__":
    main()
