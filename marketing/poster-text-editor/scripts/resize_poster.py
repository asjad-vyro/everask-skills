#!/usr/bin/env python3
"""Fit a poster onto other canvas sizes without stretching or cropping it.

Usage: python3 resize_poster.py job.json
{"image": "in.png", "outputs": [{"path": "story.png", "width": 1080, "height": 1920},
                                {"path": "square.jpg", "width": 1080, "height": 1080, "fill": "#FFFFFF"}]}
"fill" is optional: a hex colour, or "auto" (default) = the poster's edge colour when the edge is plain,
otherwise a blurred, enlarged copy of the poster. The poster is scaled to fit inside the canvas and centred.
Prints JSON with each file's pixel size and the scale used.
"""
import json, sys
import numpy as np
from PIL import Image, ImageFilter

def main(job):
    im = Image.open(job["image"]).convert("RGB")
    W, H = im.size
    arr = np.array(im)
    edge = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]]).astype(float)
    flat = edge.std(axis=0).max() < 12
    med = tuple(int(v) for v in np.median(edge, axis=0))
    res = []
    for o in job["outputs"]:
        cw, ch = int(o["width"]), int(o["height"])
        s = min(cw / W, ch / H)
        nw, nh = max(1, round(W * s)), max(1, round(H * s))
        fill = o.get("fill", "auto")
        if fill == "auto" and not flat:
            k = max(cw / W, ch / H)
            bgim = im.resize((max(cw, round(W * k)), max(ch, round(H * k))), Image.LANCZOS)
            l, t = (bgim.width - cw) // 2, (bgim.height - ch) // 2
            canvas = bgim.crop((l, t, l + cw, t + ch)).filter(ImageFilter.GaussianBlur(max(cw, ch) / 40))
            how = "blurred copy of the poster"
        else:
            c = med if fill == "auto" else tuple(int(fill.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
            canvas = Image.new("RGB", (cw, ch), c)
            how = "plain colour #%02X%02X%02X" % c
        canvas.paste(im.resize((nw, nh), Image.LANCZOS), ((cw - nw) // 2, (ch - nh) // 2))
        p = o["path"]
        if p.lower().endswith((".jpg", ".jpeg")):
            canvas.save(p, "JPEG", quality=95)
        else:
            canvas.save(p)
        res.append({"path": p, "size": list(Image.open(p).size), "poster_scaled_to": [nw, nh], "scale": round(s, 4), "padding": how,
                    "stretched": False})
    print(json.dumps({"outputs": res}, indent=1))

if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
