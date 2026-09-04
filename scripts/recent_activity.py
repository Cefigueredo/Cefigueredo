"""Rewrite the 'recently shipped' block in README.md from the GitHub API."""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone

USER = "Cefigueredo"
START, END = "<!--START_SECTION:activity-->", "<!--END_SECTION:activity-->"
MAX_ROWS = 5

def get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "User-Agent": "profile-readme-bot",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def ago(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    d = (datetime.now(timezone.utc) - dt).days
    if d == 0: return "today"
    if d == 1: return "yesterday"
    if d < 30: return f"{d} days ago"
    if d < 365: return f"{d // 30} month{'s' if d // 30 > 1 else ''} ago"
    return f"{d // 365} year{'s' if d // 365 > 1 else ''} ago"

repos = get(f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=100")
repos = [r for r in repos if not r["fork"] and not r["archived"] and r["name"] != USER]
rows = ["| Repo | What | Last push |", "|:--|:--|:--|"]
for r in repos[:MAX_ROWS]:
    lang = f" `{r['language']}`" if r.get("language") else ""
    rows.append(f"| [**{r['name']}**]({r['html_url']}){lang} | {r.get('description') or '_no description yet_'} | {ago(r['pushed_at'])} |")
block = "\n".join(rows)

readme = open("README.md", encoding="utf-8").read()
new = re.sub(re.escape(START) + r".*?" + re.escape(END),
             f"{START}\n{block}\n{END}", readme, flags=re.S)
if new != readme:
    open("README.md", "w", encoding="utf-8").write(new)
    print("README updated"); sys.exit(0)
print("No changes")
