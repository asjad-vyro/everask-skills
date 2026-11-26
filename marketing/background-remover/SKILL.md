---
name: Background Remover and Resizer
description: >
  Cuts the background out of a photo and returns a transparent PNG, or the
  subject on white or any colour, in the exact sizes marketplaces, social
  profiles and print need. Use it for "remove the background", "make this
  photo transparent", "put the product on white", "2000x2000 for my shop",
  "cut out my logo" or "profile picture on a blue background".
---

# Background Remover and Resizer

The user gives a photo and wants the subject on a transparent or flat-colour background, at exact sizes. A good result is a clean cut-out with no halo, nothing missing from the subject, nothing about the subject changed, and every file at the pixel size asked, with the subject scaled to fit and never stretched.

Do the whole job in one reply. Never open with questions: decide, say what you assumed, deliver. Write no text before your first tool call or between tool calls: no "I'll load the skill", no "Let me". The first words the user sees are the result.

## Hard rules

- Write the reply in the language the user wrote in, unless they ask for another. Keep their file names, sizes and colours exactly as given.
- Never invent a size, a colour or a platform rule. Use the sizes and colours the user gave. If they name a platform but no size, use the preset list in Step 4 and say "common size, check the platform's current requirement".
- Never claim a cut-out is clean without looking at it (Step 5). Name any rough edge, missing part or changed detail plainly.
- Do not change the subject. If the edit model altered a label, a logo, text on the product, a face or colours, say so and offer one retry.
- Do not remove watermarks or logos of someone else from an image the user does not own. If the picture carries a stock-photo or photographer watermark, say you will not remove it and stop there.
- ID, passport and visa photos: make the size and background colour the user asked for, but say that official acceptance rules (size, head position, expression, background) are theirs to check with the issuing office. Do not promise a photo will be accepted.

Work in `/tmp/.scratch/background-remover/`. Never install anything: there is no cut-out package in the sandbox and none may be added. Pillow and numpy are enough.

`SKILL_DIR` below is the `skill_dir` from the `skill_view` result that loaded this skill (scripts are in its `scripts/` folder); use the full path in every command. If you do not have it, find `cutout.py` under `~/.computer/skills` with `search_files`.

## Step 1: Get the picture and the job

- An uploaded image arrives as a URL in the message context. Download it: `curl -L -o /tmp/.scratch/background-remover/original.<ext> "<url>"`. If the user gave a path, use it. If they point to Google Drive or Dropbox and it is connected, fetch it from there; otherwise ask them to attach it.
- **No picture attached**: there is nothing to cut out. Reply in two or three lines: say what you can do (transparent PNG, white or coloured background, exact sizes), and ask them to attach the photo. This is the one case where you deliver no file.
- Decide the outputs from the message: transparent PNG; the subject on white or a named colour (as JPG or PNG); the sizes named, or presets from Step 4. With no instructions beyond "remove the background", deliver the transparent PNG only.

## Step 2: Choose the route

```bash
echo '{"image": "<original>", "inspect": true}' > /tmp/.scratch/background-remover/inspect.json
python3 SKILL_DIR/scripts/cutout.py /tmp/.scratch/background-remover/inspect.json
```

Read `recommended_route` in the result:

- **`border`**: the edge of the picture is one flat colour (studio white, grey, a plain wall). Cut it out in code directly from the original. Do not call `image_generate`: the original pixels stay untouched, which is the best result.
- **`edit-green` or `edit-magenta`**: the background is a scene, a texture or a gradient. Use the edit model to put a solid colour behind the subject, then cut that colour out in code. Green is the default; magenta is chosen for you when the subject itself has green in it.

## Route border: cut out in code

```bash
echo '{"image": "<original>", "output": "/tmp/.scratch/background-remover/cutout.png", "mode": "border"}' > /tmp/.scratch/background-remover/cut.json
python3 SKILL_DIR/scripts/cutout.py /tmp/.scratch/background-remover/cut.json
```

It removes the flat colour that is connected to the edge of the picture (and large enclosed gaps such as a mug handle), softens the edge and removes the background colour mixed into edge pixels. If it prints `ok: false`, the background is not flat enough: use the edit route.

**Soft shadow left under the subject** (a grey smear under a product, seen in the Step 5 check or when the subject's bounding box looks too tall): for a colourful subject, run the same job again with `"shadow": "remove"` added. Do not write your own matting code. Never use it on a black, grey or white subject, because those parts get cut away too.

## Route edit: solid key colour through the edit model

1. Make the original available as a URL: use the message's image URL if you have it, otherwise `publish_artifact` the local file with `kind: "file"` and `as_input: true` and use the URL it returns.
2. Call `image_generate` with top-level parameters `image_url` and `prompt`:

   ```
   Keep the subject exactly as it is: same shape, colours, details, labels, text, logo and position. Replace the entire background with a pure solid flat <#00FF00 green | #FF00FF magenta> colour, with no shadow, no reflection, no gradient and no floor line. Change nothing about the subject.
   ```

3. Download the returned image with `curl -L` into `/tmp/.scratch/background-remover/edited.png`.
4. Key the colour out, comparing with the original to catch changes:

   ```bash
   echo '{"image": "/tmp/.scratch/background-remover/edited.png", "output": "/tmp/.scratch/background-remover/cutout.png", "mode": "key", "key": "#00FF00", "reference": "<original>"}' > /tmp/.scratch/background-remover/cut.json
   python3 SKILL_DIR/scripts/cutout.py /tmp/.scratch/background-remover/cut.json
   ```

   (Use `"key": "#FF00FF"` for magenta.) If it prints `ok: false` because the background is not solid, call `image_generate` once more with the same prompt and "the background must be one single flat colour" added. If it fails again, tell the user the cut-out could not be made cleanly and what you tried; do not publish a bad file as if it were good.
5. The edit model returns its own size, often smaller than the original. Say in the reply what resolution the cut-out has, and that it is lower than the original if so.

## Step 3: Check the cut-out in code

Read the script's result and act on it:

- `has_alpha_channel` is true and `corners_transparent` is true.
- `transparent_share` between 0.05 and 0.95; the script warns otherwise.
- `subject_box` is inside the picture and `subject_touches_edge` is false (if true, the original photo cuts the subject off: say so).
- `warnings`, including `subject_drift` for the edit route: copy each one into the reply in plain words.

## Step 4: Export the sizes and formats

Write every output in one job. `fill` is `transparent` (PNG or WebP only) or a hex colour; a JPG always gets a colour (white by default). `subject_fill` is how much of the canvas the subject may fill (default 0.85).

```bash
echo '{"image": "/tmp/.scratch/background-remover/cutout.png", "outputs": [
  {"path": "/tmp/.scratch/background-remover/<name>-transparent.png"},
  {"path": "/tmp/.scratch/background-remover/<name>-2000x2000-white.jpg", "width": 2000, "height": 2000, "fill": "#FFFFFF", "subject_fill": 0.85}]}' > /tmp/.scratch/background-remover/sizes.json
python3 SKILL_DIR/scripts/export_sizes.py /tmp/.scratch/background-remover/sizes.json
```

Omit `width` and `height` to keep the cut-out's own canvas. The subject is trimmed to its visible edge, scaled to fit and centred, never stretched or cropped.

Presets, for when the user names a shape or platform but no size. These are common sizes and the user must check the platform's current requirement:

| Name | Pixels |
|---|---|
| square, marketplace | 2000 x 2000, subject about 85% |
| 4:5 portrait | 1080 x 1350 |
| 9:16 story | 1080 x 1920 |
| 16:9 | 1920 x 1080 |
| profile picture | 400 x 400, subject fills about 90% (`subject_fill` 0.9) |

If the script reports `enlarged: true`, the subject was scaled up from a smaller cut-out and may look soft: say so. Colour backgrounds: use the exact hex the user gave; for a colour name without a hex, pick the plain colour, state the hex you used, and offer to change it.

## Step 5: Look at it, then publish

1. Put the transparent PNG on a mid-grey or contrasting flat background with Pillow (never a pure white one, which hides white halos) and call `media_analyze` on that. Ask: is any part of the subject missing (thin handles, straps, hair, glass, transparent parts), is there a coloured halo or leftover background at the edges, and is anything of the subject different from the original (label text, logo, colours, shape).
2. For the edit route, also look at the original with `media_analyze` and compare shape, colours and any text or logo on the subject with the cut-out. Only say the subject is unchanged if you compared; otherwise say you did not compare. If anything changed, say so and offer one retry.
3. Say plainly when edges are rough. Fine hair, fur, glass, smoke and shadows are a known limit of this method.
4. Publish every file with `publish_artifact`, `kind: "file"`, named `<name>-<what>.<ext>`. Do not publish the grey-background check picture.

## The reply

Start with the result, not with what you did. Do not begin with "I'll load the skill" or narrate tool use. Then:

1. The files, one line each: name, pixel size, format, background.
2. One line on how it was made: cut out in code from the original, or via the edit model with a solid colour behind the subject.
3. What you checked and found, including any missing part, halo, changed detail, enlarged subject or low resolution. If there is nothing to report, say the check found no missing parts or halo.
4. For ID or passport photos, the line about official rules.

## When the user asks for a change

Change only what was asked: another background colour, another size, a tighter or looser fit. Reuse the cut-out you already made instead of cutting out again, keep the other files as they were, use the same file names with a suffix, and say in one line what changed.

## Final self-check

- Every file has the exact pixel size the user asked for; the PNG has an alpha channel; the JPG has a colour background.
- The subject is not stretched, cropped or changed, and the reply reports anything that was.
- No size, colour or requirement was invented.
- The reply is in the user's language and does not start with narration.
