---
name: Poster Text Editor
description: >
  Changes the date, name, price or wording on a poster, flyer or invitation you
  already have (image or PDF) and keeps the rest of the design exactly as it is.
  Use it for "change the date on this poster", "fix the price on my flyer",
  "replace the name on this invitation", "edit the text in this image",
  "swap my logo", or "make this poster fit a story and a square".
---

# Poster Text Editor

The user gives a finished graphic and asks for a small text change. A good result is the same file type and the same pixel size, with only the asked text different, set to match the original's position, size, weight and colour, and a list of what changed.

Do the whole job in one reply. Never open with questions: decide, state what you assumed, deliver. Write no text before your first tool call and none between tool calls: no "I'll load the skill", no "Let me". The first words the user sees are the result.

## Hard rules

- Write the reply in the language the user wrote in, unless they ask for another. Keep their names, figures and spellings exactly as given, and put the new text on the poster exactly as they typed it.
- Never invent text. Do not correct, translate, shorten or "improve" the new wording, and do not fill in a date, price, name, time or address the user did not give. If a change needs a fact you were not given, ask for nothing: leave the text as it is and say what is missing.
- Change only what was asked. Everything else on the graphic stays as it was.
- Decline to alter official or financial documents: IDs, passports, certificates, diplomas, tickets, receipts, invoices, payslips, bank or medical or legal papers, or anything where a changed date, amount or name would mislead someone about a fact. Say plainly why, and offer to help build a new, clearly original design instead. Posters, flyers, invitations, menus, social graphics and the user's own designs are fine.
- Replace a logo only with a logo file the user supplies. Never draw or generate one to stand in for a brand.
- Never claim the text is right until you have read it back from the final picture (Step 5).

Work in `/tmp/.scratch/poster-text-editor/`. Never install anything (no pip, no apt, no browser).

## Step 1: Get the file and the list of changes

- An uploaded image or PDF arrives as a URL in the message context. Download it with `curl -L -o /tmp/.scratch/poster-text-editor/original.<ext> "<url>"`. If the user gave a path instead, use it. If they point to a file in Google Drive or Dropbox and that app is connected, fetch it from there; otherwise ask them to attach it.
- **No file attached** (the message only describes a poster): there is nothing to edit. Reply in two or three lines saying what you can do (change dates, names, prices or wording on an image or PDF, keep the design, fit other sizes), that you need the file attached, and what you need from them: the old text and the new text. This is the one case where you do not deliver a file.
- Write the change list as `old -> new` pairs from the message. If the user says "change the date to 19 March" and the poster shows one date, the old text is that date. If the old text is ambiguous (two dates, say) and the message does not settle it, change the most prominent one and say so.
- Check the file type and size with Pillow (or PyMuPDF for a PDF). Note the pixel size: the output must match it.

`SKILL_DIR` below is the `skill_dir` from the `skill_view` result that loaded this skill (the scripts are in its `scripts/` folder); use the full path in every command. If you do not have it, find `edit_image.py` under `~/.computer/skills` with `search_files`.

## Step 2: Pick the route

| File | Background behind the text | Route |
|---|---|---|
| PDF | any | A: edit the live text in place |
| PNG, JPG, WebP | flat colour or a smooth gradient | B: draw the new text in code |
| PNG, JPG, WebP | photo, texture, pattern, or text with effects (glow, outline, 3D) | C: image-edit model |
| PDF that is only a picture (no live text) | see Route A dump | B or C on a rendered page |

Prefer B whenever the background around the text is plain, and always for Arabic, Chinese, Japanese, Korean, Thai, Hindi and other non-Latin text, and for long text: image models misspell these.

## Route A: PDF with live text

1. List the text so you can see how it is split:

   ```bash
   echo '{"pdf": "<in.pdf>", "dump": true}' > /tmp/.scratch/poster-text-editor/dump.json
   python3 SKILL_DIR/scripts/edit_pdf.py /tmp/.scratch/poster-text-editor/dump.json
   ```

   If `live_text_spans` is 0 the PDF is a picture: render the page to PNG with PyMuPDF at 200 dpi and use Route B or C, then save the result as a PDF with Pillow.
2. Edit:

   ```bash
   echo '{"pdf": "<in.pdf>", "output": "/tmp/.scratch/poster-text-editor/<name>-edited.pdf", "edits": [{"old": "<old text>", "new": "<new text>"}]}' > /tmp/.scratch/poster-text-editor/job.json
   python3 SKILL_DIR/scripts/edit_pdf.py /tmp/.scratch/poster-text-editor/job.json
   ```

   The script keeps position, size and colour, and sets the text in the closest available font (it says which). It moves later text on the same line if the new text is longer, and shrinks the text if it would run off the page. Read its `warnings` and repeat them to the user. If a phrase is "not found", look at the dump: the text is probably split across spans, so give the exact pieces.

## Route B: image, plain background

1. Find the old text's box. Try OCR first (it is in the sandbox):

   ```bash
   echo '{"image": "<original>", "phrases": ["<old text>"]}' > /tmp/.scratch/poster-text-editor/find.json
   python3 SKILL_DIR/scripts/locate_text.py /tmp/.scratch/poster-text-editor/find.json
   ```

   Use the `box` it returns. If it errors, or finds nothing (stylised or non-Latin text), call `media_analyze` on the image and ask for the bounding box of that exact text as fractions of the image width and height (left, top, right, bottom), tight around the text and nothing else. Use these as `box_frac`.
2. Edit. List every change in one job so the file is written once:

   ```bash
   echo '{"image": "<original>", "output": "/tmp/.scratch/poster-text-editor/<name>-edited.png", "crops_dir": "/tmp/.scratch/poster-text-editor/crops", "edits": [{"box": [x0, y0, x1, y1], "old": "<old text>", "new": "<new text>"}]}' > /tmp/.scratch/poster-text-editor/job.json
   python3 SKILL_DIR/scripts/edit_image.py /tmp/.scratch/poster-text-editor/job.json
   ```

   - Use `box_frac` instead of `box` for fractions. The box must be tight around the old text (padding of a few pixels is added for you). Include the whole line the user wants changed, or only the part that changes; if you change a part of a line, the box covers just that part and `old` is just that part.
   - Optional per edit: `align` (`left`, `center`, `right`; default is detected), `color` (hex), `bold`, `font` (path).
   - The script rebuilds the background under the old text from the pixels beside it (works for flat colours and smooth gradients), sizes the new text to the old text's height, picks regular or bold by width, matches the colour, keeps the baseline, and keeps the alignment. The output has the same pixel size and file type as the input (use the same extension as the original for the output file).
   - Read `warnings`. If it says the background is textured, switch to Route C for that edit. If the text got smaller to fit, tell the user.
3. Font match is approximate: the original font is rarely available. Say in one line that the new text is set in the closest available font.

## Route C: photo or textured background (image-edit model)

Call `image_generate` with top-level parameters `image_url` (the uploaded picture's URL, or publish the local file first with `publish_artifact`, `kind: "file"`, `as_input: true`, and pass the URL) and `prompt`. Prompt shape:

```
Edit this image. Change the text "<exact old text>" to "<exact new text>". Keep the same position, font style, size and colour. Change nothing else: the layout, the photo, the other text and the colours stay exactly as they are.
```

One text change per call is more reliable; for several changes, do them in turn, passing each result as the next `image_url`. Then check the output size with Pillow; if it differs from the original, tell the user (do not stretch it back). Image models misspell and can alter other details, so Step 5 is mandatory for this route.

## Step 3: Logo swap

Only when the user supplies the new logo file. Download it, remove any plain background if needed, scale it to fit the old logo's box (use `media_analyze` to find that box as fractions), paste it with Pillow over a background patch rebuilt the same way as in Route B, and keep the aspect ratio of the new logo. If the user did not attach a logo, say you need the file and change nothing else.

## Step 4: Other sizes (only if asked)

For a story, square, A3 or any other size, never stretch. Write the sizes in a job and run:

```bash
echo '{"image": "<edited image>", "outputs": [{"path": "/tmp/.scratch/poster-text-editor/<name>-story.png", "width": 1080, "height": 1920}]}' > /tmp/.scratch/poster-text-editor/sizes.json
python3 SKILL_DIR/scripts/resize_poster.py /tmp/.scratch/poster-text-editor/sizes.json
```

It scales the poster to fit inside the new canvas, centres it, and fills the rest with the poster's edge colour (or a blurred copy of it). Say in the reply that the poster was fitted, not cropped or stretched, and that a different shape may need the layout redone. Use the sizes the user named; do not invent a size list.

## Step 5: Verify, then publish

1. Look at the final picture with `media_analyze` (for Route B, the `crop` file in the script's output is a zoomed before/after of each edit and is the best thing to look at). Ask it to read out, character by character, the text that was changed, and to say whether anything else on the picture looks different from the original (other text, colours, logo, photo). For a PDF, read the text back with PyMuPDF `page.get_text()`.
2. Compare each read-back with the new text the user asked for, character by character. If one is wrong or anything else changed: retry once with the other route (B or C). If it is still wrong, deliver the best version and say exactly which characters are off.
3. Confirm in code that the output has the same pixel size (or page count and size) as the original.
4. Publish the final file with `publish_artifact`: `kind: "file"` for images, `kind: "document"` for a PDF. Name it exactly `<original file name>-edited.<same extension>` (keep the uploaded file's own name, do not invent a title). Send every file you made; when the user asked for several sizes, publish each.

## The reply

Start with the result, not with what you did. Do not begin with "I'll load the skill" or narrate tool use. Then:

1. The published file or files (with pixel sizes).
2. A change list, one line each: `<old text> -> <new text>`.
3. One line on what stayed the same, and one line on the route and font (for example: "text redrawn in the closest available font" or "edited with the image model").
4. What the read-back showed. If a character is off or something else shifted, say exactly what, and offer one more try. If the edit could not be made (an unclear box, an unsupplied logo), say so.

## When the user asks for a change

Change only what was asked, starting from the last version you made unless they say otherwise. Keep everything else exactly as it was, rebuild the same file type under the same name with a version suffix, and say in one line what changed.

## Final self-check

- Same pixel size and file type as the original (unless sizes were requested).
- Each new text matches what the user typed, character for character, and was read back from the picture.
- No text, date, price or name was invented, corrected or translated.
- Nothing else on the graphic changed, and the reply lists each change.
- The reply does not start with narration and is in the user's language.
