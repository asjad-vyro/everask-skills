#!/usr/bin/env python3
"""Read-only job listings aggregated across multiple public boards — stdlib only.

Queries several free, no-auth job APIs and merges them into one normalized,
de-duplicated list, ranked by title relevance to the search (newest-first
within each band):

  remotive        remotive.com        remote-only, all categories, server search
  remoteok        remoteok.com        remote-only, tech-heavy
  arbeitnow       arbeitnow.com       EU + remote, all fields
  jobicy          jobicy.com          remote-only, tag search
  himalayas       himalayas.app       remote-only, all categories
  workingnomads   workingnomads.com   remote-only, all categories
  weworkremotely  weworkremotely.com  remote-only, all categories (RSS)
  jobspresso      jobspresso.co       remote-only, curated (RSS)
  fourdayweek     4dayweek.io         4-day-week roles, remote + on-site
  landingjobs     landing.jobs        Europe tech, on-site + remote
  greenhouse      boards-api.greenhouse.io  curated big-company boards
  lever           api.lever.co        curated big-company boards
  pythonorg       python.org/jobs     Python roles (RSS)
  larajobs        larajobs.com        Laravel/PHP roles (RSS)

Commands:
  sources             list the boards this skill queries
  list   [filters]    query all (or selected) boards and merge

All output is JSON on stdout. Per-board failures are non-fatal: the board is
skipped, a note goes to stderr, and the run continues with whatever succeeded.
A total failure (or bad args) yields ``{ "error": ... }`` so output is always
parseable.

Pass ``--xlsx PATH`` to also write every returned listing to a spreadsheet
(stdlib only: the .xlsx is assembled by hand), and ``--extra FILE`` to add
postings found by web search to that spreadsheet. Pass ``--days N`` to keep
only listings posted in the last N days.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.sax.saxutils import escape as _xml_escape

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def _get(url, params=None, timeout=25):
    """GET a URL and parse JSON. Raises on network/HTTP/parse failure."""
    if params:
        params = {k: v for k, v in params.items() if v not in (None, "")}
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def _clean(text):
    """Strip HTML entities/tags a couple of boards leak into plain fields."""
    if not isinstance(text, str):
        return text
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
    # Some boards send UTF-8 that was decoded as Latin-1 once too often
    # ('MÃ©xico'). Undo it only when the result is valid UTF-8.
    if re.search("[Â-ô][\u0080-¿]", text):
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return text


def _epoch_to_iso(epoch):
    try:
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc).isoformat()
    except (ValueError, TypeError, OSError):
        return None


def _rfc822_to_iso(text):
    try:
        return parsedate_to_datetime(text).isoformat()
    except (TypeError, ValueError):
        return None


def _norm_date(value):
    """Any date a board gives (epoch, ISO, RFC 822) -> 'YYYY-MM-DDTHH:MM:SSZ' in UTC.

    Returns None when it cannot be read, so sorting and --days compare one format.
    """
    if value in (None, ""):
        return None
    dt = None
    try:
        num = float(value)  # epoch seconds or milliseconds
        dt = datetime.fromtimestamp(num / 1000.0 if num > 1e11 else num,
                                    tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        text = str(value).strip()
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            try:
                dt = parsedate_to_datetime(text)
            except (TypeError, ValueError, IndexError):
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_xml(url, timeout=25):
    """GET a URL and parse it as an RSS/XML document."""
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return ET.fromstring(resp.read().decode("utf-8", "replace"))


def _salary_range(lo, hi, currency=None):
    """'50000, 67000, EUR' -> '50,000 – 67,000 EUR'; None unless both ends set."""
    try:
        lo, hi = int(lo or 0), int(hi or 0)
    except (TypeError, ValueError):
        return None
    if not (lo and hi):
        return None
    if currency and currency not in ("$", "USD"):
        return f"{lo:,} – {hi:,} {currency}"
    return f"${lo:,} – ${hi:,}"


def _job(*, title, company, location, is_remote, apply_url, source,
         posted_at=None, salary=None, job_type=None, category=None, tags=None,
         id=None):
    """Build the stable normalized shape every board maps onto."""
    return {
        "id": id,
        "title": _clean(title),
        "company": _clean(company),
        "category": _clean(category),
        "location": _clean(location) or ("Remote" if is_remote else None),
        "is_remote": bool(is_remote),
        "salary": (salary or None) if not isinstance(salary, str) else (salary.strip() or None),
        "job_type": job_type,
        "tags": tags or [],
        "apply_url": apply_url,
        "source": source,
        "posted_at": _norm_date(posted_at),
    }


def _term_in(term, text, compact):
    """Substring match tolerant of plurals and hyphen/space splits.

    'engineers' matches 'Engineer'; 'frontend' matches 'Front-End' (via the
    compact form with hyphens/spaces stripped).
    """
    cands = {term, term.replace("-", "")}
    if term.endswith("s") and len(term) > 3:
        cands.add(term[:-1])
    return any(c in text or c.replace("-", "") in compact for c in cands if c)


def _haystacks(job):
    """(lowercase haystack, compact haystack) for a job."""
    hay = " ".join(str(x) for x in (
        job["title"] or "", job["company"] or "", job["category"] or "",
        " ".join(job["tags"] or []),
    )).lower()
    return hay, hay.replace("-", "").replace(" ", "")


def _matches(job, terms):
    """Client-side filter for boards without server search."""
    if not terms:
        return True
    hay, compact = _haystacks(job)
    return all(_term_in(t, hay, compact) for t in terms)


def _title_hits(job, terms):
    """How many query terms appear in the title — used to rank relevance."""
    title = (job["title"] or "").lower()
    compact = title.replace("-", "").replace(" ", "")
    return sum(1 for t in terms if _term_in(t, title, compact))


_PARENTHETICAL = re.compile(r"\s*[(\[][^)\]]*[)\]]")


def _dedup_key(job):
    """(normalized title, company) — collapses per-city reposts of one role.

    'Staff Product Engineer (Montevideo)' and 'Staff Product Engineer
    (Campinas)' at the same company are one job for our purposes.
    """
    title = _PARENTHETICAL.sub("", (job["title"] or "").lower())
    title = title.split("|")[0]
    title = re.sub(r"[^a-z0-9]+", " ", title).strip()
    return title, (job["company"] or "").lower().strip()


# --- Per-board fetchers -----------------------------------------------------
# Each returns a list of normalized jobs. They may raise; the caller catches.

def fetch_remotive(search, terms, cap):
    data = _get("https://remotive.com/api/remote-jobs",
                {"search": search, "limit": cap})
    out = []
    for j in (data.get("jobs", []) if isinstance(data, dict) else []):
        out.append(_job(
            id=j.get("id"), title=j.get("title"), company=j.get("company_name"),
            category=j.get("category"), location=j.get("candidate_required_location"),
            is_remote=True, salary=j.get("salary"), job_type=j.get("job_type"),
            tags=j.get("tags"), apply_url=j.get("url"), source="remotive",
            posted_at=j.get("publication_date"),
        ))
    # Remotive's server search is loose — tighten with the same client filter.
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_remoteok(search, terms, cap):
    data = _get("https://remoteok.com/api")
    out = []
    for j in data if isinstance(data, list) else []:
        if not isinstance(j, dict) or j.get("legal") or not j.get("position"):
            continue  # first element is a legal notice
        smin, smax = j.get("salary_min") or 0, j.get("salary_max") or 0
        salary = f"${smin:,} – ${smax:,}" if smin and smax else None
        out.append(_job(
            id=j.get("id"), title=j.get("position"), company=j.get("company"),
            location=j.get("location"), is_remote=True, salary=salary,
            tags=j.get("tags"), apply_url=j.get("url"), source="remoteok",
            posted_at=j.get("date"),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_arbeitnow(search, terms, cap):
    data = _get("https://www.arbeitnow.com/api/job-board-api")
    out = []
    for j in (data.get("data", []) if isinstance(data, dict) else []):
        jt = j.get("job_types") or []
        out.append(_job(
            id=j.get("slug"), title=j.get("title"), company=j.get("company_name"),
            location=j.get("location"), is_remote=j.get("remote", False),
            job_type=(jt[0] if jt else None), tags=j.get("tags"),
            apply_url=j.get("url"), source="arbeitnow",
            posted_at=_epoch_to_iso(j.get("created_at")),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_jobicy(search, terms, cap):
    # Over-fetch: Jobicy's tag search only understands single tags — a
    # multi-word phrase skews the result set — so send the first term only
    # and let the client-side filter below do the real work.
    params = {"count": max(cap, 50) if terms else cap}
    if terms:
        params["tag"] = terms[0]
    data = _get("https://jobicy.com/api/v2/remote-jobs", params)
    out = []
    for j in (data.get("jobs", []) if isinstance(data, dict) else []):
        jt = j.get("jobType") or []
        ind = j.get("jobIndustry") or []
        smin, smax = j.get("annualSalaryMin"), j.get("annualSalaryMax")
        salary = f"${smin:,} – ${smax:,}" if smin and smax else None
        out.append(_job(
            id=j.get("id"), title=j.get("jobTitle"), company=j.get("companyName"),
            category=(ind[0] if ind else None), location=j.get("jobGeo"),
            is_remote=True, salary=salary, job_type=(jt[0] if jt else None),
            apply_url=j.get("url"), source="jobicy", posted_at=j.get("pubDate"),
        ))
    # Never trust Jobicy's tag filter — it drops multi-word queries and
    # returns unrelated latest jobs. Always filter client-side.
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_himalayas(search, terms, cap):
    # No server-side search — over-fetch when filtering client-side.
    data = _get("https://himalayas.app/jobs/api",
                {"limit": max(cap, 100) if terms else cap})
    out = []
    for j in (data.get("jobs", []) if isinstance(data, dict) else []):
        cats = j.get("parentCategories") or j.get("categories") or []
        locs = j.get("locationRestrictions") or []
        out.append(_job(
            id=j.get("guid"), title=j.get("title"), company=j.get("companyName"),
            category=(cats[0] if cats else None),
            location=(", ".join(locs) if locs else None), is_remote=True,
            salary=_salary_range(j.get("minSalary"), j.get("maxSalary"),
                                 j.get("currency")),
            job_type=j.get("employmentType"), tags=j.get("categories"),
            apply_url=j.get("applicationLink"), source="himalayas",
            posted_at=_epoch_to_iso(j.get("pubDate")),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_workingnomads(search, terms, cap):
    data = _get("https://www.workingnomads.com/api/exposed_jobs/")
    out = []
    for j in data if isinstance(data, list) else []:
        tags = [t.strip() for t in (j.get("tags") or "").split(",") if t.strip()]
        out.append(_job(
            id=j.get("url"), title=j.get("title"), company=j.get("company_name"),
            category=j.get("category_name"), location=j.get("location"),
            is_remote=True, tags=tags, apply_url=j.get("url"),
            source="workingnomads", posted_at=j.get("pub_date"),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_weworkremotely(search, terms, cap):
    root = _get_xml("https://weworkremotely.com/remote-jobs.rss")
    out = []
    for item in root.findall(".//item"):
        get = lambda tag: (item.findtext(tag) or "").strip()
        # Item titles are "Company: Job Title".
        company, _, title = get("title").partition(": ")
        if not title:
            company, title = None, get("title")
        out.append(_job(
            id=get("guid") or None, title=title, company=company,
            category=get("category") or None, location=get("region") or None,
            is_remote=True, job_type=get("type") or None,
            tags=[s.strip() for s in get("skills").split(",") if s.strip()],
            apply_url=get("link") or None, source="weworkremotely",
            posted_at=_rfc822_to_iso(get("pubDate")),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_jobspresso(search, terms, cap):
    ns = {"jp": "https://jobspresso.co"}
    root = _get_xml("https://jobspresso.co/?feed=job_feed")
    out = []
    for item in root.findall(".//item"):
        get = lambda tag: (item.findtext(tag, namespaces=ns) or "").strip()
        # Feed quirk: jp:job_type holds the category, jp:job_category the type.
        out.append(_job(
            id=get("guid") or None, title=get("title") or None,
            company=get("jp:company") or None, category=get("jp:job_type") or None,
            location=get("jp:location") or None, is_remote=True,
            job_type=get("jp:job_category") or None,
            apply_url=get("link") or None, source="jobspresso",
            posted_at=_rfc822_to_iso(get("pubDate")),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_fourdayweek(search, terms, cap):
    data = _get("https://4dayweek.io/api/jobs")
    out = []
    for j in (data.get("jobs", []) if isinstance(data, dict) else []):
        locs = [", ".join(filter(None, (l.get("city"), l.get("country"))))
                for l in (j.get("locations") or [])]
        stack = [s.get("name") for s in (j.get("stack") or []) if s.get("name")]
        tags = stack + [t for t in (j.get("level"), "4-day week") if t]
        out.append(_job(
            id=j.get("id"), title=j.get("title"), company=j.get("company_name"),
            category=j.get("category"), location=(", ".join(locs) or None),
            is_remote=(j.get("work_arrangement") == "remote"),
            salary=_salary_range(j.get("salary_lower"), j.get("salary_upper"),
                                 j.get("salary_currency")),
            tags=tags, apply_url=f"https://4dayweek.io/job/{j.get('slug')}",
            source="fourdayweek", posted_at=_epoch_to_iso(j.get("posted")),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_landingjobs(search, terms, cap):
    data = _get("https://landing.jobs/api/v1/jobs", {"limit": max(cap, 50)})
    out = []
    for j in data if isinstance(data, list) else []:
        url = j.get("url") or ""
        # Company only appears as the slug in the URL: landing.jobs/at/<company>/…
        m = re.search(r"landing\.jobs/at/([^/]+)/", url)
        company = m.group(1).replace("-", " ").title() if m else None
        locs = [", ".join(filter(None, (l.get("city"), l.get("country_code"))))
                for l in (j.get("locations") or [])]
        out.append(_job(
            id=j.get("id"), title=j.get("title"), company=company,
            location=("; ".join(locs) or None), is_remote=bool(j.get("remote")),
            salary=_salary_range(j.get("gross_salary_low"),
                                 j.get("gross_salary_high"),
                                 j.get("currency_code")),
            job_type=j.get("type"), tags=j.get("tags"), apply_url=url or None,
            source="landingjobs", posted_at=j.get("published_at"),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


# Curated companies whose public ATS boards we aggregate. Slugs verified live;
# a company that stops resolving is skipped (inner try), not fatal.
_GREENHOUSE_COMPANIES = ["gitlab", "stripe", "cloudflare", "figma", "canonical",
                         "duolingo", "elastic"]
_LEVER_COMPANIES = {"spotify": "Spotify", "palantir": "Palantir",
                    "octoenergy": "Octopus Energy", "veeva": "Veeva",
                    "outreach": "Outreach"}


def _fetch_companies(companies, fetch_one, source):
    """Fetch curated company boards concurrently; a dead slug is skipped."""
    out, failed = [], []
    with ThreadPoolExecutor(max_workers=len(companies)) as ex:
        futures = {slug: ex.submit(fetch_one, slug) for slug in companies}
        for slug, fut in futures.items():
            try:
                out.extend(fut.result())
            except Exception as exc:  # one odd response must not sink the board
                failed.append(slug)
                print(f"[skip] {source}/{slug}: {exc}", file=sys.stderr)
    if failed and not out:
        raise ValueError(f"all boards failed: {failed}")
    return out


def fetch_greenhouse(search, terms, cap):
    def one(slug):
        data = _get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
        jobs = []
        for j in (data.get("jobs", []) if isinstance(data, dict) else []):
            loc = (j.get("location") or {}).get("name")
            jobs.append(_job(
                id=j.get("id"), title=j.get("title"),
                company=j.get("company_name") or slug.title(), location=loc,
                is_remote=("remote" in (loc or "").lower()),
                apply_url=j.get("absolute_url"), source="greenhouse",
                posted_at=j.get("first_published") or j.get("updated_at"),
            ))
        return jobs

    out = _fetch_companies(_GREENHOUSE_COMPANIES, one, "greenhouse")
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_lever(search, terms, cap):
    def one(slug):
        data = _get(f"https://api.lever.co/v0/postings/{slug}",
                    {"mode": "json", "limit": 100})
        jobs = []
        for j in data if isinstance(data, list) else []:
            cats = j.get("categories") or {}
            posted = j.get("createdAt")
            jobs.append(_job(
                id=j.get("id"), title=j.get("text"),
                company=_LEVER_COMPANIES[slug],
                category=cats.get("department"), location=cats.get("location"),
                is_remote=(j.get("workplaceType") == "remote"),
                job_type=cats.get("commitment"),
                tags=[t for t in (cats.get("team"),) if t],
                apply_url=j.get("hostedUrl"), source="lever",
                posted_at=_epoch_to_iso(posted // 1000 if posted else None),
            ))
        return jobs

    out = _fetch_companies(_LEVER_COMPANIES, one, "lever")
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_pythonorg(search, terms, cap):
    root = _get_xml("https://www.python.org/jobs/feed/rss/")
    out = []
    for item in root.findall(".//item"):
        get = lambda tag: (item.findtext(tag) or "").strip()
        # Item titles are "Job Title, Company"; description starts with location.
        title, _, company = get("title").rpartition(", ")
        if not title:
            title, company = company, None
        desc = get("description")
        location = _clean(desc.split("<", 1)[0]) or None
        out.append(_job(
            id=get("guid") or None, title=title, company=company,
            category="Python", location=location,
            is_remote=("remote" in (location or "").lower()),
            apply_url=get("link") or None, source="pythonorg",
            posted_at=_rfc822_to_iso(get("pubDate")) if get("pubDate") else None,
        ))
    return [j for j in out if _matches(j, terms)][:cap]


def fetch_larajobs(search, terms, cap):
    ns = {"lj": "https://larajobs.com"}
    root = _get_xml("https://larajobs.com/feed")
    out = []
    for item in root.findall(".//item"):
        get = lambda tag: (item.findtext(tag, namespaces=ns) or "").strip()
        location = get("lj:location") or None
        tags = [t.strip() for t in get("lj:tags").split(",") if t.strip()]
        out.append(_job(
            id=get("guid") or None, title=get("title") or None,
            company=get("lj:company") or None, category="Laravel / PHP",
            location=location,
            is_remote=("remote" in (location or "").lower()),
            salary=get("lj:salary") or None,
            job_type=get("lj:job_type") or None, tags=tags,
            apply_url=get("link") or None, source="larajobs",
            posted_at=_rfc822_to_iso(get("pubDate")),
        ))
    return [j for j in out if _matches(j, terms)][:cap]


BOARDS = {
    "remotive": fetch_remotive,
    "remoteok": fetch_remoteok,
    "arbeitnow": fetch_arbeitnow,
    "jobicy": fetch_jobicy,
    "himalayas": fetch_himalayas,
    "workingnomads": fetch_workingnomads,
    "weworkremotely": fetch_weworkremotely,
    "jobspresso": fetch_jobspresso,
    "fourdayweek": fetch_fourdayweek,
    "landingjobs": fetch_landingjobs,
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "pythonorg": fetch_pythonorg,
    "larajobs": fetch_larajobs,
}


# --- Spreadsheet export -----------------------------------------------------
# A small hand-built .xlsx (a zip of XML parts), so no package is needed.

_XML_BAD = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff￾￿]")
_XLSX_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_XML_HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

# (header, column width); the Link column holds clickable URLs.
_XLSX_COLUMNS = [("Title", 46), ("Company", 26), ("Location", 28), ("Remote", 9),
                 ("Pay", 24), ("Posted", 12), ("Type", 14), ("Source", 15),
                 ("Link", 60), ("Tags", 40)]
_XLSX_LINK_COL = 8

_XLSX_STYLES = (
    _XML_HEAD + f'<styleSheet xmlns="{_XLSX_NS}">'
    '<fonts count="3">'
    '<font><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
    '<font><u/><sz val="11"/><color rgb="FF0563C1"/><name val="Calibri"/></font>'
    '</fonts>'
    '<fills count="3">'
    '<fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FF1F3A5F"/>'
    '<bgColor indexed="64"/></patternFill></fill>'
    '</fills>'
    '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="3">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
    '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    '</cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>')


def _xesc(text):
    """Escape text for XML, dropping characters XML 1.0 cannot hold."""
    return _xml_escape(_XML_BAD.sub("", str(text)), {'"': "&quot;"})


def _xlsx_row(job):
    tags = job.get("tags") or []
    return [job.get("title"), job.get("company"), job.get("location"),
            "Yes" if job.get("is_remote") else "No", job.get("salary"),
            (job.get("posted_at") or "")[:10], job.get("job_type"),
            job.get("source"), job.get("apply_url"),
            ", ".join(str(t) for t in tags) if isinstance(tags, list) else str(tags)]


def write_xlsx(path, jobs):
    """Write listings to one sheet: bold header, filter, frozen header row, clickable links."""
    strings, index = [], {}

    def sst(text):
        if text not in index:
            index[text] = len(strings)
            strings.append(text)
        return index[text]

    def col(i):
        return chr(ord("A") + i)  # fewer than 26 columns

    last_col = col(len(_XLSX_COLUMNS) - 1)
    last_row = len(jobs) + 1
    header = "".join(f'<c r="{col(i)}1" s="1" t="s"><v>{sst(h)}</v></c>'
                     for i, (h, _w) in enumerate(_XLSX_COLUMNS))
    rows, links = [f'<row r="1">{header}</row>'], []
    for n, job in enumerate(jobs, start=2):
        cells = []
        for i, value in enumerate(_xlsx_row(job)):
            text = "" if value is None else _XML_BAD.sub("", str(value)).strip()
            if not text:
                continue
            style = ""
            if i == _XLSX_LINK_COL and re.match(r"https?://", text):
                links.append((f"{col(i)}{n}", text.replace(" ", "%20")))
                style = ' s="2"'
            cells.append(f'<c r="{col(i)}{n}"{style} t="s"><v>{sst(text)}</v></c>')
        rows.append(f'<row r="{n}">{"".join(cells)}</row>')

    cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>'
                   for i, (_h, w) in enumerate(_XLSX_COLUMNS))
    hyperlinks = sheet_rels = ""
    if links:
        hyperlinks = "<hyperlinks>" + "".join(
            f'<hyperlink ref="{ref}" r:id="rId{k}"/>'
            for k, (ref, _u) in enumerate(links, 1)) + "</hyperlinks>"
        sheet_rels = (
            _XML_HEAD + f'<Relationships xmlns="{_PKG_REL_NS}">' + "".join(
                f'<Relationship Id="rId{k}" Type="{_REL_NS}/hyperlink" '
                f'Target="{_xesc(u)}" TargetMode="External"/>'
                for k, (_ref, u) in enumerate(links, 1)) + "</Relationships>")
    sheet = (
        _XML_HEAD + f'<worksheet xmlns="{_XLSX_NS}" xmlns:r="{_REL_NS}">'
        f'<dimension ref="A1:{last_col}{last_row}"/>'
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        '<selection pane="bottomLeft" activeCell="A2" sqref="A2"/>'
        '</sheetView></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        f'<cols>{cols}</cols><sheetData>{"".join(rows)}</sheetData>'
        f'<autoFilter ref="A1:{last_col}{last_row}"/>{hyperlinks}</worksheet>')
    shared = (
        _XML_HEAD + f'<sst xmlns="{_XLSX_NS}" uniqueCount="{len(strings)}">'
        + "".join(f'<si><t xml:space="preserve">{_xesc(s)}</t></si>' for s in strings)
        + "</sst>")
    workbook = (
        _XML_HEAD + f'<workbook xmlns="{_XLSX_NS}" xmlns:r="{_REL_NS}"><sheets>'
        '<sheet name="Job listings" sheetId="1" r:id="rId1"/></sheets></workbook>')
    workbook_rels = (
        _XML_HEAD + f'<Relationships xmlns="{_PKG_REL_NS}">'
        f'<Relationship Id="rId1" Type="{_REL_NS}/worksheet" Target="worksheets/sheet1.xml"/>'
        f'<Relationship Id="rId2" Type="{_REL_NS}/styles" Target="styles.xml"/>'
        f'<Relationship Id="rId3" Type="{_REL_NS}/sharedStrings" Target="sharedStrings.xml"/>'
        '</Relationships>')
    root_rels = (
        _XML_HEAD + f'<Relationships xmlns="{_PKG_REL_NS}">'
        f'<Relationship Id="rId1" Type="{_REL_NS}/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>')
    main_ct = "application/vnd.openxmlformats-officedocument.spreadsheetml"
    content_types = (
        _XML_HEAD + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'<Override PartName="/xl/workbook.xml" ContentType="{main_ct}.sheet.main+xml"/>'
        f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="{main_ct}.worksheet+xml"/>'
        f'<Override PartName="/xl/styles.xml" ContentType="{main_ct}.styles+xml"/>'
        f'<Override PartName="/xl/sharedStrings.xml" ContentType="{main_ct}.sharedStrings+xml"/>'
        '</Types>')

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        z.writestr("xl/styles.xml", _XLSX_STYLES)
        z.writestr("xl/sharedStrings.xml", shared)
        z.writestr("xl/worksheets/sheet1.xml", sheet)
        if sheet_rels:
            z.writestr("xl/worksheets/_rels/sheet1.xml.rels", sheet_rels)


# --- Location matching and output -------------------------------------------

def _loc_match(word, where):
    """A place word against a job's location text.

    Short words ('us', 'uk', 'usa') match whole words only, so 'uk' does not
    match 'Ukraine' and 'us' does not match 'Russia'.
    """
    if len(word) <= 3:
        return re.search(r"(?<![a-z])" + re.escape(word) + r"(?![a-z])",
                         where) is not None
    return word in where


def _render(result):
    """Pretty JSON, but one listing per line so long lists stay short to read."""
    jobs = result.get("jobs")
    if not isinstance(jobs, list):
        return json.dumps(result, indent=2, ensure_ascii=False)
    head = json.dumps({k: v for k, v in result.items() if k != "jobs"},
                      indent=2, ensure_ascii=False)
    body = ",\n".join("    " + json.dumps(j, ensure_ascii=False) for j in jobs)
    return head[:-2] + ',\n  "jobs": [\n' + body + "\n  ]\n}"


def _load_extra(path, existing):
    """Postings found by web search (a JSON list) -> listings for the spreadsheet.

    Each item needs title, company and an http(s) url; location, pay and posted
    (a date) are optional. Duplicates of listings already found are skipped.
    Returns (listings, note), where note says what was skipped or what failed.
    """
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError) as exc:
        return [], f"could not read {path}: {exc}"
    if not isinstance(raw, list):
        return [], "the extra file must hold a JSON list of postings"
    seen = {j["apply_url"] for j in existing} | {_dedup_key(j) for j in existing}
    out, skipped = [], 0
    for item in raw:
        item = item if isinstance(item, dict) else {}
        url = str(item.get("url") or "").strip()
        title, company = _clean(item.get("title")), _clean(item.get("company"))
        if not (title and company and re.match(r"https?://", url)):
            skipped += 1
            continue
        where = _clean(item.get("location")) or None
        job = _job(id=url, title=title, company=company, location=where,
                   is_remote="remote" in (where or "").lower(), apply_url=url,
                   source="web", posted_at=item.get("posted"),
                   salary=_clean(item.get("pay")))
        if url in seen or _dedup_key(job) in seen:
            skipped += 1
            continue
        seen.update((url, _dedup_key(job)))
        out.append(job)
    note = (f"{skipped} item(s) skipped: missing title, company or http(s) url, "
            "or already listed") if skipped else None
    return out, note


def cmd_sources(_args):
    return {"sources": list(BOARDS.keys())}


def cmd_list(args):
    requested = (
        [s.strip() for s in args.source.split(",") if s.strip()]
        if args.source else list(BOARDS.keys())
    )
    unknown = [s for s in requested if s not in BOARDS]
    if unknown:
        return {"error": f"unknown source(s): {unknown}. valid: {list(BOARDS)}"}

    terms = [t for t in (args.q or "").lower().split() if t]
    per_board = max(args.limit, 25)  # over-fetch, trim after merge
    jobs, errors = [], []
    with ThreadPoolExecutor(max_workers=min(len(requested), 8)) as ex:
        futures = {name: ex.submit(BOARDS[name], args.q, terms, per_board)
                   for name in requested}
        # Collect in board order so dedup keeps the same winner as before.
        for name in requested:
            try:
                jobs.extend(futures[name].result())
            except Exception as exc:  # one odd response must not sink the run
                errors.append(f"{name}: {type(exc).__name__}: {str(exc)[:120]}")
                print(f"[skip] {name}: {exc}", file=sys.stderr)

    # Location filter: a comma-separated list; a job passes if it matches ANY
    # entry. Each entry is one of:
    #   'remote'                 -> any remote-flagged job, wherever restricted
    #   'anywhere'/'worldwide'/  -> remote AND not geo-restricted (drops
    #     'global'                  "USA only", "Europe", "Brazil", "London")
    #   anything else            -> that text inside the location field
    wanted = [w.strip() for w in
              (getattr(args, "location", None) or "").lower().split(",")
              if w.strip()]
    if wanted:
        open_words = ("anywhere", "worldwide", "global", "international",
                      "everywhere")

        def _unrestricted(j):
            where = (j["location"] or "").lower()
            return j["is_remote"] and (
                not where or where == "remote"
                or any(w in where for w in open_words))

        def _wanted(j):
            where = (j["location"] or "").lower()
            for w in wanted:
                if w == "remote":
                    if j["is_remote"]:
                        return True
                elif w in ("anywhere", "worldwide", "global"):
                    if _unrestricted(j):
                        return True
                elif _loc_match(w, where):
                    return True
            return False

        jobs = [j for j in jobs if _wanted(j)]

    # Recency filter. A listing with no readable posting date cannot be shown
    # to be recent, so it is dropped (and counted).
    days = getattr(args, "days", None)
    undated = 0
    if days:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        undated = sum(1 for j in jobs if not j["posted_at"])
        jobs = [j for j in jobs if j["posted_at"] and j["posted_at"] >= cutoff]

    # Dedup by (normalized title, company) — also collapses per-city reposts
    # like 'Staff Product Engineer (São Paulo)' / '(Campinas)'. First
    # occurrence (board order) wins.
    seen, deduped = set(), []
    for j in jobs:
        key = _dedup_key(j)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(j)

    # With a search: jobs whose TITLE hits the query terms rank first (a job
    # matched only via tags — e.g. a full-stack role tagged "frontend" — sinks
    # below true title matches), newest-first within each band. Without a
    # search: plain newest-first.
    deduped.sort(key=lambda j: (_title_hits(j, terms), j["posted_at"] or ""),
                 reverse=True)

    # One employer must not flood the list; best-ranked listings survive.
    if args.per_company > 0:
        by_company, capped = {}, []
        for j in deduped:
            c = (j["company"] or "").lower().strip()
            if c and by_company.get(c, 0) >= args.per_company:
                continue
            if c:
                by_company[c] = by_company.get(c, 0) + 1
            capped.append(j)
        deduped = capped

    deduped = deduped[:args.limit]

    by_source = {}
    for j in deduped:
        by_source[j["source"]] = by_source.get(j["source"], 0) + 1
    result = {
        "query": {"search": args.q, "location": (args.location or None),
                  "days": days, "sources": requested},
        "count": len(deduped),
        "by_source": by_source,
        "errors": errors,
    }
    if days:
        result["undated_dropped"] = undated
    result["jobs"] = deduped
    return result


_COMMANDS = {"sources": cmd_sources, "list": cmd_list}


def main(argv=None):
    p = argparse.ArgumentParser(description="Multi-board job listings (read-only).")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("sources", help="list the boards this skill queries")

    lp = sub.add_parser("list", help="query all (or selected) boards and merge")
    lp.add_argument("-q", "--search", dest="q",
                    help="free-text across title/company/category/tags")
    lp.add_argument("--location",
                    help="comma-separated places, a job matches if it matches "
                         "any (e.g. 'germany,netherlands', 'new york'); text "
                         "is matched inside the job's location; 'remote' "
                         "matches any remote-flagged job; 'anywhere'/"
                         "'worldwide' matches only remote jobs with no "
                         "geographic restriction")
    lp.add_argument("--source",
                    help=f"comma list to restrict boards (default all): {','.join(BOARDS)}")
    lp.add_argument("--limit", type=int, default=50, help="merged result cap (default 50)")
    lp.add_argument("--per-company", type=int, default=3, dest="per_company",
                    help="max listings per company (default 3; 0 = unlimited)")
    lp.add_argument("--days", type=int,
                    help="only listings posted in the last N days "
                         "(listings with no posting date are dropped)")
    lp.add_argument("--xlsx", metavar="PATH",
                    help="also write the returned listings to this .xlsx file")
    lp.add_argument("--extra", metavar="FILE",
                    help="JSON list of postings found by web search "
                         "(title, company, url; optional location, pay, posted) "
                         "to add at the top of the --xlsx spreadsheet")

    args = p.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    try:
        result = _COMMANDS[args.command](args)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        result = {"error": f"network error: {exc}"}
    except (json.JSONDecodeError, ET.ParseError, ValueError) as exc:
        result = {"error": f"bad response: {exc}"}

    xlsx = getattr(args, "xlsx", None)
    if xlsx and "error" not in result:
        rows = list(result.get("jobs") or [])
        if getattr(args, "extra", None):
            extra, note = _load_extra(args.extra, rows)
            result["extra_added"] = len(extra)
            if note:
                result["extra_note"] = note
            rows = extra + rows
        if rows:
            try:
                write_xlsx(xlsx, rows)
                result["xlsx"] = os.path.abspath(xlsx)
            except Exception as exc:  # the listings are still worth returning
                result["xlsx_error"] = f"{type(exc).__name__}: {exc}"
        else:
            result["xlsx_error"] = "no listings, so no spreadsheet was written"

    print(_render(result))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
