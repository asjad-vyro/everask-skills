---
name: Story and Chapter Writer
description: >
  Writes or continues a short story, novel chapter or children's story that keeps your characters, world and rules consistent.
  Use it for "write chapter 3", "continue my story", "a bedtime story about a turtle", "rewrite this scene but never mention dates".
---

# Story and Chapter Writer

A good result is prose fiction that follows the user's rules to the letter, keeps characters and world consistent with what came before, hits the requested length, and comes with an updated story sheet the user can paste back next time. The story is in the reply itself.

## Hard rules

- **Language.** Write in the language the user wrote in, unless they ask for another. Keep every name, place and invented term exactly as given.
- **User rules beat everything.** Rules like "never mention dates or years", "she never speaks first", "no magic" apply to the whole text, including narration, chapter titles and the story sheet. Never break one to make the story better.
- **Do not invent canon the user gave differently.** Do not change a character's fixed traits, past events or world rules. New details you add are allowed but go on the story sheet as "new in this chapter".
- **Editing an existing text:** change only what was asked and keep everything else word for word.
- **Safety.** No sexual content involving minors. Do not use real private people as characters; invent names or use the ones the user gave for fictional people.
- **Counting in code.** Count words with `execute_code`, never by hand.

## Step 1: Build the story sheet

From the request and any pasted earlier chapters or notes, write a story sheet with these fields. Use what was given; fill gaps with plain choices and mark them "(my choice)". Keep it short.

```
STORY SHEET
Title / chapter: 
Language and length target: 
Audience / age group: 
Point of view and tense: 
Tone and genre: 
Setting (where, when in the story's own terms): 
Characters (name: fixed traits, goals, how they speak): 
World rules and invented terms: 
User rules (numbered, verbatim): 
Events so far: 
This chapter's job (what must happen): 
```

If the request is thin ("a bedtime story about a brave turtle"), decide: age group from the request, about 400 to 600 words for a bedtime story, simple words, a clear beginning, middle and calm ending, and one lesson shown, not announced. Say the length and choices you made.

## Step 2: Write the chapter

1. Follow the sheet: point of view, tense, tone, the chapter's job.
2. Aim for the requested length. If none is given: a scene about 500 words, a short story about 1,200 words, a chapter about 1,500 words, a children's story as above.
3. Show with action and dialogue; vary sentence length; give each character a distinct way of speaking from the sheet.
4. For children: short sentences, concrete images, repetition where it helps, a gentle ending. Match the age.
5. End the chapter so the next one can begin (unless it is the end of the story).

## Step 3: Check against the sheet

In `execute_code`, paste the draft and run:

1. Word count, and whether it is within 10 percent of the target.
2. For rules that can be searched (dates, years, digits, forbidden words, a name spelled differently), a search of the draft and list of hits.

Then read the draft once against every numbered user rule, character trait and world rule. Fix every violation and the length, then recount. Do not state any word count that did not come from the code.

## Step 4: Deliver

The reply, in this order:

1. The chapter, with its title (a title must also obey the rules).
2. One line: the word count from the code and the language.
3. The **updated story sheet** (same fields, with "Events so far" extended by what happened in this chapter and new details marked), inside a block the user can copy, headed "Paste this at the start of your next request".
4. A rule check: one line per user rule saying it was followed.
5. A line listing any choices you made that the user did not specify.

If the user asks for a file, load the built-in `docx` skill with `skill_view` and follow it, including its delivery step, and do not call `publish_artifact` for it; give the story sheet in the reply. If Google Docs or Notion is connected and the user wants the earlier chapters from there, you may read them; otherwise work from what they pasted.

## When the user asks for a change

Change only what was asked, keep everything else exactly as it was, word for word, and say in one line what changed. Recheck the rules and word count on the changed text, and update the story sheet. If a file was built, rebuild the same file type under the same name.
