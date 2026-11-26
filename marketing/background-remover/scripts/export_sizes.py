#!/usr/bin/env python3
"""Export a cut-out PNG at exact sizes and formats, never stretching or cropping the subject.

Usage: python3 export_sizes.py job.json
{"image": "cutout.png",
 "outputs": [{"path": "mug-transparent.png"},                                    # same canvas, transparent
             {"path": "mug-2000-white.jpg", "width": 2000, "height": 2000, "fill": "#FFFFFF", "subject_fill": 0.85},
             {"path": "mug-story.png", "width": 1080, "height": 1920, "fill": "transparent"}]}
width/height: the canvas. Omit both to keep the cut-out's own size.
subject_fill: share of the canvas (0.1 to 1.0) the subject may fill, default 0.85. The subject is trimmed to its
visible edge first, then scaled to fit inside that share on both sides and centred.
fill: "transparent" (PNG or WebP only) or a hex colour. JPG always needs a colour; default white.
Prints each file's real pixel size, mode, and the subject box inside the canvas.
"""
import json, sys
import numpy as np
from PIL import Image

def main(job):
    src = Image.open(job["image"]).convert("RGBA")
    al = np.array(src.split()[3])
    ys, xs = np.where(al > 8)
    if len(xs) == 0:
        print(json.dumps({"ok": False, "error": "The cut-out has no visible pixels."})); return
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    subject = src.crop(box)
    sw, sh = subject.size
    out = []
    for o in job["outputs"]:
        p = o["path"]
        jpg = p.lower().endswith((".jpg", ".jpeg"))
        if "width" not in o and "height" not in o:
            canvas_size = src.size
            frame = None
        else:
            canvas_size = (int(o["width"]), int(o["height"]))
        cw, ch = canvas_size
        fill = o.get("fill", "#FFFFFF" if jpg else "transparent")
        sf = float(o.get("subject_fill", 0.85))
        scale_used = 1.0
        if "width" not in o and "height" not in o:
            # keep the original canvas and the subject's place on it
            layer = src
            pos_box = box
        else:
            s = min(cw * sf / sw, ch * sf / sh)
            scale_used = s
            nw, nh = max(1, round(sw * s)), max(1, round(sh * s))
            layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            x, y = (cw - nw) // 2, (ch - nh) // 2
            layer.paste(subject.resize((nw, nh), Image.LANCZOS), (x, y))
            pos_box = (x, y, x + nw, y + nh)
        if fill == "transparent" and not jpg:
            res_im = layer
        else:
            colour = tuple(int(fill.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) if fill != "transparent" else (255, 255, 255)
            bg = Image.new("RGBA", layer.size, colour + (255,))
            res_im = Image.alpha_composite(bg, layer).convert("RGB")
        if jpg:
            res_im.convert("RGB").save(p, "JPEG", quality=95, subsampling=0)
        elif p.lower().endswith(".webp"):
            res_im.save(p, "WEBP", quality=95)
        else:
            res_im.save(p, "PNG")
        chk = Image.open(p)
        out.append({"path": p, "size": list(chk.size), "mode": chk.mode, "has_alpha": chk.mode in ("RGBA", "LA"),
                    "background": "transparent" if (chk.mode == "RGBA" and fill == "transparent") else (fill if fill != "transparent" else "#FFFFFF"),
                    "subject_box": list(pos_box), "subject_inside_canvas": bool(pos_box[0] >= 0 and pos_box[1] >= 0 and pos_box[2] <= chk.size[0] and pos_box[3] <= chk.size[1]),
                    "subject_fills": [round((pos_box[2] - pos_box[0]) / chk.size[0], 2), round((pos_box[3] - pos_box[1]) / chk.size[1], 2)],
                    "scale_vs_cutout": round(scale_used, 2), "enlarged": scale_used > 1.0, "stretched": False})
    print(json.dumps({"ok": True, "outputs": out}, indent=1))

if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
