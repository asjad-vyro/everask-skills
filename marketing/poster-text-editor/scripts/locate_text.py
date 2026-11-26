#!/usr/bin/env python3
"""Find where given phrases sit on an image, using tesseract (OCR), and print their boxes.

Usage: python3 locate_text.py job.json
job.json: {"image": "in.png", "phrases": ["12 March 2027", "15"], "lang": "eng"}   (lang optional, e.g. "eng+kor")
Prints JSON: for each phrase, the pixel box [x0,y0,x1,y1] and fractions of the image size, plus every
OCR line found. If tesseract is missing or does not find a phrase, use media_analyze to estimate the box.
"""
import json, re, shutil, subprocess, sys
from PIL import Image

def norm(s):
    return re.sub(r"\s+", "", s).lower()

def main(job):
    W, H = Image.open(job["image"]).size
    if not shutil.which("tesseract"):
        print(json.dumps({"error": "tesseract not found; estimate the box with media_analyze instead", "size": [W, H]}))
        return
    lang = job.get("lang", "eng")
    r = subprocess.run(["tesseract", job["image"], "stdout", "-l", lang, "--psm", "11", "tsv"],
                       capture_output=True, text=True)
    if r.returncode != 0 and lang != "eng":
        r = subprocess.run(["tesseract", job["image"], "stdout", "-l", "eng", "--psm", "11", "tsv"], capture_output=True, text=True)
    words = []
    for ln in r.stdout.splitlines()[1:]:
        p = ln.split("\t")
        if len(p) < 12 or not p[11].strip():
            continue
        try:
            conf = float(p[10])
        except ValueError:
            continue
        if conf < 0:
            continue
        x, y, w, h = map(int, p[6:10])
        words.append({"text": p[11], "box": [x, y, x + w, y + h], "conf": conf})
    # group into lines by vertical overlap
    words.sort(key=lambda a: (a["box"][1], a["box"][0]))
    lines = []
    for w in words:
        cy = (w["box"][1] + w["box"][3]) / 2
        for L in lines:
            if L["y0"] <= cy <= L["y1"]:
                L["words"].append(w); L["y0"] = min(L["y0"], w["box"][1]); L["y1"] = max(L["y1"], w["box"][3]); break
        else:
            lines.append({"y0": w["box"][1], "y1": w["box"][3], "words": [w]})
    out_lines = []
    for L in lines:
        L["words"].sort(key=lambda a: a["box"][0])
        out_lines.append(L)
    found = {}
    for ph in job.get("phrases", []):
        target = norm(ph)
        best = None
        for L in out_lines:
            ws = L["words"]
            for i in range(len(ws)):
                acc = ""
                for j in range(i, len(ws)):
                    acc += norm(ws[j]["text"])
                    if acc == target:
                        bx = [min(w["box"][0] for w in ws[i:j + 1]), min(w["box"][1] for w in ws[i:j + 1]),
                              max(w["box"][2] for w in ws[i:j + 1]), max(w["box"][3] for w in ws[i:j + 1])]
                        best = best or []
                        best.append(bx)
                    if len(acc) >= len(target):
                        break
        if best:
            found[ph] = [{"box": b, "box_frac": [round(b[0] / W, 4), round(b[1] / H, 4), round(b[2] / W, 4), round(b[3] / H, 4)]} for b in best]
        else:
            found[ph] = []
    print(json.dumps({"size": [W, H], "found": found,
                      "lines": [{"text": " ".join(w["text"] for w in L["words"]),
                                 "box": [min(w["box"][0] for w in L["words"]), min(w["box"][1] for w in L["words"]),
                                         max(w["box"][2] for w in L["words"]), max(w["box"][3] for w in L["words"])]} for L in out_lines]},
                     ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
