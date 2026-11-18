#!/usr/bin/env python3
"""Find schools, transport, parks and shops near a property, with real distances.

Usage:
    python3 nearby.py --address "12 Park Road, Leeds LS6 2AA"
    python3 nearby.py --lat 53.81 --lon -1.57 [--radius 1500] [--per-kind 4]

Geocodes the address with OpenStreetMap Nominatim, then asks the Overpass API for
places within --radius metres (default 1500, max 5000). Distances are straight-line
(haversine) from the property; walking minutes are estimated at 80 m a minute along a
route 1.3 times the straight line, and are labelled as estimates.

Prints JSON:
    {"property": {"lat", "lon", "matched_address", "source"},
     "radius_m": 1500,
     "places": {"schools": [...], "transport": [...], "parks": [...], "shops": [...]},
     "notes": [...]}
Each place: {"name", "type", "distance_m", "distance_text", "walk_min_estimate",
             "source"}  (source = the OpenStreetMap link for that place).
On failure prints {"error": "..."} and exits 1. Read-only: no network writes.
Data © OpenStreetMap contributors (ODbL). Stdlib only.
"""

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "listing-launch-kit/1.0 (skill script)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# kind -> list of (osm key, value regex)
KINDS = {
    "schools": [("amenity", "^(school|kindergarten|college|university)$")],
    "transport": [("railway", "^(station|halt|tram_stop)$"),
                  ("public_transport", "^station$"),
                  ("highway", "^bus_stop$")],
    "parks": [("leisure", "^(park|playground|nature_reserve|garden)$")],
    "shops": [("shop", "^(supermarket|convenience|bakery|chemist|mall|greengrocer|butcher)$"),
              ("amenity", "^(pharmacy|marketplace)$")],
}


def fetch(url, data=None, timeout=40):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        # Old Python builds (LibreSSL) fail some TLS handshakes: retry with curl if present.
        if "SSL" not in str(exc) or not shutil.which("curl"):
            raise
        cmd = ["curl", "-sS", "-m", str(timeout), "-A", UA, "--fail", url]
        if data is not None:
            cmd[1:1] = ["--data-binary", "@-"]
        out = subprocess.run(cmd, input=data, capture_output=True, timeout=timeout + 5)
        if out.returncode != 0:
            raise RuntimeError(out.stderr.decode("utf-8", "replace").strip()[:200])
        return json.loads(out.stdout.decode("utf-8"))


def geocode(address):
    q = urllib.parse.urlencode({"q": address, "format": "jsonv2", "limit": 1,
                                "addressdetails": 0})
    res = fetch(NOMINATIM + "?" + q)
    if not res:
        return None
    r = res[0]
    return {"lat": float(r["lat"]), "lon": float(r["lon"]),
            "matched_address": r.get("display_name", ""),
            "source": "https://www.openstreetmap.org/%s/%s" % (r.get("osm_type"), r.get("osm_id"))}


def haversine(lat1, lon1, lat2, lon2):
    rad = math.radians
    dlat, dlon = rad(lat2 - lat1), rad(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(rad(lat1)) * math.cos(rad(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(a))


def distance_text(m):
    mi = m / 1609.344
    mi_text = "<0.1 mi" if mi < 0.1 else "%.1f mi" % mi
    if m < 1000:
        return "%d m (%s)" % (round(m / 10) * 10, mi_text)
    return "%.1f km (%.1f mi)" % (m / 1000, m / 1609.344)


def overpass(lat, lon, radius):
    parts = []
    for rules in KINDS.values():
        for key, rx in rules:
            if key == "highway":  # bus stops: nodes only, closer in, keeps the query fast
                parts.append('node(around:%d,%f,%f)["highway"="bus_stop"];'
                             % (min(radius, 800), lat, lon))
            else:
                parts.append('nwr(around:%d,%f,%f)["%s"~"%s"];' % (radius, lat, lon, key, rx))
    query = "[out:json][timeout:60];(" + "".join(parts) + ");out center tags;"
    data = urllib.parse.urlencode({"data": query}).encode()
    errors = []
    for url in OVERPASS:
        try:
            return fetch(url, data=data, timeout=90)
        except Exception as exc:  # try the next mirror
            errors.append("%s: %s" % (url.split("/")[2], exc))
            time.sleep(1)
    raise RuntimeError("Overpass API unavailable (%s). Use web_search for nearby places "
                       "instead and cite each source." % "; ".join(errors))


def classify(tags):
    for kind, rules in KINDS.items():
        for key, rx in rules:
            if key in tags and re.match(rx, tags[key]):
                return kind, tags[key].replace("_", " ")
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--address")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    ap.add_argument("--radius", type=int, default=1500)
    ap.add_argument("--per-kind", type=int, default=4)
    a = ap.parse_args()
    radius = max(200, min(a.radius, 5000))
    notes = []

    if a.lat is not None and a.lon is not None:
        prop = {"lat": a.lat, "lon": a.lon, "matched_address": "", "source": "coordinates given"}
    elif a.address and a.address.strip():
        try:
            prop = geocode(a.address.strip())
        except Exception as exc:
            print(json.dumps({"error": "Geocoding failed: %s" % exc}))
            return 1
        if not prop:
            print(json.dumps({"error": "Address not found on OpenStreetMap. Check the spelling "
                                       "or pass --lat/--lon from the user's map pin."}))
            return 1
        notes.append("Check matched_address is the property; if not, rerun with --lat/--lon.")
    else:
        print(json.dumps({"error": "Give --address or both --lat and --lon."}))
        return 1

    try:
        res = overpass(prop["lat"], prop["lon"], radius)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "property": prop}))
        return 1

    found = {k: {} for k in KINDS}
    for el in res.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        kind, typ = classify(tags)
        if not kind:
            continue
        lat = el.get("lat", el.get("center", {}).get("lat"))
        lon = el.get("lon", el.get("center", {}).get("lon"))
        if lat is None or lon is None:
            continue
        d = haversine(prop["lat"], prop["lon"], lat, lon)
        key = name.lower()
        if key in found[kind] and found[kind][key]["distance_m"] <= d:
            continue  # keep the nearest entry of a repeated name (e.g. two bus stops)
        found[kind][key] = {
            "name": name, "type": typ, "distance_m": int(round(d)),
            "distance_text": distance_text(d),
            "walk_min_estimate": max(1, int(round(d * 1.3 / 80))),
            "source": "https://www.openstreetmap.org/%s/%s" % (el["type"], el["id"]),
        }

    places = {}
    for kind, items in found.items():
        ranked = sorted(items.values(), key=lambda x: x["distance_m"])
        # nearest of each type first (a station and a bus stop, not four bus stops)
        first, seen = [], set()
        for p in ranked:
            if p["type"] not in seen:
                seen.add(p["type"])
                first.append(p)
        rest = [p for p in ranked if p not in first]
        places[kind] = sorted((first + rest)[: a.per_kind], key=lambda x: x["distance_m"])
        if not places[kind]:
            notes.append("No named %s found within %d m on OpenStreetMap; use web_search "
                         "or leave it out." % (kind, radius))
    notes.append("Distances are straight-line; walking minutes are estimates. School "
                 "catchments and ratings are not included: check them with the official source.")
    print(json.dumps({"property": prop, "radius_m": radius, "places": places,
                      "attribution": "Data © OpenStreetMap contributors (ODbL)",
                      "notes": notes}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
