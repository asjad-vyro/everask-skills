#!/usr/bin/env python3
"""Read an installer's supplier price list (.csv or .xlsx) into clean JSON.

Usage:
    python3 price_list.py prices.xlsx [--sheet "Sheet name"] > price_list.json
    python3 price_list.py prices.csv > price_list.json

Headers are matched loosely (case and punctuation ignored):
    category   : category, type, group, kind
    description: description, item, product, name, model
    sku        : sku, code, part, part number, item code
    unit_cost  : unit cost, cost, price, buy price, trade price, net price
    unit       : unit, per, uom, pricing unit
    watts      : watts, w, wattage, wp, power w
    kw         : kw, kva, ac kw, rating kw, inverter kw
    kwh        : kwh, capacity, usable kwh, capacity kwh

Prints {"items": [...], "skipped": [...], "warnings": [...]}. Each item:
    {"row", "sku", "category", "description", "unit", "unit_cost", "watts", "kw", "kwh"}
category is one of panel, inverter, battery, mounting, electrical, labour, other.
unit is one of each, per_panel, per_kw, per_job, per_hour (default each).
Rows with no readable cost are listed in "skipped" with the reason, never guessed.

Stdlib only. Reads the file; writes nothing.
"""

import csv
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RELNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

HEADERS = {
    "category": ["category", "type", "group", "kind", "component"],
    "description": ["description", "item", "product", "name", "model", "itemdescription", "productname"],
    "sku": ["sku", "code", "part", "partnumber", "partno", "itemcode", "ref", "reference"],
    "unit_cost": ["unitcost", "cost", "price", "buyprice", "tradeprice", "netprice", "costprice",
                  "unitprice", "costexvat", "priceexvat", "costextax"],
    "unit": ["unit", "per", "uom", "pricingunit", "units"],
    "watts": ["watts", "w", "wattage", "wp", "powerw", "panelw", "panelwatts"],
    "kw": ["kw", "kva", "ackw", "ratingkw", "inverterkw", "ratedkw", "outputkw"],
    "kwh": ["kwh", "capacity", "usablekwh", "capacitykwh", "storagekwh", "batterykwh"],
}

CATEGORY_WORDS = [
    ("battery", r"batter|storage|powerwall"),
    ("inverter", r"inverter|microinverter|optimi[sz]er"),
    ("mounting", r"mount|rail|bracket|roof ?hook|clamp|racking|frame|flashing"),
    ("labour", r"labou?r|install(ation)? (time|hours)|fitter|electrician time"),
    ("electrical", r"cabl|wire|isolator|breaker|mcb|rcbo|meter|connector|mc4|conduit|electrical|"
                   r"consumer unit|fuse|surge|spd|scaffold|commission"),
    ("panel", r"panel|module|\bpv\b|solar"),
]
UNIT_WORDS = [
    ("per_panel", r"panel|module"),
    ("per_kw", r"kw"),
    ("per_hour", r"hour|hr\b|/h\b"),
    ("per_job", r"job|install|system|lot|fixed"),
]


def _key(text):
    return re.sub(r"[^a-z]", "", str(text or "").lower())


def _number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    text = re.sub(r"^[^\d\-.]+", "", text)  # drop currency symbols such as £ $ € R
    match = re.match(r"-?\d+(\.\d+)?", text)
    return float(match.group(0)) if match else None


def _category(raw, description):
    text = f"{raw or ''} {description or ''}".lower()
    for name, pattern in CATEGORY_WORDS:
        if re.search(pattern, str(raw or "").lower()):
            return name
    for name, pattern in CATEGORY_WORDS:
        if re.search(pattern, text):
            return name
    return "other"


def _unit(raw, category):
    text = str(raw or "").lower()
    for name, pattern in UNIT_WORDS:
        if text and re.search(pattern, text):
            return name
    if category == "labour":
        return "per_hour"
    return "each"


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return [row for row in csv.reader(fh, dialect)]


def read_xlsx(path, sheet_name=None):
    with zipfile.ZipFile(path) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        sheets = [(s.get("name"), targets[s.get(RELNS)]) for s in wb.find("m:sheets", NS)]
        if sheet_name:
            matches = [s for s in sheets if s[0].lower() == sheet_name.lower()]
            if not matches:
                raise ValueError(f"No sheet named '{sheet_name}'. Sheets: {[s[0] for s in sheets]}")
            target = matches[0][1]
        else:
            target = sheets[0][1]
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        root = ET.fromstring(zf.read(target))
    rows = []
    for row in root.iter(f"{{{NS['m']}}}row"):
        cells = {}
        for c in row.findall("m:c", NS):
            ref = c.get("r", "")
            col = 0
            for ch in re.match(r"[A-Z]+", ref).group(0) if ref else "":
                col = col * 26 + (ord(ch) - 64)
            kind = c.get("t")
            v = c.find("m:v", NS)
            if kind == "s" and v is not None:
                value = shared[int(v.text)]
            elif kind == "inlineStr":
                value = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
            elif v is not None:
                value = v.text
            else:
                value = ""
            cells[col or len(cells) + 1] = value
        if cells:
            rows.append([cells.get(i, "") for i in range(1, max(cells) + 1)])
    return rows


def parse(rows):
    warnings, skipped, items = [], [], []
    header_idx, mapping = None, {}
    for idx, row in enumerate(rows[:15]):
        keys = [_key(c) for c in row]
        found = {}
        for field, aliases in HEADERS.items():
            for col, k in enumerate(keys):
                if k in aliases and field not in found:
                    found[field] = col
        if "unit_cost" in found and ("description" in found or "sku" in found):
            header_idx, mapping = idx, found
            break
    if header_idx is None:
        raise ValueError("Could not find a header row with a cost/price column and an item or "
                         "description column in the first 15 rows.")
    for field in ("category", "unit", "watts", "kw", "kwh"):
        if field not in mapping:
            warnings.append(f"No '{field}' column; inferred where possible.")

    def get(row, field):
        col = mapping.get(field)
        return row[col] if col is not None and col < len(row) else ""

    for offset, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
        if not any(str(c).strip() for c in row):
            continue
        description = str(get(row, "description")).strip()
        sku = str(get(row, "sku")).strip()
        cost = _number(get(row, "unit_cost"))
        if cost is None:
            skipped.append({"row": offset, "item": description or sku, "reason": "no readable cost"})
            continue
        category = _category(get(row, "category"), description)
        watts = _number(get(row, "watts"))
        kw = _number(get(row, "kw"))
        kwh = _number(get(row, "kwh"))
        text = f"{description} {sku}"
        if category == "panel" and watts is None:
            m = re.search(r"(\d{3})\s*(w|wp)\b", text, re.I)
            watts = float(m.group(1)) if m else None
        if category == "inverter" and kw is None:
            m = re.search(r"(\d+(?:\.\d+)?)\s*kw\b", text, re.I)
            kw = float(m.group(1)) if m else None
        if category == "battery" and kwh is None:
            m = re.search(r"(\d+(?:\.\d+)?)\s*kwh\b", text, re.I)
            kwh = float(m.group(1)) if m else None
        item = {"row": offset, "sku": sku or description, "category": category,
                "description": description or sku, "unit": _unit(get(row, "unit"), category),
                "unit_cost": round(cost, 4), "watts": watts, "kw": kw, "kwh": kwh}
        if category == "panel" and not watts:
            warnings.append(f"Row {offset}: panel '{item['description']}' has no wattage.")
        if category == "inverter" and not kw:
            warnings.append(f"Row {offset}: inverter '{item['description']}' has no kW rating.")
        if category == "battery" and not kwh:
            warnings.append(f"Row {offset}: battery '{item['description']}' has no kWh capacity.")
        items.append(item)
    if not items:
        raise ValueError("No priced rows found under the header row.")
    return {"items": items, "skipped": skipped, "warnings": warnings}


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__, file=sys.stderr)
        return 2
    path = argv[0]
    sheet = argv[argv.index("--sheet") + 1] if "--sheet" in argv else None
    try:
        if path.lower().endswith((".xlsx", ".xlsm")):
            rows = read_xlsx(path, sheet)
        elif path.lower().endswith((".csv", ".tsv", ".txt")):
            rows = read_csv(path)
        else:
            raise ValueError("Use a .csv or .xlsx file (export .xls or Google Sheets to .xlsx or .csv).")
        result = parse(rows)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
