#!/usr/bin/env python3
"""Score local business websites 0-10 on how much they need a new site.

Usage:
    python3 audit_sites.py <url-or-"none"> [<url-or-"none"> ...]
    python3 audit_sites.py --file prospects.json   # [{"name": ..., "website": ...}, ...]

Prints one JSON object per input on stdout, as a JSON list:
    {"name", "website", "final_url", "score", "reasons": [...], "checks": {...}}
"score" is null when the site blocked the check or timed out: open it in a
browser and score it by hand with the same rules.

Score (10 = most in need):
    no website, or it does not load (error, 4xx/5xx)  -> 10
    otherwise 2 points each for:
      no HTTPS                       (final URL is http://, or https fails)
      not mobile friendly            (no <meta name="viewport">)
      slow                           (first response over 3 s, or HTML over 2 MB)
      no clear booking/contact path  (no tel:, mailto:, booking or contact link/button)
      out of date                    (newest copyright year older than last year)

Stdlib only. Read-only: it fetches each home page once and never submits anything.
"""

import concurrent.futures
import datetime
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

TIMEOUT = 15
SLOW_SECONDS = 3.0
HEAVY_BYTES = 2 * 1024 * 1024
MAX_READ = 4 * 1024 * 1024
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

BOOKING_WORDS = re.compile(
    r"book(ing)?|appointment|schedule|reserve|reservation|contact|get in touch|"
    r"enquir|inquir|request a (quote|call)|call us|calendly|cal\.com|setmore|"
    r"acuity|square\s?appointments|opentable|fresha|booksy",
    re.I,
)
LINK_OR_BUTTON = re.compile(r"<(a|button)\b[^>]*>(.*?)</\1>", re.I | re.S)
COPYRIGHT = re.compile(r"(?:©|&copy;|copyright)\s*(?:[^0-9<]{0,20})?((?:19|20)\d{2})(?:\s*[-–]\s*((?:19|20)\d{2}))?", re.I)
VIEWPORT = re.compile(r"<meta[^>]+name\s*=\s*[\"']?viewport\b", re.I)


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    ctx = ssl.create_default_context()
    started = time.monotonic()
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
        first_byte = time.monotonic() - started
        body = resp.read(MAX_READ)
        return resp.geturl(), resp.status, first_byte, body


def _normalise(url):
    url = (url or "").strip()
    if not url or url.lower() in {"none", "null", "-", "n/a"}:
        return ""
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    return url


def audit(name, website):
    url = _normalise(website)
    result = {"name": name, "website": website or "", "final_url": "", "score": 0,
              "reasons": [], "checks": {}}
    if not url:
        result.update(score=10, reasons=["No website"])
        result["checks"]["reachable"] = False
        return result

    fetched, https_failed = None, False
    try:
        fetched = _fetch(url)
    except Exception as exc:  # noqa: BLE001 — any failure means try plain http
        if _blocked(exc):
            return _unchecked(result, exc)
        if url.lower().startswith("https://"):
            https_failed = True
            try:
                fetched = _fetch("http://" + url[len("https://"):])
            except Exception as exc2:  # noqa: BLE001
                if _blocked(exc2):
                    return _unchecked(result, exc2)
                result.update(score=10, reasons=[f"Website does not load ({_short(exc2)})"])
                result["checks"]["reachable"] = False
                return result
        else:
            result.update(score=10, reasons=[f"Website does not load ({_short(exc)})"])
            result["checks"]["reachable"] = False
            return result

    final_url, status, first_byte, body = fetched
    result["final_url"] = final_url
    checks = result["checks"]
    checks["reachable"] = True
    checks["status"] = status
    if status >= 400:
        result.update(score=10, reasons=[f"Website returns an error (HTTP {status})"])
        return result

    html = body.decode("utf-8", errors="replace")
    score, reasons = 0, []

    no_https = https_failed or final_url.lower().startswith("http://")
    checks["https"] = not no_https
    if no_https:
        score += 2
        reasons.append("No HTTPS (browsers mark it 'Not secure')")

    mobile = bool(VIEWPORT.search(html))
    checks["mobile_viewport"] = mobile
    if not mobile:
        score += 2
        reasons.append("Not mobile friendly (no viewport tag)")

    checks["first_response_seconds"] = round(first_byte, 2)
    checks["html_bytes"] = len(body)
    if first_byte > SLOW_SECONDS or len(body) > HEAVY_BYTES:
        score += 2
        reasons.append(f"Slow (first response {first_byte:.1f}s, page {len(body)//1024} KB)")

    has_booking = "tel:" in html.lower() or "mailto:" in html.lower()
    if not has_booking:
        for _tag, inner in LINK_OR_BUTTON.findall(html):
            text = re.sub(r"<[^>]+>", " ", inner)
            if BOOKING_WORDS.search(text):
                has_booking = True
                break
    if not has_booking and re.search(r"href=[\"'][^\"']*(book|appointment|contact|schedule)", html, re.I):
        has_booking = True
    checks["booking_or_contact"] = has_booking
    if not has_booking:
        score += 2
        reasons.append("No clear booking or contact button")

    years = []
    for start, end in COPYRIGHT.findall(html):
        years.append(int(end or start))
    newest = max(years) if years else None
    checks["copyright_year"] = newest
    this_year = datetime.date.today().year
    if newest is not None and newest < this_year - 1:
        score += 2
        reasons.append(f"Looks out of date (copyright {newest})")

    result["score"] = score
    result["reasons"] = reasons or ["No obvious problems found"]
    return result


def _blocked(exc):
    """A bot wall or a slow server, not proof the site is broken."""
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in (401, 403, 406, 429, 503)
    reason = getattr(exc, "reason", exc)
    return isinstance(reason, (TimeoutError, ssl.SSLError)) or "timed out" in str(reason).lower()


def _unchecked(result, exc):
    result.update(score=None, reasons=[f"Could not check automatically ({_short(exc)}); open it in the browser"])
    result["checks"]["reachable"] = None
    return result


def _short(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTP {exc.code}"
    if isinstance(exc, urllib.error.URLError):
        return str(exc.reason)[:80]
    return type(exc).__name__


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--file":
        with open(argv[1], encoding="utf-8") as fh:
            items = [(p.get("name", ""), p.get("website", "")) for p in json.load(fh)]
    else:
        items = [("", u) for u in argv]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda it: audit(*it), items))
    results.sort(key=lambda r: -1 if r["score"] is None else r["score"], reverse=True)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
