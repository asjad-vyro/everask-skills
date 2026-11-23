---
name: Group Presentation Script
description: >
  Writes a spoken script for a group presentation, split by speaker, tied to slide numbers and timed to your slot.
  Use it for "write what each of us says", "script for our group presentation", "split this talk between 4 people in 10 minutes".
---

# Group Presentation Script

A good result is a script each presenter can read aloud: it sounds like people talking, each part fits the time, hand-overs are smooth, and every fact comes from the user's material. The script is the reply itself.

## Hard rules

- **Language.** Write the script in the language the user wrote in, unless they ask for another. Keep their names, figures and terms exactly as given. Do not build anything that only works in English.
- **No invented facts.** Use only the topic material, slides or outline the user gave. If the script needs a fact, number, date, quote or source the user did not give, either leave it out or write `[check: ...]` at that spot. Never invent a statistic or a study.
- **Thin requests (a topic and nothing else).** Keep the content to basic, uncontroversial points anyone could say about the topic. Anything about the speakers' own school (including its size or how many people are in it), city, company, class, results, survey answers, local rules, local conventions (bin colours, permit names, prices) or personal experience is not known to you: do not state it as fact. Leave a fill-in spot in the script's language, such as `[add: your own example]`, and keep the word budget around it. Trend claims ("fewer than before", "more every year") need `[check: ...]` too.
- The whole reply, including the opening line of assumptions and any closing note, is in the user's language.
- **All counting in `execute_code`.** Never count words or minutes by hand.
- Write for the ear: short sentences, plain words, no reading out bullet lists, no essay style. For non-native speakers or younger students, use even shorter sentences.
- Do not add stage directions about gestures unless asked. Short cues like "[next slide]" are allowed.

## Step 1: Read the request

Find: the topic; the slides or outline (numbered; if not given, you will plan them); the number of speakers and their names (otherwise "Speaker 1", "Speaker 2", ...); total minutes; level or audience (class, team meeting, clients). If minutes are not given, assume 10 and say so. If speakers are not given, assume 3 and say so. Do not open with questions.

If no slides were given, make a slide plan of one slide per main point: about one slide per minute, with an opening slide and a closing slide. List it in the reply as "Slide plan" so the user can build the deck to match.

## Step 2: Word budget (in code)

In `execute_code`:

1. Planning rate: 130 words per minute (use 110 if the user says the speakers are non-native or the audience is young; say which you used).
2. Reserve 10 percent of the time for pauses and hand-overs. Speaking minutes = total minutes x 0.9. Total word budget = speaking minutes x rate.
3. Split the slides across speakers in order, as evenly as possible by number of slides; give a speaker more words only if the user said so. Opening slide goes to Speaker 1, closing to the last speaker (or the user's choice).
4. Per speaker: slides, words budget, minutes. Per slide: a word budget (opening and closing shorter; the rest equal).
5. Print the table.

## Step 3: Write the script

For each speaker in order, a heading with the speaker's name and slide numbers, then the text slide by slide:

```
## <Speaker name> (slides <a>-<b>)

**Slide <n>: <slide title>**
<what the speaker says>
```

Rules for the text:

1. The opening (Speaker 1): greet, say the topic, say in one sentence why it matters, and name who will speak on what.
2. Each slide: one main idea, said in your own words; do not read the slide's bullets one by one.
3. Hand-over line at the end of each speaker's part, naming the next speaker and the topic: "<Next name> will now show you ...".
4. Closing (last speaker): one-line recap of the main points, one closing thought, thanks.
5. Stay near each slide's word budget.

## Step 4: Check (in code)

Put the final script text in `execute_code`, count the words per speaker and in total, and compute the minutes at the planning rate. If the total is more than 10 percent over or under the budget, edit the script and recount once. Use the final counts only.

## Step 5: Questions

After the script, add **Likely questions**: two or three questions the audience could ask about this topic, each with a short answer of one to three sentences, using only the user's material (or `[check: ...]`). Say who could answer each, by name.

## Output shape

The reply holds, in this order:

1. One line of assumptions (rate used, speakers, minutes, slide plan if you made one).
2. The script (Step 3).
3. Likely questions.
4. A table at the end:

| Speaker | Slides | Words | Minutes |
|---|---|---|---|
| <name> | <a>-<b> | <counted words> | <minutes> |
| Total | | <counted> | <minutes> |

Do not state numbers in the table that did not come from the code.

If the user asks for a file, load the built-in `docx` skill with `skill_view` and follow it, including its delivery step; do not call `publish_artifact` for it. If an app such as Google Slides or Google Docs is connected and the user asks you to read their slides from there, you may; otherwise work from what they pasted.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, and say in one line what changed. If a change alters a speaker's length, recount and update the table. If a file was built, rebuild the same file type under the same name.
