#!/usr/bin/env python3
"""Cut a subject out of its background and write a transparent PNG (Pillow + numpy only).

Usage: python3 cutout.py job.json
Inspect first (nothing is written):
  {"image": "photo.png", "inspect": true}
  -> border colour, whether the edge of the picture is one flat colour, and what to do next.
Cut out:
  {"image": "photo.png", "output": "cutout.png", "mode": "border"}      # background already one flat colour (studio white, grey...)
  {"image": "edited.png", "output": "cutout.png", "mode": "key", "key": "#00FF00"}   # picture from the edit model, solid key colour
Optional: "erode": 1 (px to pull the edge in, removes halos), "soft": 0.8 (edge blur), "reference": "original.png"
(compare the subject with the original to catch drift when the edit model made the picture).
Prints JSON with checks: alpha present, share of transparent pixels, subject box, corners, warnings.
"""
import json, sys
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

def hex_to_rgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)

def rgb_hex(c):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)

def ring_pixels(arr, frac=0.03):
    H, W = arr.shape[:2]
    r = max(2, int(min(H, W) * frac))
    return np.concatenate([arr[:r].reshape(-1, 3), arr[-r:].reshape(-1, 3),
                           arr[:, :r].reshape(-1, 3), arr[:, -r:].reshape(-1, 3)]).astype(float)

def border_info(arr):
    px = ring_pixels(arr)
    med = np.median(px, axis=0)
    d = np.sqrt(((px - med) ** 2).sum(axis=1))
    return med, float((d < 28).mean())

def share_key_like(arr):
    s = arr[::4, ::4].astype(int)
    R, G, B = s[..., 0], s[..., 1], s[..., 2]
    green = ((G > 150) & (G > R + 60) & (G > B + 60)).mean()
    magenta = ((R > 150) & (B > 150) & (G < R - 60) & (G < B - 60)).mean()
    return float(green), float(magenta)

def label(mask):
    """4-connected components of a small boolean grid. Returns (labels, areas, touches_border)."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    areas, border = [0], [False]
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] == 0:
                n += 1
                lab[y, x] = n
                q = deque([(y, x)]); a = 0; tb = False
                while q:
                    cy, cx = q.popleft(); a += 1
                    if cy in (0, h - 1) or cx in (0, w - 1):
                        tb = True
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = n; q.append((ny, nx))
                areas.append(a); border.append(tb)
    return lab, areas, border

def up(mask_small, W, H, grow=1):
    im = Image.fromarray((mask_small * 255).astype("uint8"), "L")
    if grow:
        im = im.filter(ImageFilter.MaxFilter(2 * grow + 1))
    return np.array(im.resize((W, H), Image.NEAREST)) > 127

def main(job):
    im = Image.open(job["image"])
    src_mode = im.mode
    im = im.convert("RGB")
    W, H = im.size
    arr = np.array(im).astype(float)
    med, match = border_info(arr)
    g, m = share_key_like(arr)
    if job.get("inspect"):
        rec = "border" if match >= 0.9 else ("edit-magenta" if g > 0.05 else "edit-green")
        print(json.dumps({"size": [W, H], "border_color": rgb_hex(med), "border_flat": match >= 0.9,
                          "border_match_share": round(match, 3), "green_share": round(g, 3), "magenta_share": round(m, 3),
                          "recommended_route": rec,
                          "note": {"border": "background is one flat colour: run mode border, no edit call needed",
                                   "edit-green": "background is not flat: ask the edit model for a solid #00FF00 background, then run mode key",
                                   "edit-magenta": "subject has green in it: ask the edit model for a solid #FF00FF background, then run mode key with key #FF00FF"}[rec]}, indent=1))
        return
    mode = job.get("mode", "border")
    warnings = []
    if mode == "key":
        key = hex_to_rgb(job.get("key", "#00FF00"))
        if match < 0.8:
            print(json.dumps({"ok": False, "error": "The edge of this picture is not one flat colour (%.0f%% of edge pixels match), so the edit model did not return a solid background. Retry the edit once, or tell the user the cut-out failed." % (match * 100),
                              "border_color": rgb_hex(med)}, indent=1)); return
        bg = med
        dist_to_key = float(np.sqrt(((bg - key) ** 2).sum()))
        if dist_to_key > 120:
            warnings.append("The returned background colour %s is far from the requested %s." % (rgb_hex(bg), rgb_hex(key)))
        t0, t1 = 45.0, 130.0
    else:
        if match < 0.8:
            print(json.dumps({"ok": False, "error": "The background is not one flat colour (%.0f%% of edge pixels match). Use the edit-model route (solid key colour) instead." % (match * 100),
                              "border_color": rgb_hex(med)}, indent=1)); return
        bg = med
        t0, t1 = 20.0, 62.0
    d = np.sqrt(((arr - bg) ** 2).sum(axis=2))
    if mode == "border" and job.get("shadow") == "remove":
        # a soft shadow is the background colour made darker: distance to the line k*bg ignores it
        u = bg / max(np.linalg.norm(bg), 1.0)
        proj = (arr * u).sum(axis=2, keepdims=True) * u
        d = np.sqrt(((arr - proj) ** 2).sum(axis=2))
        warnings.append("shadow removal is on: dark or grey parts of the subject may be cut away too; check the result.")
    a = np.clip((d - t0) / (t1 - t0), 0, 1)
    # work on a small copy to find which background-like areas are really background
    scale = 300.0 / max(W, H)
    sw, sh = max(8, int(W * scale)), max(8, int(H * scale))
    small = np.array(Image.fromarray((a * 255).astype("uint8"), "L").resize((sw, sh), Image.BOX)) / 255.0
    subj = small >= 0.5
    if mode == "border":
        bgcell = ~subj
        lab, areas, border = label(bgcell)
        keep_bg = np.zeros_like(bgcell)
        for i in range(1, len(areas)):
            if border[i] or areas[i] >= 0.002 * sw * sh:   # edge-connected, or an enclosed hole (mug handle) big enough
                keep_bg |= lab == i
        allowed = up(keep_bg, W, H, grow=1)
        a = np.where(allowed, a, 1.0)
    # drop specks: subject pieces much smaller than the biggest one
    lab, areas, _ = label(np.array(Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8"), "L").resize((sw, sh), Image.BOX)) >= 128)
    if len(areas) > 1:
        big = max(areas[1:])
        keepm = np.zeros((sh, sw), dtype=bool)
        for i in range(1, len(areas)):
            if areas[i] >= 0.01 * big:
                keepm |= lab == i
        a = a * up(keepm, W, H, grow=2)
    # remove background colour mixed into edge pixels
    af = np.maximum(a, 0.04)[..., None]
    rgb = np.where((a > 0)[..., None] & (a < 1)[..., None], (arr - (1 - af) * bg) / af, arr)
    if mode == "key":
        if key[1] > key[0] and key[1] > key[2]:      # green key: pull green spill back
            spill = np.clip(rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2]), 0, None)
            rgb[..., 1] -= spill
        elif key[0] > 128 and key[2] > 128 and key[1] < 128:   # magenta key: pull red and blue spill back
            spill = np.clip(np.minimum(rgb[..., 0], rgb[..., 2]) - rgb[..., 1], 0, None)
            rgb[..., 0] -= spill; rgb[..., 2] -= spill
    rgb = np.clip(rgb, 0, 255)
    alpha_im = Image.fromarray((a * 255).astype("uint8"), "L")
    er = int(job.get("erode", 1))
    if er > 0:
        alpha_im = alpha_im.filter(ImageFilter.MinFilter(2 * er + 1))
    soft = float(job.get("soft", 0.8))
    if soft > 0:
        alpha_im = alpha_im.filter(ImageFilter.GaussianBlur(soft))
    out = Image.fromarray(rgb.astype("uint8"), "RGB").convert("RGBA")
    out.putalpha(alpha_im)
    out.save(job["output"], "PNG")
    al = np.array(alpha_im) / 255.0
    ys, xs = np.where(al > 0.5)
    res = {"ok": True, "output": job["output"], "mode": mode, "size": [W, H], "background_color": rgb_hex(bg),
           "has_alpha_channel": Image.open(job["output"]).mode == "RGBA",
           "transparent_share": round(float((al < 0.04).mean()), 3)}
    if len(xs):
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        res["subject_box"] = bbox
        res["subject_touches_edge"] = bool(bbox[0] <= 0 or bbox[1] <= 0 or bbox[2] >= W or bbox[3] >= H)
        res["subject_share"] = round(float((al > 0.5).mean()), 3)
    k = 6
    res["corners_transparent"] = bool(max(al[:k, :k].max(), al[:k, -k:].max(), al[-k:, :k].max(), al[-k:, -k:].max()) < 0.04)
    ts = res["transparent_share"]
    if ts < 0.05 or ts > 0.95:
        warnings.append("Transparent share is %.0f%%, which is not plausible for a cut-out: the subject may be missing or the background may not have been removed." % (ts * 100))
    if res.get("subject_touches_edge"):
        warnings.append("The subject touches the edge of the picture, so it may have been cut off in the original.")
    semi = float(((al > 0.04) & (al < 0.96)).mean())
    res["soft_edge_share"] = round(semi, 3)
    if semi > 0.08:
        warnings.append("A lot of the picture is semi-transparent (%.0f%%): shadows, glass or fine detail. Say so." % (semi * 100))
    if job.get("reference"):
        ref = Image.open(job["reference"]).convert("RGB")
        res["reference_size"] = list(ref.size)
        if abs(ref.size[0] / ref.size[1] - W / H) > 0.02:
            res["aspect_match"] = False
            warnings.append("The edited picture has a different shape (%dx%d) from the original (%dx%d), so the subject may have been moved or rescaled." % (W, H, ref.size[0], ref.size[1]))
        else:
            res["aspect_match"] = True
            r2 = np.array(im.resize(ref.size, Image.LANCZOS)).astype(float)
            ra = np.array(ref).astype(float)
            core = np.array(alpha_im.resize(ref.size, Image.BILINEAR).filter(ImageFilter.MinFilter(9))) > 250
            if core.sum() > 100:
                drift = float(np.abs(r2[core] - ra[core]).mean())
                res["subject_drift"] = round(drift, 1)
                if drift > 30:
                    warnings.append("The subject looks different from the original (mean colour difference %.0f of 255): the edit model may have changed it. Compare by eye." % drift)
    res["warnings"] = warnings
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
