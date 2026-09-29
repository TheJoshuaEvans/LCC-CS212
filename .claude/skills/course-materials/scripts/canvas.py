#!/usr/bin/env python3
"""Read-only helper for the CS 212 Canvas course.

Loads CANVAS_KEY from the project's .env (or the environment) and never prints it.

Usage:
    canvas.py course                 Course info
    canvas.py modules                Modules and their items
    canvas.py assignments            Assignments with due dates (Pacific time)
    canvas.py assignment <id>        One assignment, description as text
    canvas.py page <url-or-title>    A wiki page as text
    canvas.py syllabus               Syllabus body as text
    canvas.py announcements          Recent announcements
    canvas.py get <api-path>         Raw JSON for any GET path under /courses/<id>
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = "https://canvas.lanecc.edu/api/v1"
COURSE_ID = 3948
PACIFIC = ZoneInfo("America/Los_Angeles")
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def load_key():
    key = os.environ.get("CANVAS_KEY")
    env_file = PROJECT_ROOT / ".env"
    if not key and env_file.exists():
        for line in env_file.read_text().splitlines():
            name, sep, value = line.strip().removeprefix("export ").partition("=")
            if sep and name.strip() == "CANVAS_KEY":
                key = value.strip().strip("'\"")
    if not key:
        sys.exit(f"CANVAS_KEY not found in environment or {env_file}")
    return key


KEY = load_key()


def request(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp), resp.headers.get("Link", "")
    except urllib.error.HTTPError as err:
        if err.code == 401:
            # Lane's Canvas tokens last at most 90 days
            sys.exit(
                "CANVAS AUTH FAILED (401): CANVAS_KEY is expired, revoked, or wrong.\n"
                "Renew it in Canvas: Account > Settings > Approved Integrations > + New Access Token,\n"
                f"then replace CANVAS_KEY in {PROJECT_ROOT / '.env'}."
            )
        sys.exit(f"Canvas request failed: HTTP {err.code} {err.reason} for {url.split('?')[0]}")


def api(path, **params):
    """GET a course-relative path, following pagination for list results."""
    params.setdefault("per_page", 100)
    url = f"{BASE}/courses/{COURSE_ID}{path}?{urllib.parse.urlencode(params, doseq=True)}"
    data, link = request(url)
    while isinstance(data, list):
        next_url = re.search(r'<([^>]+)>;\s*rel="next"', link)
        if not next_url:
            break
        more, link = request(next_url.group(1))
        data += more
    return data


class _TextExtractor(HTMLParser):
    BLOCKS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCKS:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")
        href = dict(attrs).get("href")
        if tag == "a" and href:
            self.parts.append(f"[{href}] ")

    def handle_data(self, data):
        self.parts.append(data)


def html_to_text(html):
    parser = _TextExtractor()
    parser.feed(html or "")
    text = "".join(parser.parts)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def pacific(iso, missing="no due date"):
    if not iso:
        return missing
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(PACIFIC)
    return dt.strftime("%a %b %d %I:%M %p")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]

    if cmd == "course":
        c = api("")
        print(f"{c['name']} (id {c['id']}), time zone {c['time_zone']}")
    elif cmd == "modules":
        for m in api("/modules", **{"include[]": "items"}):
            print(f"# {m['name']}")
            for i in m.get("items", []):
                url = i.get("external_url") or i.get("page_url") or ""
                print(f"   - {i['type']}: {i['title']}" + (f"  <{url}>" if url else ""))
    elif cmd == "assignments":
        for a in api("/assignments", order_by="due_at"):
            print(f"- [{a['id']}] {a['name']} | due {pacific(a.get('due_at'))} | {a.get('points_possible')} pts")
    elif cmd == "assignment" and args:
        a = api(f"/assignments/{args[0]}")
        print(f"{a['name']} | due {pacific(a.get('due_at'))} | {a.get('points_possible')} pts\n")
        print(html_to_text(a.get("description")))
    elif cmd == "page" and args:
        slug = urllib.parse.quote(args[0].lower().replace(" ", "-"), safe="-")
        p = api(f"/pages/{slug}")
        print(f"{p['title']}\n")
        print(html_to_text(p.get("body")))
    elif cmd == "syllabus":
        print(html_to_text(api("", **{"include[]": "syllabus_body"}).get("syllabus_body")))
    elif cmd == "announcements":
        data, _ = request(f"{BASE}/announcements?context_codes[]=course_{COURSE_ID}&per_page=20")
        for a in data:
            print(f"## {a['title']} ({pacific(a.get('posted_at') or a.get('created_at'), 'unscheduled')})\n{html_to_text(a.get('message'))}\n")
    elif cmd == "get" and args:
        print(json.dumps(api(args[0]), indent=2))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
