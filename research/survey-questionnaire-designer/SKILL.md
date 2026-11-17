---
name: Survey and Questionnaire Designer
description: >
  Designs an unbiased survey, or fixes a draft one: neutral question wording, the right scales, sensible order, sample size and an analysis plan, ready to paste into a form tool.
  Use it for "design a survey", "write a questionnaire", "fix my leading questions", "review my survey", "survey for my thesis".
---

# Survey and Questionnaire Designer

A good result is a short questionnaire the user can paste straight into a form tool, where every question has a purpose tied to a decision, the wording is neutral, the answer options are complete, and an analysis plan says what to do with the answers. The whole job is finished in one reply. Never open with questions to the user.

## Step 1: Decide the job and the gaps

1. Work out which job it is:
   - **Design**: the user wants a new survey.
   - **Review**: the user pasted a draft. Do Step 4 first, then deliver the corrected questionnaire (Steps 2, 3 and 5 as needed).
2. Pin down four things from the message: the decision the survey informs, the audience, the survey length they want, and how it will be sent (email, in-app, link, paper).
3. If any of these is missing, do not ask. Choose a sensible default, and list it in an "Assumptions" line at the top of the reply (for example "Audience: not given, assumed current customers"). Never invent facts about the user's company, product or audience: refer to them only as the user described them, and use bracketed fields like `[product name]` where a name is needed.
4. Check that a survey is the right tool. Surveys measure how common, how often and how strongly something is felt. They do not discover problems nobody has named yet. If the user's real need is "why" or "what are we missing", say so in one sentence, include two or three open-text questions, and suggest a few interviews alongside.

## Step 2: Draft the questionnaire

Follow this order:

1. **Introduction** (3 lines): the purpose in neutral words, the time it takes, and whether answers are anonymous or confidential. Do not hint at the "right" answer. State the time only as an estimate based on the number of questions (about 4 to 5 questions per minute is a fair rule of thumb for closed questions).
2. **Screening and demographic questions**: only those the analysis needs. Short, at the start.
3. **Behavioural questions** (what people did, how often) before attitude questions.
4. **Attitude and satisfaction questions**.
5. **Open-text questions** last, one to three at most.
6. **Closing**: thank the respondent, and optionally offer a follow-up contact route.

Keep it short. Default to 8 to 12 questions and under 5 minutes unless the user asked for more. Every question you add lowers completion and data quality, so cut any question that no decision depends on.

## Step 3: Write each question well

Pick the type from this table.

| Type | Use for | Caution |
|---|---|---|
| Single choice | Mutually exclusive options | Options must be exhaustive; add "Other (please specify)" or "None of these" when needed |
| Multi-select | Several answers can apply | Not for ranking; say "Select all that apply" |
| Likert (agreement, satisfaction) | Attitudes | One direction across the whole survey; label every point or at least both ends |
| Rating (0 to 10, NPS) | A single measure | State what each end means |
| Ranking | Relative importance | At most 5 to 7 items; it is tiring |
| Open text | Explanation, surprises | Use sparingly; it is costly to analyse |

Rules for wording:

- **One question per question.** Split "How easy and enjoyable is checkout?" into two.
- **No leading or loaded words.** "How much do you enjoy our fast shipping?" assumes enjoyment and praises the shipping. Ask "How would you rate the shipping speed of your last order?" with a balanced scale.
- **Neutral, balanced scales.** Equal numbers of positive and negative options, an honest midpoint, plus "Not applicable" or "Don't know" where respondents may lack an opinion.
- **Short recall windows.** Ask about the last week, month or most recent occasion, not "the past 12 months".
- **Behavioural and specific.** "In the last 30 days, how many times did you...?" beats "Do you often...?". Use ranges that do not overlap.
- **Plain words.** Use the respondent's own terms, not internal product names or jargon.
- **No forced answers on sensitive items.** Add "Prefer not to say".
- **Scales**: 5-point and 7-point Likert are both defensible, and 5 is easier for respondents. Keep the direction the same throughout (1 = lowest, highest number = most positive).
- **NPS**: "How likely are you to recommend [product] to a friend or colleague?", 0 to 10. Promoters 9 to 10, passives 7 to 8, detractors 0 to 6, NPS = % promoters minus % detractors. It is one comparable number, not a full satisfaction measure; pair it with an open "What is the main reason for your score?".
- **SUS** (System Usability Scale): if the user wants perceived usability of a product, use the standard ten statements word for word and score 0 to 100. A score near 68 is commonly quoted as average. Do not rewrite its items.

## Step 4: Review mode (when the user pasted a draft)

Go through the draft question by question and make a table: `#`, original wording, problem (leading, loaded, double-barrelled, vague, overlapping options, missing options, unbalanced scale, long recall, jargon, wrong order), and the rewrite. Quote the original exactly. If a question is fine, say "No change" rather than inventing a flaw. Any change the user did not ask for, such as a new recall window or an added screening question, must be marked "(assumption)" in the table and also listed in the Assumptions line. Then give the full corrected questionnaire in the same shape as Step 5.

## Step 5: Sample size and analysis plan

1. **Sample size.** Do the arithmetic in `execute_code`, never by hand. For a proportion, n = z^2 * p * (1 - p) / e^2 with z = 1.96 for 95% confidence, p = 0.5 (most cautious) and margin of error e. Use the user's margin if given, otherwise 5%: that gives about 385 for a large population. If the user gave a population size N, apply the finite-population correction n_adj = n / (1 + (n - 1) / N). Copy the computed numbers into the reply. If the user gave no population size, say that and assume a large population. Note that a convenience sample (people who chose to answer) does not become representative just because it is big; say what groups may be missing.
2. **Response expectations.** Do not invent a response rate. Say the number of invitations needed equals the target responses divided by the response rate the user expects, and give the formula with their figure if they gave one, otherwise mark it "not given". The target responses is the final adjusted n (after the finite-population correction, if applied), never the unadjusted n. Compute every derived figure in `execute_code` from that final n: each row of an invitations table, the margin of error at any other sample size (e = z * sqrt(p * (1 - p) / n), times sqrt((N - n) / (N - 1)) when N is known), and any quoted range. Before writing the section, check that every figure in it uses the same target n.
3. **Fielding advice.** Give the send method and timing only. Do not claim effects, such as "a reminder lifts response" or "Tuesdays work best", unless the user supplied them.
4. **Analysis plan**, one line per question or group of questions: what you will report (full distribution, not just the mean; median for ordinal scales), which segments to cross-tabulate (only segments the user named or that the decision needs), how to code open text (read a sample, group into themes, report the top themes with example quotes), and always report sample size and response rate beside every result.

## Step 6: The reply

Put everything in the reply itself, in this order:

1. **Assumptions** (one short line each; "none" if the user gave everything).
2. **Survey goal**: one sentence: "This survey will help decide `<the decision>`".
3. **Questionnaire**, numbered, each question as:
   - `Q<n>. <exact question text>`
   - `Type / options:` the full answer options and scale labels
   - `Purpose:` which decision or analysis it feeds
   - `Required:` yes or no
   Include the introduction and closing text, written out in full.
4. **Sample size and fielding**: the computed numbers, how and when to send, and a reminder to pilot the survey with 3 to 5 people from the audience before launch, asking them to say aloud what each question means to them.
5. **Analysis plan** as in Step 5.
6. **Limits**: one or two lines on what this survey cannot tell the user (such as the "why" behind answers) and on non-response bias.

For a review, put the issues table before the corrected questionnaire.

## Hard rules

- Never invent numbers, benchmarks, response rates, customer details or findings. Anything not given by the user is an assumption and is labelled as one.
- Every sum goes through `execute_code`, including invitations and margins at other sample sizes, and all of them use the final adjusted n.
- Never state engagement lifts or timing benchmarks the user did not give.
- Deliver the full questionnaire in the reply. Build a file only if the user asks for one (a .docx or .csv), and then publish it with `publish_artifact`.
- A draft survey is a draft until the user sends it. Do not claim to have sent, posted or created it in any tool.
