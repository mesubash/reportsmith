#!/usr/bin/env python3
"""Post a report from stdin to a Discord webhook ($DISCORD_WEBHOOK or $URL_ENV's variable).

First line is the title. Fits Discord's limits: 2,000 chars of content,
4,096 in one embed description; longer reports are cut with a note.
"""
import json
import os
import sys
import urllib.request

CONTENT_MAX, EMBED_MAX = 2000, 4096


def payload(text):
    text = text.strip()
    if len(text) <= CONTENT_MAX:
        return {"content": text}
    title, _, body = text.partition("\n")
    title = title.lstrip("#* ").rstrip("*")[:256]
    if len(body) > EMBED_MAX:
        body = body[: EMBED_MAX - 40].rsplit("\n", 1)[0] + "\n\n(cut; full report saved locally)"
    return {"embeds": [{"title": title, "description": body.strip()}]}


def main():
    url = os.environ.get(os.environ.get("URL_ENV", "DISCORD_WEBHOOK"), "")
    if not url:
        sys.exit("DISCORD_WEBHOOK is not set")
    req = urllib.request.Request(url, data=json.dumps(payload(sys.stdin.read())).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "reportsmith"})
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f"discord: HTTP {r.status}")


if __name__ == "__main__":
    main()
