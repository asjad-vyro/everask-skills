---
name: AI Image Prompt Writer
description: >
  Turns an idea or a brief into precise prompts for AI image models, and makes
  the images in EverAsk when asked. Picks the right model for the job
  (photoreal hero shots, images with readable text, posters and packaging,
  illustration, quick drafts, edits), spells out the subject, composition,
  light, lens, style and colours, keeps a character or product identical
  across a set, and writes clean edit instructions. Use it for "write an image
  prompt", "Midjourney prompt", "prompt for Nano Banana", "improve my image
  prompt", "product shot prompt" or "consistent character across images".
---

# AI Image Prompt Writer

Write image prompts that get the picture the user has in mind on the first or second try.

Image models fill every gap with the most average choice. A prompt that names only the subject leaves the light, the framing, the style and the colours to chance, which is why results look generic. Every prompt here decides those things, in the order the model weighs them.

## Step 1: Gather the brief

From the message and files, note:

- **What it's for**: an ad, social post, website hero, product shot, illustration, poster, thumbnail or concept art. This sets the aspect ratio: 1:1 or 4:5 for feed posts, 9:16 for stories, 16:9 for web banners and slides, 2:3 or 3:4 for posters and portraits.
- **The subject**, and the details that must be right.
- **Any words in the image**, exactly as they should appear.
- **Brand colours and fonts**, as names and hex codes.
- **References**: a product photo, a person, a style to match.
- **How many images**, and whether they're a set that must match.

Ask only if you can't tell what the image shows. Otherwise make the creative calls and state them.

If the whole job is putting a product into a scene, or a product ad poster, the built-in `product-shoot` and `ad-poster` skills do it end to end; load one with `skill_view`.

## Step 2: Pick the model

If the user named a model, write for it. If they want EverAsk to make the image, the `image_generate` tool's description lists the models available now and what each is for. Trust it over this list:

- **Drafts, variations and batches**: Z-Image Turbo, the default.
- **The final image**, such as a photoreal scene, a product, several people interacting, or anything that needs real-world knowledge: Nano Banana Pro.
- **Any image with words people must read** (a poster, menu, label, UI mockup, infographic or non-Latin text): GPT Image 2.5, or Seedream 5.0 Pro for dense layouts and packaging.
- **A transparent PNG** (a logo, sticker or cut-out): GPT Image 2.5 with `options: {"background": "transparent"}`.
- **Illustration, concept art, painterly and anime looks**: Midjourney v7.
- **Edits and combining references**: Nano Banana 2 Lite Edit by default; Nano Banana Pro Edit for complex changes; GPT Image 2.5 Edit to replace text exactly; Seedream 5.0 Pro Edit to change one thing and leave the rest untouched.

## Step 3: Write the prompt

Write full sentences, 30 to 80 words, in this order. Models give the most weight to what comes first.

1. **The subject**, with 3 to 6 defining details: "a ceramic pour-over coffee dripper in matte sage green, with a thin brass rim".
2. **The action or pose.**
3. **The setting**: place, time of day, season and era.
4. **One style or medium**, stated plainly: "editorial product photograph", "flat vector illustration", "loose watercolour".
5. **The light**: its source, direction and quality, such as "soft window light from the left, with a gentle shadow to the right". This is the biggest single lever on quality.
6. **Framing and camera**: shot size, angle, lens and focus, such as "close-up at eye level, 85mm, shallow depth of field".
7. **Colour**: 3 to 5 named colours tied to objects, such as "a cream (#F3EDE2) backdrop and a terracotta (#C65D3B) mug".
8. **Text**, if any (below).

**Words that steer:**

- **Shot size**: extreme close-up, close-up, medium, full, wide, establishing.
- **Angle**: eye level; low angle (power); high angle (smaller, vulnerable); overhead flat lay; Dutch tilt (unease).
- **Lens**: 24mm (shows the setting), 50mm (natural), 85mm (portrait, blurred background), macro, tilt-shift. Use f/1.8 for a soft background and f/8 for everything sharp.
- **Light**: golden hour, overcast, hard midday sun, softbox, rim light, Rembrandt, backlit, neon, candlelight, haze. High-key is bright and airy; low-key is dark and moody.
- **Composition**: rule of thirds, centred and symmetrical, leading lines, negative space for copy, foreground framing.
- **Materials**: matte, glossy, brushed metal, linen, worn leather, frosted glass.

**Text in the image:**

- Put the exact words in double quotes, early in the prompt, and keep each piece short. One to four words render most reliably.
- Say the type style ("bold condensed sans-serif", "elegant serif"), the sizes (a headline with a smaller line under it) and the position ("centred in the upper third").
- Ask for high contrast with the background.
- For long copy, generate the image without text and add the words in a design tool, or add them afterwards with GPT Image 2.5 Edit.

**Say what you want, not what you don't.** Most models have no negative prompt, and naming a thing can make it appear. Write "an empty, quiet street at dawn", not "no people, no cars". Midjourney's `--no` is the exception.

## Step 4: Adjust for the model

| Model | How to write for it |
|---|---|
| Nano Banana Pro, Nano Banana 2 | Conversational sentences, as if briefing a photographer. Strong with references ("the woman in image 1"); write edits as plain instructions. |
| GPT Image 2.5 | Describe the layout section by section (top, middle, bottom), quote every word exactly and name the fonts. Best for UI, menus, infographics and posters. |
| Seedream 5.0 Pro | Quote the text and say where it goes, and which language it's in. Good at dense layouts and text in many languages. |
| Midjourney v7 | Shorter, evocative phrases. In EverAsk, settings go in `options`, such as `{"stylize": 250, "chaos": 10}`, and `{"niji": "6"}` gives the anime model. Elsewhere, write them after the prompt: `--ar 4:5 --stylize 250 --no text`. |
| Z-Image Turbo | Write out the full description, since it doesn't expand short prompts: 40 to 70 words, with the light spelled out. |
| Grok Imagine | Plain language and one style anchor. For an edit, describe only the change. |
| Flux (outside EverAsk) | Prose with the most important thing first, no negative prompts, and hex colours tied to objects. Use Kontext for edits. |

## Step 5: Sets that must match

- **Write one style block** (medium, light, lens, palette with hex codes, and mood) and paste it word for word into every prompt in the set.
- **Write a fixed description** of each recurring character or product (age, hair and clothes; or materials, colour and logo position) and repeat it word for word.
- **Make a hero image first**, on the quality model. Then make every other image from it, passing it as a reference: "the same woman as in the reference image, with the same hair and outfit, now sitting at a café table".
- **Keep the model and aspect ratio** the same across the set.

## Step 6: Edits and references

- **One change per instruction**, with a plain verb: change, add, remove or replace. Chain bigger changes as separate edits.
- **For a removal, say what fills the space**: "remove the cup and continue the wooden table surface".
- **Protect what matters** with a short closing clause: "keep her face, the logo and the layout exactly the same".
- **For a change to the whole image** (night, winter, a new style), add "keep the composition and the subject unchanged".
- **Several references**: number them and give each one a job: "image 1 is the person, image 2 is the outfit, image 3 sets the style". Use sharp, well-lit references.

## Step 7: Deliver

Reply with:

1. The model and aspect ratio you chose, and why, in one line.
2. Each prompt in its own code block, so it copies cleanly. For a set, give the style block first, then a table of the images and their prompts.
3. One or two suggestions for variations, such as another angle or palette.

Then offer to make the images in EverAsk.

## Step 8: Generate, only when asked

Call `image_generate` with `prompt`, `model` and `aspect_ratio`. Add `num_images` for variations of one prompt, `image_url` or `image_urls` for edits and references, and `resolution` ("2K" or "4K") only when the user asks for that size.

Look at each image before presenting it, with `media_analyze` if you need to. Is the text spelled right? Are hands and faces natural? Is everything the brief needs there? If something missed, fix one thing in the prompt, try again, and say what you changed:

| Problem | Fix |
|---|---|
| Generic or flat | Add concrete details, and say where the light comes from |
| The subject is lost in the scene | Put it first, and set the shot size |
| Text misspelled | Shorter text in quotes, earlier in the prompt, on a text model |
| Colours off | Fewer colours, each named with its hex code and tied to an object |
| An unwanted object appears | Describe what should be there instead |
| An edit changed too much | A short "keep" clause, or a smaller step |
| A character changed between images | Repeat the fixed description, and pass the hero image as a reference |
| Refused by the safety filter | Rephrase it; sending it again unchanged won't work |

Don't switch to another model without telling the user.

Then reply as in Step 7, with the model and why and the prompts you used, so the user can make more. For a set, that's the style block and then a table of the images and their prompts. If you made extra takes, say which images are the final ones.

## What not to do

- Don't put a real person's likeness, or another brand's logo or characters, into an image unless they're the user's own or the user has the rights.
- Don't name a living artist to copy their style; describe the style in its own terms.
- Don't add words to an image that the user didn't give, such as a tagline, a price or a subline; suggest them instead.
- Don't pad prompts with filler like "masterpiece, 8k, ultra detailed"; describe the actual picture.
- Don't put more than one style or one scene in a prompt.
- Don't generate images the user didn't ask for.
