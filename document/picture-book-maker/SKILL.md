---
name: Picture Book Maker
description: >
  Makes an illustrated children's story as a finished PDF picture book: a cover, a matching picture and a page of big text for every scene.
  Use it for "make a picture book", "illustrated children's story", "turn my story into a book with pictures", "bedtime story book for my kid".
---

# Picture Book Maker

A good picture book is short (6 to 10 scenes, 20 to 45 words each), reads aloud easily for the age group, and has one picture per scene in which the main character always looks the same. You deliver a PDF with a cover, one page per scene and an end page, and give the story text in the reply.

## Hard rules

- Write the story and the book in the language the user wrote in, unless they ask for another. Keep names (the child's name, characters, places) exactly as given.
- If the user gave the story text, use it unchanged on the pages (split it into scenes without rewording). Otherwise write the story yourself.
- Pictures never contain text, letters or signs: all words are typed in the HTML. Never generate a real child's likeness from a photo or description of a real person; characters are made-up animals, objects or generic cartoon children. If the user names a child, that name appears in the text or dedication only.
- Keep the story gentle and age-appropriate. When you write the story, comfort comes from feelings, play and kindness, never from explaining how the real world works (no "thunder is really..."): no real-world facts, numbers or causes in the story. Never ask questions first: decide, state assumptions, deliver.
- At most 10 scene pictures plus one cover picture, in total at most 11 `image_generate` calls.

## Step 1: Plan the book

1. Age group: the user's, or assume ages 3 to 6 (say so). Younger means shorter sentences and simpler words.
2. Scenes: 6 to 10. If the user gave a story or outline, one scene per beat (merge beats if there are more than 10, and say so). Each scene text is 20 to 45 words, one idea per page.
3. If you write the story: a small hook, a problem, three tries or events, a warm resolution. No scary endings. No facts or claims about the real world beyond what the user gave.
4. Character sheet: one line fixing the main character's look: what it is, age or size, colours, clothing or marks. Example shape only: `<animal or child>, <size>, <fur or skin colours>, <clothes>`. Use only what the user gave, or invent a simple look and mark it as an assumption.
5. Art style line: one line, the same for every picture, for example in this shape: `soft watercolour children's book illustration, warm colours, gentle lighting, simple shapes`.
6. For each scene, a one-sentence picture description: where it happens and what the character does. Wide scene, character in the middle, no text.

## Step 2: Make the pictures

1. Make `/tmp/.scratch/picture-book-maker/` with `terminal`.
2. Call `image_generate` once for the cover and once per scene, top-level parameters only. If the tool has a size, aspect ratio or orientation parameter, ask for landscape. Every prompt has exactly this shape, with the same character sheet line and the same art style line copied word for word each time:

   `<art style line>. <character sheet line>. Scene: <this scene's picture description>. Wide landscape composition, character centred. No text, no letters, no words, no speech bubbles.`

   The cover prompt's scene is the character in a happy, simple pose with the story's setting behind.
3. Copy or download each result to `/tmp/.scratch/picture-book-maker/cover.png` and `scene-1.png`, `scene-2.png`, ... (use `terminal` with `cp`, or `curl -L -o` for a URL).
4. If a call fails, retry it once. If it fails again, keep the page without a picture (Step 3 shows how) and say which scene in the reply. Do not stop the whole book.
5. Look at the cover and one scene with `media_analyze`: same-looking character, no text in the picture? Regenerate only an image that clearly shows text, once.

## Step 3: Build the PDF

1. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox; use the full path where it says `SKILL_DIR`. If it gives no path, find `book.html` under `~/.computer/skills` with `search_files`. Read `SKILL_DIR/templates/book.html` with `read_file`.
2. Write `/tmp/.scratch/picture-book-maker/page.html` with `write_file`: the template with
   - the title in `<title>` and the cover `h1`; the `by` line only if the user gave a dedication or a name ("For <the child's name>", translated); otherwise delete that `div`;
   - one scene `<section class="page">` per scene, in order, with its `scene-N.png` and the scene text exactly as in your plan (HTML-escape `&`, `<`, `>`), and the page number in `.num` (cover is page 1, first scene is 2);
   - for a scene with no picture, replace the `<img>` by `<div class="missing">` plus a short note in the book's language that the picture is to come;
   - the end page with "The End" translated and an optional short line (or delete the `<p>`);
   - `lang` and `dir` on `<html>` (`rtl` for Arabic, Hebrew, Persian, Urdu); the two colours in `:root` to suit the story (assumption).
3. Run: `python3 SKILL_DIR/scripts/build_pdf.py /tmp/.scratch/picture-book-maker/page.html /tmp/.scratch/picture-book-maker/<title-slug>.pdf <scenes + 2>`. It finds headless Chrome (on PATH or under `/root/.cache/puppeteer` or `/root/.cache/ms-playwright`), builds the PDF, writes `<title-slug>-standalone.html` (pictures inlined), checks the page count and flags any page whose text comes within 25 points of the bottom edge. The template shrinks long text by itself; if the script still flags a page, cut that scene's words (only if you wrote them; otherwise lower `.text` font-size) and run it once more.
4. Look at one scene page once (render it with `fitz` from `pymupdf` and use `media_analyze`): text fully visible, not cut off, picture present.
5. Never install a browser or a PDF package, and never rebuild the book with another PDF library: they are not needed and waste minutes. If the script prints CHROME NOT FOUND, publish `<title-slug>-standalone.html` as `html_preview` (`kind: "html_preview"`), give the story text in the reply, and say the PDF could not be built.

## Step 4: Publish and reply

1. Publish the PDF with `publish_artifact`, `kind: "document"`, named `<title-slug>.pdf`.
2. Reply in the user's language:
   - One line: the title, the number of pages, and the age group.
   - The story text, scene by scene, numbered, exactly as in the book.
   - "Assumptions:" age group, character look, art style, anything merged or any picture that failed.
   - One line offering changes ("other character colours", "shorter text", "a different ending").

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. A text change: edit `/tmp/.scratch/picture-book-maker/page.html`. A picture change for one scene: regenerate only that scene with the same character sheet and art style lines plus the new instruction, replace only that file. Rebuild the PDF under the same name, publish it again and say in one line what changed.
