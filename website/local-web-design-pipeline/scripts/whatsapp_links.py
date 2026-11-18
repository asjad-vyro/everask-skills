#!/usr/bin/env python3
"""Build tap-to-send WhatsApp links (wa.me) with a pre-filled message.

Usage:
    python3 whatsapp_links.py --country 44 --file messages.json

messages.json: [{"name": "...", "phone": "0113 496 0000", "message": "Hi ..."}, ...]
--country: the calling code of the area searched (44 UK, 1 US/Canada, 92 Pakistan,
971 UAE, 61 Australia, ...). Used for numbers written in national form.

Prints a JSON list: {"name", "phone", "international", "link", "note"}.
"link" is empty when the number cannot be read; "note" says why.

The link only opens the user's own WhatsApp with the message typed in. Nothing is
sent until the user taps send. Stdlib only.
"""

import json
import re
import sys
import urllib.parse


def to_international(phone, country):
    raw = (phone or "").strip()
    if not raw:
        return "", "No phone number"
    digits = re.sub(r"\D", "", raw)
    if raw.startswith("+"):
        number = digits
    elif digits.startswith("00"):
        number = digits[2:]
    elif country == "1" and len(digits) == 10:
        number = "1" + digits
    elif digits.startswith("0"):
        number = country + digits[1:]
    elif digits.startswith(country) and len(digits) > 9:
        number = digits
    else:
        number = country + digits
    if not 8 <= len(number) <= 15:
        return "", f"Could not read '{raw}' as a full phone number"
    return number, ""


def main(argv):
    if "--file" not in argv or "--country" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    country = re.sub(r"\D", "", argv[argv.index("--country") + 1])
    with open(argv[argv.index("--file") + 1], encoding="utf-8") as fh:
        items = json.load(fh)
    out = []
    for item in items:
        number, note = to_international(item.get("phone", ""), country)
        link = ""
        if number:
            link = "https://wa.me/" + number + "?text=" + urllib.parse.quote(item.get("message", ""))
            note = "Opens WhatsApp only if this number uses WhatsApp; landlines often do not."
        out.append({"name": item.get("name", ""), "phone": item.get("phone", ""),
                    "international": "+" + number if number else "", "link": link, "note": note})
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
