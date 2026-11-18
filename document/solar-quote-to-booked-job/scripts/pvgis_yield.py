#!/usr/bin/env python3
"""Expected solar yield for a roof, from the EU's free PVGIS service (worldwide data).

Usage:
    python3 pvgis_yield.py --lat 53.80 --lon -1.55 [--facing S|SW|...|<degrees from north>]
                           [--tilt 35] [--loss 14]

--facing: the way the roof slope faces (compass letters or degrees: N=0, E=90, S=180,
          W=270). Omit it, or pass "unknown", to let PVGIS use the best angle (and say so).
--tilt:   roof pitch in degrees. Omit to let PVGIS use the best pitch.
--loss:   system losses in % (cables, inverter, dirt). Default 14, the PVGIS default.

Prints JSON:
    {"kwh_per_kwp_year", "peak_sun_hours", "monthly_kwh_per_kwp": [12 numbers],
     "tilt", "facing_degrees", "pvgis_aspect", "optimal_angles_used", "loss_pct",
     "radiation_database", "years", "source_url", "checked_on"}
kwh_per_kwp_year is the yearly output of 1 kWp on that roof, after losses.
peak_sun_hours is the daily average sunlight on the panel plane (kWh/m2/day).
On failure prints {"error": ...} and exits 1: never fill these numbers in from memory.

Stdlib only. One read-only GET to re.jrc.ec.europa.eu.
"""

import datetime
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"
COMPASS = {"N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5, "E": 90, "ESE": 112.5, "SE": 135,
           "SSE": 157.5, "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5, "W": 270,
           "WNW": 292.5, "NW": 315, "NNW": 337.5}
WORDS = {"NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W", "NORTHEAST": "NE",
         "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW"}


def facing_to_degrees(text):
    if text is None:
        return None
    raw = str(text).strip().upper().replace("-", "").replace(" ", "")
    if raw in ("", "UNKNOWN", "NONE", "?", "FLAT"):
        return None
    raw = WORDS.get(raw, raw)
    if raw in COMPASS:
        return COMPASS[raw]
    try:
        deg = float(raw.rstrip("°"))
    except ValueError:
        raise ValueError(f"Cannot read roof direction '{text}'. Use N, NE, E, SE, S, SW, W, NW "
                         "or degrees from north.")
    return deg % 360


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv):
    if "--lat" not in argv or "--lon" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        lat, lon = float(arg(argv, "--lat")), float(arg(argv, "--lon"))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Latitude must be -90..90 and longitude -180..180.")
        facing = facing_to_degrees(arg(argv, "--facing"))
        tilt = arg(argv, "--tilt")
        tilt = None if tilt in (None, "", "unknown") else float(tilt)
        loss = float(arg(argv, "--loss", 14))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    params = {"lat": lat, "lon": lon, "peakpower": 1, "loss": loss,
              "mountingplace": "building", "outputformat": "json"}
    # PVGIS aspect: 0 = facing south, 90 = west, -90 = east, 180 = north.
    aspect = None if facing is None else round((facing % 360) - 180, 1)
    optimal = facing is None or tilt is None
    if facing is None and tilt is None:
        params["optimalangles"] = 1
    elif facing is None:
        # Direction unknown, pitch known: assume the roof faces the equator (best case).
        params.update(angle=tilt, aspect=0 if lat >= 0 else 180)
    elif tilt is None:
        params.update(aspect=aspect, optimalinclination=1)
    else:
        params.update(angle=tilt, aspect=aspect)

    url = API + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "solar-quote-skill/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:200]
        print(json.dumps({"error": f"PVGIS returned HTTP {exc.code}: {detail}", "source_url": url}))
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": f"PVGIS could not be reached ({exc})", "source_url": url}))
        return 1

    try:
        totals = data["outputs"]["totals"]["fixed"]
        monthly = [m["E_m"] for m in data["outputs"]["monthly"]["fixed"]]
        mount = data["inputs"]["mounting_system"]["fixed"]
        meteo = data["inputs"]["meteo_data"]
    except (KeyError, TypeError):
        print(json.dumps({"error": "Unexpected PVGIS reply", "source_url": url}))
        return 1
    used_aspect = mount["azimuth"]["value"]
    out = {
        "kwh_per_kwp_year": round(totals["E_y"], 1),
        "peak_sun_hours": round(totals["H(i)_y"] / 365, 2),
        "monthly_kwh_per_kwp": [round(x, 1) for x in monthly],
        "tilt": mount["slope"]["value"],
        "facing_degrees": round((used_aspect + 180) % 360, 1),
        "pvgis_aspect": used_aspect,
        "optimal_angles_used": optimal,
        "loss_pct": loss,
        "radiation_database": meteo.get("radiation_db"),
        "years": f"{meteo.get('year_min')}-{meteo.get('year_max')}",
        "source_url": url,
        "checked_on": datetime.date.today().isoformat(),
    }
    if optimal:
        out["note"] = ("Roof pitch or direction not given: PVGIS used the best angle, so this is "
                       "an upper estimate. Confirm the real roof at the site visit.")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
