---
name: Lecture and Lesson Slides
description: >
  Builds lecture, lesson or training slides in EverAsk's slide maker from a
  topic or from course material such as a syllabus, a textbook chapter, notes
  or a policy. Sets learning objectives, then builds the topic up one idea at a
  time with examples, check-your-understanding questions, a common-mistakes
  slide and a summary, pitched at the audience's level and sized to the
  session. Keeps the facts accurate and invents no sources. Use it for
  "lecture slides", "lesson slides", "slides to teach", "class presentation",
  "training deck" or "turn this chapter into slides".
---

# Lecture and Lesson Slides

Turn a topic or course material into slides a teacher or trainer can teach from, built in EverAsk's slide maker.

Good teaching slides follow how people learn: say what students will be able to do, build one idea at a time, show an example, check they got it, and close by tying it back.

## Step 1: Pin down the session

From the request, the attached material, and any file the user points you to in a connected app such as Google Drive, settle:

- **Topic**: and, when material is attached, which part of it to cover.
- **Audience and level**: such as Year 9 students, first-year undergraduates or new support hires. If none is given, infer it from the topic and the material.
- **Length**: when it's given, plan about one slide per 2 to 3 minutes; otherwise about 12 slides. At most 20 slides: that is the slide maker's limit.
- **Terms and notation**: use the material's own, so the slides match what students read.

Don't ask questions unless you can't tell what the topic is, or the request refers to material that isn't attached ("this chapter", "our policy"). Then ask one question.

## Step 2: Plan the slides

1. **Title**: the topic, and the course or session if given.
2. **Learning objectives**: 2 to 4, each starting with a verb a student can be checked on, such as explain, calculate, compare, identify or apply.
3. **Hook**: a question, a puzzle or a real case that makes the topic matter.
4. **What you already know**: a short recap of the idea this topic builds on, if there is one.
5. **The ideas**: one per slide, in teaching order. Follow each hard idea with an example slide, worked step by step for anything numerical or procedural.
6. **Check your understanding**: after every 2 or 3 ideas, a slide with one question. Put its answer on the next slide, never on the same one.
7. **Common mistakes**: the misconceptions students usually have about this topic, and the fix for each.
8. **Practice**: one short task to do in the session.
9. **Summary**: the main points, matched to the objectives.
10. **Exit question**: one question that tests the main objective.

Fit the language to the level: short sentences and everyday words for school students, and the field's terms, defined on first use, for university and professional audiences.

**Accuracy matters more than anything else on teaching slides.** Definitions, formulas, dates and figures must be correct. Take them from the material when there is any; otherwise use only well-established facts you are sure of, and leave a figure out rather than guess it. Name a source only if it is real and you saw it in the material or found it with web search. Never invent studies, quotes or citations.

## Step 3: Build the deck

Load the built-in `design-slides` skill with `skill_view`. It loads the slide tools and explains how to call them. Follow it to build the deck, with these changes:

- The request you pass to its outline step and its build step is the user's message, word for word, followed by this brief:

  ```
  LESSON BRIEF
  Audience: <level>. Length: <minutes, or not given>.
  Objectives:
  - <objective>
  Slide plan (follow exactly):
  1. <title>: <bullets>
  Rules: Facts, figures, dates and formulas must be accurate, and come from the material when it is given. Do not invent plausible figures, quotes, studies or sources. Each answer goes on the slide after its question.
  ```

- Pass the same brief to both steps.
- If the user attached material, also pass its text as the deck's source, the way `design-slides` describes, so the slides keep its facts.

The outline appears in the chat for the user to approve or change before the slides are made. Don't repeat it in your reply.

## Step 4: Hand it over

Reply in a few lines: the slide count, the level you pitched it at, and the look the slide maker picked.

The slides carry no speaker notes. If the user asks for notes or a script, write them as a separate document with one short section per slide number. Offer that, or a short quiz on the same material, as the next step.

## What not to do

- Don't put an answer on the same slide as its question.
- Don't invent facts, statistics, quotes, studies or sources.
- Don't paste the slides or their code into the chat.
