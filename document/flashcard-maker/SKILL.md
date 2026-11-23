---
name: Flashcard Maker
description: >
  Turns your notes, a chapter or a topic into flashcards: a flip-card deck to study on screen plus a print-and-cut PDF sheet.
  Use it for "make flashcards", "turn these notes into cards", "vocabulary flashcards", "cards to memorise".
---

# Flashcard Maker

A good deck has one fact per card, a short question or term on the front, a short answer on the back, and nothing the user's material does not support. The user gets an interactive flip deck (published to the chat), a PDF of 8 cards per A4 sheet to print double-sided and cut out, and the card list in the reply. A two-column .csv is added when the user asks for one or mentions an app such as Anki or Quizlet.

Hard rules:
- Write the cards in the language the user wrote in, unless they ask for another. For vocabulary decks the front is the word in the language being learned and the back is the meaning in the user's language. Keep the user's names, figures and terms exactly as given.
- Use only the user's material. If the user gave pasted terms and definitions, keep their wording: do not reword, add or drop cards. If the user gave only a topic, write the cards yourself using well-established facts only, no invented statistics, dates or quotes, and say in the reply that the cards were generated and should be checked.
- 10 to 40 cards. If the material has more than 40 facts, keep the 40 most important and say how many were left out. If the user wants more, build a second deck.
- Any number or calculation on a card is computed in `execute_code`, never in your head.
- Do not ask questions. Decide, state the assumption in one line, deliver.
- Never install a browser or any PDF package. The script finds Chrome itself; if it prints `PDF NOT BUILT`, publish the print html as `html_preview` and say so.

## Step 1: Write the cards

1. Pick the mode. Facts and concepts: front is a question or a short prompt, back is the shortest correct answer. Vocabulary: front is the word, back is the meaning, `extra` is one short example sentence (only if the user gave one, or write a simple one and mark it as generated in the reply).
2. One fact per card. A back that needs more than about 25 words should be split into two cards. Fronts must be distinct from each other.
3. Order cards in the order of the user's material.
4. Choose a short title from the user's words, and labels for the two sides in the deck language (for example the words for "Question" and "Answer", or "Word" and "Meaning").
5. `dir` is `rtl` for Arabic, Hebrew, Persian and Urdu, otherwise `ltr`. `lang` is the language code.

## Step 2: Build the deck, the print sheet and the csv

1. Call `skill_view` on this skill. Its result has `skill_dir`, the skill's folder in the sandbox. Use the full path where the commands below say `SKILL_DIR`. If `skill_view` gives no path, find `build_cards.py` under `~/.computer/skills` with `search_files`.
2. Use `write_file` to save `/tmp/.scratch/flashcard-maker/spec.json`:

```json
{"config": {"title": "<title>", "lang": "<code>", "dir": "ltr", "frontLabel": "<front label>", "backLabel": "<back label>",
            "ui": {"card": "...", "of": "...", "flip": "...", "prev": "...", "next": "...", "shuffle": "...",
                   "know": "...", "dontKnow": "...", "known": "...", "learning": "...", "hint": "...",
                   "doneTitle": "...", "reviewLearning": "...", "restart": "...", "allKnown": "..."}},
 "cards": [{"front": "...", "back": "...", "extra": "optional"}]}
```

   The `ui` block holds the deck's button and label texts. Translate every key into the deck language. Meanings: `card` and `of` make "Card 3 of 12"; `know` is "I know it"; `dontKnow` is "Still learning"; `known` and `learning` label the two piles; `hint` is "Click the card or press Space to flip. Arrow keys move between cards."; `doneTitle` is "Round complete"; `reviewLearning` is "Review the cards still learning"; `restart` is "Start again"; `allKnown` is "You know every card." In English leave `ui` out.
3. Run in `terminal`:
   `python SKILL_DIR/scripts/build_cards.py SKILL_DIR/templates/deck.html /tmp/.scratch/flashcard-maker/spec.json /tmp/.scratch/flashcard-maker/out <deck-name>`
   with `<deck-name>` a short file name from the title, no spaces. The script writes `<deck-name>.html`, `<deck-name>-print.pdf` and `<deck-name>.csv`, checks that the card count is the same in all of them and that the PDF has an even number of pages (fronts and backs alternate), and prints the card list. Fix any `ERROR` and run again (an ERROR about page count means some card text is too long: shorten it). A `WARNING` lists interface texts still in English: translate them and run again.
4. Compare the printed card list with your plan: same count, same wording.
5. If the script prints `PDF NOT BUILT`, Chrome is missing: publish the print html it names with `kind: "html_preview"` instead of the PDF and say so in the reply.

## Step 3: Publish

1. `publish_artifact(path=".../<deck-name>.html", kind="html_preview")` for the flip deck.
2. `publish_artifact(path=".../<deck-name>-print.pdf", kind="document")` for the print sheet.
3. Only if the user asked for a csv or an import into another app: `publish_artifact(path=".../<deck-name>.csv", kind="file")`.

## Step 4: Reply

The reply contains, in the deck language:
1. One line: how many cards, the mode, and what was published (flip deck, print PDF, csv if asked).
2. How to use the deck, two lines: click or tap the card or press Space to flip, mark "I know it" or "Still learning", shuffle, and review the cards still learning at the end of a round (progress is kept only while the page stays open).
3. How to print: double-sided, flip on the long edge, A4, scale 100 percent; the back pages are already mirrored so each answer lines up behind its question; cut along the dashed lines.
4. The card list as a numbered list `N. <front> -> <back>`, so it can be checked.
5. One line on assumptions. If you wrote the cards (or any example sentences) from a topic, say plainly that you generated them and ask the user to check them before studying.

Do not paste the page's code in the reply.

## When the user asks for a change

Change only what was asked and keep everything else exactly as it was. Edit `spec.json` (if the file is gone, rebuild it from the card list in your previous reply), run the same command with the same `<deck-name>`, publish the same files again and say in one line what changed (for example "card 5 reworded, 2 cards added at the end").
