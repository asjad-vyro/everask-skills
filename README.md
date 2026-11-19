# EverAsk Skills

The 189 skills for the EverAsk Skills Library. Each skill is a folder with a `SKILL.md` at its top.

- 58 are copied unchanged from open-source repos at pinned commits, except for the `name` in `SKILL.md`, which is set to the Library card title. The tables below link each one's source and give its licence.
- The 3 slides skills are our own. They plan the deck, then build it with EverAsk's built-in slide maker.
- The 10 video, voice, music and image skills in Marketing are our own too. They run on EverAsk's own tools (`media_analyze`, `audio_transcribe`, `audio_generate`, `music_generate`, `image_generate`, `video_generate`, and ffmpeg in the sandbox) and use ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b)'s video production notes and provider guides; none of its text is copied.
- Swarm Rebuild Video in Website is our own `SKILL.md` and recorder around the page script of [Swarm Rebuild](https://github.com/DhvanilPatel/swarm-cursors/tree/3d49e0ac96172eb6af7ae8229b2152121bed2092), a tribute to Joel Califa's [Swarm](https://califa.github.io/swarm-site/). Its `scripts/swarm.js` is copied unchanged. That project has no licence yet and asks that its code not be reused without checking with its author and Joel Califa.
- 27 more (added November 2026) are adapted for EverAsk rather than copied: rewritten as numbered steps for its agent, with other products' machinery and promotion removed, connectors made optional, and each one tested end to end. 24 come from the open-source repos linked in the tables; Job Search, arXiv Paper Finder and Songwriter are our own, rebuilt from skills bundled with the agent.
- 77 more (added mid-November 2026) were found on [skills.sh](https://skills.sh) and in the repos behind it, and are adapted the same way: numbered steps for the EverAsk agent, other products' machinery and promotion removed, connectors optional, a rule against invented details, and sums done in code. Each has a config, a cover and two end-to-end test cases; the tables below link each one's source and give its licence.
- 13 more (added late November 2026) are for documents people print, submit or send, and for everyday spreadsheet jobs: formal letters, thesis chapters, lesson plans, exam papers, worksheets, one-page handouts, invoices and quotes, reference checks, documents turned into slides, reports from data, merging and comparing sheets, tables out of PDFs, and small-business trackers. 10 are written for EverAsk; Lesson Plan Builder, Invoice and Quote Maker and Citation and Reference Checker are adapted from the open-source repos linked in the tables. They follow the same rules as the adapted skills above, write in the user's language, and build the file in the same turn when a file is what the user needs. Each was written by one agent and corrected by a second reviewer, and has a config, a 600x800 cover and two test cases. Their end-to-end runs are still to do.

Each folder also has two files of our own: a `skill.config.json`, with the skill's Library type, example prompts and connector badges, and a `cover.webp` for its Library card.

## Import

One import gives every skill the same type, so import each type folder with its own link and pick the matching type:

| Type | Link | Skills |
|---|---|---|
| Document | https://github.com/asjad-vyro/everask-skills/tree/main/document | 38 |
| Slides | https://github.com/asjad-vyro/everask-skills/tree/main/slides | 3 |
| Email | https://github.com/asjad-vyro/everask-skills/tree/main/email | 11 |
| Data | https://github.com/asjad-vyro/everask-skills/tree/main/data | 30 |
| Engineering | https://github.com/asjad-vyro/everask-skills/tree/main/engineering | 16 |
| Marketing | https://github.com/asjad-vyro/everask-skills/tree/main/marketing | 43 |
| Research | https://github.com/asjad-vyro/everask-skills/tree/main/research | 23 |
| Website | https://github.com/asjad-vyro/everask-skills/tree/main/website | 12 |

Each skill folder looks like this:

```
email/
  cold-email/
    SKILL.md
    skill.config.json
    cover.webp
    the skill's other files
```

- **`skill.config.json`** is optional. Every field in it is optional too:

  ```json
  {
    "type": "email",
    "example_prompts": ["Write a cold email and 3 follow-ups to RevOps heads at Series B SaaS"],
    "connectors": ["gmail", "outlook", "hubspot"]
  }
  ```

  - `type`: the skill's type, the same as its folder.
  - `example_prompts`: up to 5, each up to 300 characters.
  - `connectors`: up to 10, written as the backend's slugs (lowercase letters, digits, `-` or `_`). They show as badges and don't connect anything.

  It must be valid JSON, so no trailing commas or comments. The import skips any value outside these limits and flags it; the check below catches both before you push.
- **Covers** are optional: one image named `cover` next to `SKILL.md`, as `.webp` (preferred), `.png`, `.jpg`, `.jpeg` or `.gif`, up to 5 MB and kept small. Every skill here has a 600×800 `cover.webp`.
- **Before you push**, run `uv run scripts/validate.py` (or `pip install pyyaml`, then `python3 scripts/validate.py`). It checks the import rules and exits non-zero on any failure. Add `--connectors <file>`, with the backend's slugs one per line, to check that every connector exists.

## Skills

### Document (45)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| 30-60-90 Day Onboarding Plan | [document/onboarding-plan-30-60-90](document/onboarding-plan-30-60-90) | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice/tree/f6c2358c133d294f02827f9a57a5394c6ecdb941/skills/recommended/onboarding-plan) | Apache-2.0 |
| Academic Writing Coach | [document/research-writing](document/research-writing) | [zLanqing/codex-claude-academic-skills](https://github.com/zLanqing/codex-claude-academic-skills/tree/7ed6377f0efb6a38951b48ef03b19d996e454b1f/research-writing-skill) | MIT |
| Business Model Canvas | [document/business-model](document/business-model) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-product-strategy/skills/business-model) | MIT |
| Compliance Check | [document/compliance-check](document/compliance-check) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/legal/skills/compliance-check) | Apache-2.0 |
| Cover Letter Writer | [document/cover-letter-generator](document/cover-letter-generator) | [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills/tree/74ae19e7c62b0516d1c298328e5544976c12da5d/skills/cover-letter-generator) | MIT |
| Customer Interview Script | [document/interview-script](document/interview-script) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-product-discovery/skills/interview-script) | MIT |
| Decision Memo and One-Pager | [document/decision-memo](document/decision-memo) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-business/skills/decision-memo) | MIT |
| Difficult Conversation Planner | [document/difficult-workplace-conversations](document/difficult-workplace-conversations) | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/3027f20f3181758385a1bb8c022d4041dfb4de84/skills/difficult-workplace-conversations) | MIT |
| Document Comparison | [document/compare-documents](document/compare-documents) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/assistant-workflows/compare-documents) | MIT |
| Document Proofreader | [document/proofread](document/proofread) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/assistant-workflows/proofread) | MIT |
| Exam and Quiz Paper Builder | [document/exam-builder](document/exam-builder) | Written for EverAsk | — |
| FAQ Builder | [document/faq-builder](document/faq-builder) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-cowork/skills/faq-builder) | MIT |
| Formal Letter Writer | [document/formal-letter](document/formal-letter) | Written for EverAsk | — |
| Grammar and Flow Check | [document/grammar-check](document/grammar-check) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-toolkit/skills/grammar-check) | MIT |
| Grant Proposal Writer | [document/grant-proposal](document/grant-proposal) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-cross/skills/grant-proposal) | MIT |
| Hiring Packet Builder | [document/job-post-builder](document/job-post-builder) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/job-post-builder) | Apache-2.0 |
| Interview Prep | [document/interview-prep-generator](document/interview-prep-generator) | [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills/tree/74ae19e7c62b0516d1c298328e5544976c12da5d/skills/interview-prep-generator) | MIT |
| Invoice and Quote Maker | [document/invoice-quotation](document/invoice-quotation) | [claude-office-skills/skills](https://github.com/claude-office-skills/skills/tree/9c4c7d5cd2813a8936bf2c9fdb174ea883b85a11/invoice-generator) | MIT |
| Lesson Plan Builder | [document/lesson-plan](document/lesson-plan) | [anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills/tree/31fd6dbb0c07cb50bb3ce7f62a4135a393bd0e8c/plugin/skills/k12-lesson-plan-creation) | Apache-2.0 |
| LinkedIn Profile Writer | [document/linkedin-profile](document/linkedin-profile) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-personal/skills/linkedin-profile) | MIT |
| Meeting Brief | [document/meeting-briefing](document/meeting-briefing) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/legal/skills/meeting-briefing) | Apache-2.0 |
| Meeting Minutes | [document/meeting-minutes](document/meeting-minutes) | [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/61fa1fa8fcc63d6dbd2f07a75aeb8e214df5acfb/skills/meeting-minutes) | MIT |
| Notion Knowledge Capture | [document/notion-knowledge-capture](document/notion-knowledge-capture) | [openai/skills](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/notion-knowledge-capture) | MIT |
| OKR Writer and Reviewer | [document/okr-writer](document/okr-writer) | [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills/tree/3456e5e309f38ac2a66943f20d4aaf8031268dfb/skills/foundation-okr-writer) | Apache-2.0 |
| One-Page Handout Maker | [document/one-page-handout](document/one-page-handout) | Written for EverAsk | — |
| Performance Review Writer | [document/performance-review](document/performance-review) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/human-resources/skills/performance-review) | Apache-2.0 |
| Personal Statement Writer | [document/personal-statement](document/personal-statement) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-students/skills/personal-statement) | MIT |
| Plain Language Rewrite | [document/plain-language-rewrite](document/plain-language-rewrite) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-cowork/skills/plain-language-rewrite) | MIT |
| PRD Writer | [document/create-prd](document/create-prd) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-execution/skills/create-prd) | MIT |
| Pre-Mortem Risk Register | [document/premortem-risk-register](document/premortem-risk-register) | [product-on-purpose/thinking-framework-skills](https://github.com/product-on-purpose/thinking-framework-skills/tree/6ab95db2d6469e4b65f3eb3ed265e46a6a1e69a8/skills/think-premortem) | Apache-2.0 |
| Pricing Strategy | [document/pricing](document/pricing) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/pricing) | MIT |
| Proposal and Quote Builder | [document/proposal-builder](document/proposal-builder) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/proposal-builder) | Apache-2.0 |
| Public Speaking Coach | [document/public-speaking](document/public-speaking) | [RefoundAI/lenny-skills](https://github.com/RefoundAI/lenny-skills/tree/13598cc54e09399bc1bc1398b0fca284110efb2f/skills/public-speaking) | MIT |
| Reference and Recommendation Letter Writer | [document/reference-letter](document/reference-letter) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-lifeadmin/skills/reference-letter) | MIT |
| Resignation Letter Writer | [document/resignation-letter](document/resignation-letter) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-resignation/skills/resignation-letter) | MIT |
| RFP Responder | [document/rfp-responder](document/rfp-responder) | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/e4a1dc3695908dd5a6c811cc76ab7aa4cf95f2f0/commercial/skills/rfp-responder) | MIT |
| SEO Content Brief | [document/seo-content-brief](document/seo-content-brief) | [calm-north/seojuice-skills](https://github.com/calm-north/seojuice-skills/tree/c1f633bea512365ba04477076369e418ecc82ffd/skills/brief) | MIT |
| SOP and Process Writer | [document/process-doc](document/process-doc) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/operations/skills/process-doc) | Apache-2.0 |
| Stakeholder Update Writer | [document/stakeholder-update](document/stakeholder-update) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/product-management/skills/stakeholder-update) | Apache-2.0 |
| Startup Team Planner | [document/team-composition-analysis](document/team-composition-analysis) | [wshobson/agents](https://github.com/wshobson/agents/tree/7e2fb559cf4b824b27f1fec49fe88f7511066d26/plugins/startup-business-analyst/skills/team-composition-analysis) | MIT |
| Study Guide from Notes | [document/study-notes-synthesizer](document/study-notes-synthesizer) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-students/skills/study-notes-synthesizer) | MIT |
| Terms of Service and Privacy Notice Drafter | [document/terms-of-service-and-privacy-notice](document/terms-of-service-and-privacy-notice) | [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice/tree/f6c2358c133d294f02827f9a57a5394c6ecdb941/skills/recommended/terms-of-service) | Apache-2.0 |
| Thesis Chapter Builder | [document/thesis-chapter](document/thesis-chapter) | Written for EverAsk | — |
| Wedding Speech and Toast Writer | [document/wedding-speech](document/wedding-speech) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/plugins/pm-lifeadmin/skills/wedding-speech) | MIT |
| Worksheet and Answer Key Maker | [document/worksheet-maker](document/worksheet-maker) | Written for EverAsk | — |

### Slides (4)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Document to Slides | [slides/document-to-slides](slides/document-to-slides) | Written for EverAsk | — |
| Lecture and Lesson Slides | [slides/lecture-slides](slides/lecture-slides) | Written for EverAsk | — |
| Pitch Deck Builder | [slides/pitch-deck](slides/pitch-deck) | Written for EverAsk | — |
| Quarterly Business Review Deck | [slides/quarterly-business-review](slides/quarterly-business-review) | Written for EverAsk | — |

### Email (11)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Cold Email Writer | [email/cold-email](email/cold-email) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/cold-email) | MIT |
| Customer Reply Writer | [email/draft-response](email/draft-response) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/customer-support/skills/draft-response) | Apache-2.0 |
| Email Deliverability Check | [email/cold-email-deliverability-check](email/cold-email-deliverability-check) | [mbfinotti/sales-skills](https://github.com/mbfinotti/sales-skills/tree/b2ed3628695e523919af440eab77648e16c5eea8/skills/cold-email-deliverability) | MIT |
| Email Sequence Builder | [email/email-sequence](email/email-sequence) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/email-sequence) | Apache-2.0 |
| Email Subject Line Generator and Tester | [email/email-subject-line-tester](email/email-subject-line-tester) | [mbfinotti/sales-skills](https://github.com/mbfinotti/sales-skills/tree/b2ed3628695e523919af440eab77648e16c5eea8/skills/cold-email-subject-line-tester) | MIT |
| Inbox Triage and Replies | [email/inbox-manager](email/inbox-manager) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/inbox-manager) | Apache-2.0 |
| Meeting Follow-Ups | [email/meeting-follow-up-pipeline](email/meeting-follow-up-pipeline) | [zapier/wade-skills](https://github.com/zapier/wade-skills/tree/b7b86e78ae2e1235bebac8668edd834b34176c19/skills/meeting-follow-up-pipeline) | MIT |
| Objection Handler | [email/handle-objection](email/handle-objection) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/sales/skills/handle-objection) | Apache-2.0 |
| Overdue Invoice Chaser | [email/invoice-chase](email/invoice-chase) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/invoice-chase) | Apache-2.0 |
| Support Ticket Triage | [email/ticket-triage](email/ticket-triage) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/customer-support/skills/ticket-triage) | Apache-2.0 |
| Suspicious Email Analyzer | [email/suspicious-email](email/suspicious-email) | [claude-office-skills/skills](https://github.com/claude-office-skills/skills/tree/9c4c7d5cd2813a8936bf2c9fdb174ea883b85a11/suspicious-email) | MIT |

### Data (34)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| A/B Test and Stats Checker | [data/statistical-analyst](data/statistical-analyst) | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/e4a1dc3695908dd5a6c811cc76ab7aa4cf95f2f0/engineering/statistical-analyst/skills/statistical-analyst) | MIT |
| Account Reconciliation | [data/reconciliation](data/reconciliation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/reconciliation) | Apache-2.0 |
| Analysis QA Check | [data/validate-data](data/validate-data) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/validate-data) | Apache-2.0 |
| Break-Even Analysis | [data/break-even-analysis](data/break-even-analysis) | [openaccountant/skills](https://github.com/openaccountant/skills/tree/f5abe381f24b5b7d59f1d0b4a825b14494ff2034/business/break-even-calc) | MIT |
| Budget vs Actual Variance Analysis | [data/variance-analysis](data/variance-analysis) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/variance-analysis) | Apache-2.0 |
| Cash Flow Snapshot | [data/cash-flow-snapshot](data/cash-flow-snapshot) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/cash-flow-snapshot) | Apache-2.0 |
| Cohort Retention Analysis | [data/cohort-retention-analysis](data/cohort-retention-analysis) | [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills/tree/9449d363e1ae43cf1706c73bebc16774e339c427/03-data-analysis-investigation/cohort-analysis) | MIT |
| Contract Terms Table | [data/commercial-agreement-tabular-review](data/commercial-agreement-tabular-review) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/tabular-review-workflows/commercial-agreement-tabular-review) | MIT |
| Customer Segmentation (RFM and Clusters) | [data/customer-segmentation](data/customer-segmentation) | [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills/tree/9449d363e1ae43cf1706c73bebc16774e339c427/03-data-analysis-investigation/segmentation-analysis) | MIT |
| Dataset Profiler | [data/explore-data](data/explore-data) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/explore-data) | Apache-2.0 |
| DCF Valuation Model | [data/dcf-valuation](data/dcf-valuation) | [claude-office-skills/skills](https://github.com/claude-office-skills/skills/tree/9c4c7d5cd2813a8936bf2c9fdb174ea883b85a11/dcf-valuation) | MIT |
| Debt Payoff Planner | [data/debt-payoff-plan](data/debt-payoff-plan) | [openaccountant/skills](https://github.com/openaccountant/skills/tree/f5abe381f24b5b7d59f1d0b4a825b14494ff2034/personal/debt-payoff) | MIT |
| Exit Waterfall and Cap Table Payouts | [data/exit-waterfall-cap-table](data/exit-waterfall-cap-table) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/skills/exit-waterfall) | MIT |
| Freelance Rate Calculator | [data/freelance-rate-calculator](data/freelance-rate-calculator) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/skills/freelance-rate) | MIT |
| Funnel Drop-Off Analysis | [data/funnel-analysis](data/funnel-analysis) | [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills/tree/9449d363e1ae43cf1706c73bebc16774e339c427/03-data-analysis-investigation/funnel-analysis) | MIT |
| Journal Entry Prep | [data/journal-entry](data/journal-entry) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/journal-entry) | Apache-2.0 |
| Metric Drop Root-Cause Finder | [data/metric-drop-root-cause](data/metric-drop-root-cause) | [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills/tree/9449d363e1ae43cf1706c73bebc16774e339c427/03-data-analysis-investigation/root-cause-investigation) | MIT |
| P&L and Financial Statements | [data/financial-statements](data/financial-statements) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/financial-statements) | Apache-2.0 |
| PDF to Spreadsheet | [data/pdf-to-spreadsheet](data/pdf-to-spreadsheet) | Written for EverAsk | — |
| Personal Budget Planner | [data/personal-budget-planner](data/personal-budget-planner) | [gajetoso/financeskills](https://github.com/gajetoso/financeskills/tree/8f8582432b3a9759e7100ce15533d2367c5566a4/skills/personal-budgeting) | MIT |
| Receivables Aging Report | [data/accounts-receivable-aging](data/accounts-receivable-aging) | [openaccountant/skills](https://github.com/openaccountant/skills/tree/f5abe381f24b5b7d59f1d0b4a825b14494ff2034/business/invoice-aging) | MIT |
| Rent vs Buy Calculator | [data/rent-vs-buy-calculator](data/rent-vs-buy-calculator) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/skills/rent-vs-buy) | MIT |
| Reorder Planner | [data/inventory-planner](data/inventory-planner) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/inventory-planner) | Apache-2.0 |
| Report from Data | [data/report-from-data](data/report-from-data) | Written for EverAsk | — |
| Risk Register Builder | [data/risk-register-builder](data/risk-register-builder) | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills/tree/c4679f94f2566c675e63b1ecece104190943d842/skills/risk-register) | MIT |
| Small Business Tracker Workbook | [data/business-tracker](data/business-tracker) | Written for EverAsk | — |
| Spreadsheet Data Cleaner | [data/spreadsheet-data-cleaner](data/spreadsheet-data-cleaner) | [anthropics/financial-services](https://github.com/anthropics/financial-services/tree/3e32c2287dcb637c184c01cc0ad82d6af7e9bb0f/plugins/vertical-plugins/financial-analysis/skills/clean-data-xls) | Apache-2.0 |
| Spreadsheet Formula Auditor | [data/spreadsheet-formula-auditor](data/spreadsheet-formula-auditor) | [anthropics/financial-services](https://github.com/anthropics/financial-services/tree/3e32c2287dcb637c184c01cc0ad82d6af7e9bb0f/plugins/agent-plugins/earnings-reviewer/skills/audit-xls) | Apache-2.0 |
| Spreadsheet Merge and Compare | [data/spreadsheet-merge-compare](data/spreadsheet-merge-compare) | Written for EverAsk | — |
| SQL Query Writer | [data/sql-queries](data/sql-queries) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/sql-queries) | Apache-2.0 |
| Startup Financial Model | [data/startup-financial-model](data/startup-financial-model) | [wshobson/agents](https://github.com/wshobson/agents/tree/9c61ab243def98f72da12abd41cfcf5bcd91af9d/plugins/startup-business-analyst/skills/startup-financial-modeling) | MIT |
| Survey Results Analysis | [data/survey-results-analysis](data/survey-results-analysis) | [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills/tree/3456e5e309f38ac2a66943f20d4aaf8031268dfb/skills/measure-survey-analysis) | Apache-2.0 |
| Trend, Seasonality and Forecast | [data/time-series-forecasting](data/time-series-forecasting) | [nimrodfisher/data-analytics-skills](https://github.com/nimrodfisher/data-analytics-skills/tree/9449d363e1ae43cf1706c73bebc16774e339c427/03-data-analysis-investigation/time-series-analysis) | MIT |
| Working Capital and Cash Cycle | [data/working-capital-cash-cycle](data/working-capital-cash-cycle) | [gajetoso/financeskills](https://github.com/gajetoso/financeskills/tree/8f8582432b3a9759e7100ce15533d2367c5566a4/skills/working-capital-analysis) | MIT |

### Engineering (16)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| API Documentation Writer | [engineering/api-documentation-writer](engineering/api-documentation-writer) | [onewave-ai/claude-skills](https://github.com/onewave-ai/claude-skills/tree/b2267d9171af4f56848d82992381b20b89b44056/api-documentation-writer) | MIT |
| Bug Report and Ticket Writer | [engineering/ticket-authoring](engineering/ticket-authoring) | [rampstackco/claude-skills](https://github.com/rampstackco/claude-skills/tree/9d281db6e7a5c4a0084ba89c91633a07f5f7e42b/skills/ticket-authoring) | MIT |
| Changelog and Release Notes Writer | [engineering/changelog-writing](engineering/changelog-writing) | [samber/developer-relations-skills](https://github.com/samber/developer-relations-skills/tree/c3a1b6912791539567727723baf626b4fec5ac7a/skills/changelog-writing) | MIT |
| Code Reviewer | [engineering/code-reviewer](engineering/code-reviewer) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/078a25cc5bfd8011459be7b91d004e900c1d02d3/skills/code-reviewer) | MIT |
| Database Schema Designer | [engineering/database-schema-designer](engineering/database-schema-designer) | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/3027f20f3181758385a1bb8c022d4041dfb4de84/skills/database-schema-designer) | MIT |
| Debug From Error or Stack Trace | [engineering/debugging-wizard](engineering/debugging-wizard) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/67c1961b180dc92cf08983344627109e983e8f51/skills/debugging-wizard) | MIT |
| Google Sheets Automation Script Writer | [engineering/google-apps-script](engineering/google-apps-script) | [jezweb/claude-skills](https://github.com/jezweb/claude-skills/tree/1260fa7439b36b18dbf16648ccc7fb44783f6c23/plugins/integrations/skills/google-apps-script) | MIT |
| Incident Response and Postmortem | [engineering/incident-response](engineering/incident-response) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/engineering/skills/incident-response) | Apache-2.0 |
| OpenAPI Spec Writer | [engineering/openapi-spec-generation](engineering/openapi-spec-generation) | [wshobson/agents](https://github.com/wshobson/agents/tree/9c61ab243def98f72da12abd41cfcf5bcd91af9d/plugins/documentation-generation/skills/openapi-spec-generation) | MIT |
| Prompt Engineer | [engineering/prompt-engineer](engineering/prompt-engineer) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/078a25cc5bfd8011459be7b91d004e900c1d02d3/skills/prompt-engineer) | MIT |
| README Writer | [engineering/crafting-effective-readmes](engineering/crafting-effective-readmes) | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/3027f20f3181758385a1bb8c022d4041dfb4de84/skills/crafting-effective-readmes) | MIT |
| Regex Builder and Explainer | [engineering/regex-debugger](engineering/regex-debugger) | [onewave-ai/claude-skills](https://github.com/onewave-ai/claude-skills/tree/b2267d9171af4f56848d82992381b20b89b44056/regex-debugger) | MIT |
| SQL Code Review | [engineering/sql-code-review](engineering/sql-code-review) | [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/a06ba06d11f41b996f8c246e2a452e1bf3a17950/skills/sql-code-review) | MIT |
| System Design and ADR Writer | [engineering/architecture-designer](engineering/architecture-designer) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/67c1961b180dc92cf08983344627109e983e8f51/skills/architecture-designer) | MIT |
| Test Plan and Test Case Writer | [engineering/test-case-authoring](engineering/test-case-authoring) | [rampstackco/claude-skills](https://github.com/rampstackco/claude-skills/tree/9d281db6e7a5c4a0084ba89c91633a07f5f7e42b/skills/test-case-authoring) | MIT |
| Workflow Automation Designer | [engineering/workflow-automator](engineering/workflow-automator) | [onewave-ai/claude-skills](https://github.com/onewave-ai/claude-skills/tree/b2267d9171af4f56848d82992381b20b89b44056/workflow-automator) | MIT |

### Marketing (43)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Ad Copy Generator | [marketing/ad-creative](marketing/ad-creative) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/ad-creative) | MIT |
| AI Image Prompt Writer | [marketing/ai-image-prompts](marketing/ai-image-prompts) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| AI Search Visibility (GEO) | [marketing/ai-seo](marketing/ai-seo) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/ai-seo) | MIT |
| AI Video Prompt Writer | [marketing/ai-video-prompts](marketing/ai-video-prompts) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Amazon Listing Writer and Optimizer | [marketing/amazon-listing-writer](marketing/amazon-listing-writer) | [nexscope-ai/amazon-skills](https://github.com/nexscope-ai/amazon-skills/tree/2bcb8cb019cfac6a1e420b11f86209df5ea47686/amazon-listing-optimization) | MIT |
| Brand and Product Naming | [marketing/brand-naming](marketing/brand-naming) | [arnabbagxd/brand-building-skills](https://github.com/arnabbagxd/brand-building-skills/tree/4a0a8b5b7a0f64bf0fc551978a18a591670a5223/skills/brand-naming) | MIT |
| Brand Message Clarifier | [marketing/brand-messaging](marketing/brand-messaging) | [wondelai/skills](https://github.com/wondelai/skills/tree/c172996495bed0fcd26896a9416b2093fd7073f0/storybrand-messaging) | MIT |
| Brand Voice Guide Builder | [marketing/guideline-generation](marketing/guideline-generation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/partner-built/brand-voice/skills/guideline-generation) | MIT |
| Churn Prevention | [marketing/churn-prevention](marketing/churn-prevention) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/churn-prevention) | MIT |
| Comparison & Alternative Pages | [marketing/competitors](marketing/competitors) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/competitors) | MIT |
| Content Repurposer | [marketing/content-repurposer](marketing/content-repurposer) | [blacktwist/social-media-skills](https://github.com/blacktwist/social-media-skills/tree/4f85b07069983b3b0b9bbe6519fed7017edcce81/skills/content-repurposer-sms) | MIT |
| Content Strategy Planner | [marketing/content-strategy](marketing/content-strategy) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/content-strategy) | MIT |
| Customer Case Study Builder | [marketing/case-study-builder](marketing/case-study-builder) | [brianrwagner/ai-marketing](https://github.com/brianrwagner/ai-marketing/tree/4925f84454348cb756d979d30239b0db967d239c/case-study-builder) | MIT |
| Discovery Call Question Planner | [marketing/discovery-call-questions](marketing/discovery-call-questions) | [mbfinotti/sales-skills](https://github.com/mbfinotti/sales-skills/tree/b2ed3628695e523919af440eab77648e16c5eea8/skills/sales-discovery-questions) | MIT |
| Influencer Campaign Brief | [marketing/influencer-campaign-brief](marketing/influencer-campaign-brief) | [mbfinotti/partnerships-skills](https://github.com/mbfinotti/partnerships-skills/tree/5764ab1dae47cdf00598c0abfcdb64c03c3c4560/skills/influencer-campaign-brief) | MIT |
| Lead Qualifier | [marketing/lead-triage](marketing/lead-triage) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/sales/skills/lead-triage) | Apache-2.0 |
| Long Video to Social Clips | [marketing/long-video-to-clips](marketing/long-video-to-clips) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Marketing Copywriter | [marketing/copywriting](marketing/copywriting) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/copywriting) | MIT |
| Marketing Plan Builder | [marketing/marketing-plan](marketing/marketing-plan) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/marketing-plan) | MIT |
| Multichannel Content Writer | [marketing/content-creation](marketing/content-creation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/content-creation) | Apache-2.0 |
| Music and Soundtrack Maker | [marketing/soundtrack](marketing/soundtrack) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| Newsletter Issue Writer (Substack) | [marketing/substack-newsletter-writer](marketing/substack-newsletter-writer) | [samber/cc-skills](https://github.com/samber/cc-skills/tree/50a33836b20f690c668af557bd9ef9d07a8c7ef2/skills/substack-ghostwriting) | MIT |
| Persuasion Audit | [marketing/influence-psychology](marketing/influence-psychology) | [wondelai/skills](https://github.com/wondelai/skills/tree/c172996495bed0fcd26896a9416b2093fd7073f0/influence-psychology) | MIT |
| Positioning & Messaging Doc | [marketing/product-marketing](marketing/product-marketing) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/product-marketing) | MIT |
| Press Release Writer | [marketing/press-release-writer](marketing/press-release-writer) | [samber/cc-skills](https://github.com/samber/cc-skills/tree/50a33836b20f690c668af557bd9ef9d07a8c7ef2/skills/press-release-writer) | MIT |
| Product Hunt Launch Plan | [marketing/product-hunt-launch-plan](marketing/product-hunt-launch-plan) | [ognjengt/founder-skills](https://github.com/ognjengt/founder-skills/tree/a45931cad934dc6243a68f905485467935a4ad9a/skills/product-hunt-launch-plan) | MIT |
| Programmatic SEO Planner | [marketing/programmatic-seo](marketing/programmatic-seo) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/programmatic-seo) | MIT |
| Referral Program Builder | [marketing/referrals](marketing/referrals) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/referrals) | MIT |
| Review Requests and Replies (Local Business) | [marketing/review-requests-and-replies](marketing/review-requests-and-replies) | [garrettjsmith/localseoskills](https://github.com/garrettjsmith/localseoskills/tree/c3b7a25b7d5cc370752d74cfea240ccf992a24db/skills/review-management) | MIT |
| RevOps Designer | [marketing/revops](marketing/revops) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/revops) | MIT |
| Sales Call Scorecard | [marketing/sales-call-review](marketing/sales-call-review) | [mbfinotti/sales-skills](https://github.com/mbfinotti/sales-skills/tree/b2ed3628695e523919af440eab77648e16c5eea8/skills/sales-call-review) | MIT |
| Sales Collateral Builder | [marketing/sales-enablement](marketing/sales-enablement) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/sales-enablement) | MIT |
| SEO Audit | [marketing/seo-audit](marketing/seo-audit) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/seo-audit) | MIT |
| Social Media Content | [marketing/social](marketing/social) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/social) | MIT |
| Songwriter | [marketing/songwriter](marketing/songwriter) | Written for EverAsk, from a skill bundled with the agent | — |
| Talking Avatar Video | [marketing/talking-avatar](marketing/talking-avatar) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| Topic Cluster Builder | [marketing/build-clusters](marketing/build-clusters) | [calm-north/seojuice-skills](https://github.com/calm-north/seojuice-skills/tree/c1f633bea512365ba04477076369e418ecc82ffd/skills/build-clusters) | MIT |
| UGC and Short-Form Video Ad Scripts | [marketing/ugc-video-ad-scripts](marketing/ugc-video-ad-scripts) | [mbfinotti/advertising-skills](https://github.com/mbfinotti/advertising-skills/tree/ab1eb51a249978c9b7bd24b3d589c713a6198fd3/skills/ugc-ad-scripts) | MIT |
| Video Breakdown and Remix | [marketing/video-breakdown-remix](marketing/video-breakdown-remix) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Video Script and Shot List | [marketing/video-script](marketing/video-script) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Video Subtitles and Translations | [marketing/video-subtitles](marketing/video-subtitles) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Voiceover Producer | [marketing/voiceover](marketing/voiceover) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| YouTube Publish Pack | [marketing/youtube-publish-pack](marketing/youtube-publish-pack) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |

### Research (24)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Academic Paper Review | [research/academic-paper-review](research/academic-paper-review) | [bytedance/deer-flow](https://github.com/bytedance/deer-flow/tree/3751eb8daf491324e728f63bcc773e0f081eb7e5/skills/public/academic-paper-review) | MIT |
| Argument Map | [research/argument-map](research/argument-map) | [product-on-purpose/thinking-framework-skills](https://github.com/product-on-purpose/thinking-framework-skills/tree/6ab95db2d6469e4b65f3eb3ed265e46a6a1e69a8/skills/think-argument-mapping) | Apache-2.0 |
| Article Quality Audit (E-E-A-T) | [research/seo-content-audit](research/seo-content-audit) | [seranking/seo-skills](https://github.com/seranking/seo-skills/tree/fd6d1408f2e6a06454d81c07c29e0f04342eb9ba/skills/seo-content-audit) | MIT |
| arXiv Paper Finder | [research/paper-finder](research/paper-finder) | Written for EverAsk, from a skill bundled with the agent | — |
| Catch-Up Digest | [research/activity-digest](research/activity-digest) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/enterprise-search/skills/digest) | Apache-2.0 |
| Citation and Reference Checker | [research/citation-checker](research/citation-checker) | [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer/tree/9820740d252800ecf0b8fc066ffb5bf9659f4a51/skills/citation-management) | MIT |
| Competitor Brief and Battlecard | [research/competitive-brief](research/competitive-brief) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/competitive-brief) | Apache-2.0 |
| Critical Appraisal of Research Evidence | [research/critical-appraisal-evidence-review](research/critical-appraisal-evidence-review) | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/ec59a29a03d5c40f73ab40878df04860bc00e876/skills/scientific-critical-thinking) | MIT |
| Due Diligence Checklist Builder | [research/due-diligence-checklist](research/due-diligence-checklist) | [anthropics/financial-services](https://github.com/anthropics/financial-services/tree/3e32c2287dcb637c184c01cc0ad82d6af7e9bb0f/plugins/vertical-plugins/private-equity/skills/dd-checklist) | Apache-2.0 |
| Fact Checker | [research/blog-factcheck](research/blog-factcheck) | [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog/tree/354442348815a7f0327077ad89af2c43cf4b4ab4/skills/blog-factcheck) | MIT |
| Job Search | [research/job-search](research/job-search) | Written for EverAsk, from a skill bundled with the agent | — |
| Jobs To Be Done Canvas | [research/jtbd-canvas](research/jtbd-canvas) | [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills/tree/3456e5e309f38ac2a66943f20d4aaf8031268dfb/skills/define-jtbd-canvas) | Apache-2.0 |
| Literature Review and Annotated Bibliography | [research/literature-review-synthesis](research/literature-review-synthesis) | [bytedance/deer-flow](https://github.com/bytedance/deer-flow/tree/3751eb8daf491324e728f63bcc773e0f081eb7e5/skills/public/systematic-literature-review) | MIT |
| Market Sizing (TAM, SAM, SOM) | [research/market-sizing-analysis](research/market-sizing-analysis) | [wshobson/agents](https://github.com/wshobson/agents/tree/7e2fb559cf4b824b27f1fec49fe88f7511066d26/plugins/startup-business-analyst/skills/market-sizing-analysis) | MIT |
| Patent and Prior Art Search | [research/prior-art-search](research/prior-art-search) | [wanshuiyin/auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/auto-claude-code-research-in-sleep/tree/9f30e834d24a337dbdd06fb20a1150d4376dfa59/skills/prior-art-search) | MIT |
| Prospect Research Brief | [research/account-research](research/account-research) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/sales/skills/account-research) | Apache-2.0 |
| Reddit Opportunity Finder | [research/reddit-opportunity-research](research/reddit-opportunity-research) | [onvoyage-ai/gtm-engineer-skills](https://github.com/onvoyage-ai/gtm-engineer-skills/tree/cfdb9edd84109077153fa7faf776eb35f6c04370/reddit-opportunity-research) | MIT |
| Scenario Planning | [research/scenario-planning](research/scenario-planning) | [product-on-purpose/thinking-framework-skills](https://github.com/product-on-purpose/thinking-framework-skills/tree/6ab95db2d6469e4b65f3eb3ed265e46a6a1e69a8/skills/think-scenario-planning) | Apache-2.0 |
| Search Across Your Apps | [research/enterprise-search](research/enterprise-search) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/enterprise-search/skills/search) | Apache-2.0 |
| Statistics Reporting Audit | [research/statistics-reporting-audit](research/statistics-reporting-audit) | [yuan1z0825/nature-skills](https://github.com/yuan1z0825/nature-skills/tree/14ca69710cae192325395a380e9cdd4ae5d9d0c8/skills/nature-statistics) | Apache-2.0 |
| Survey and Questionnaire Designer | [research/survey-questionnaire-designer](research/survey-questionnaire-designer) | [owl-listener/designer-skills](https://github.com/owl-listener/designer-skills/tree/9a6930cf84a822eb458624bd11c61aac5bbdf224/design-research/skills/survey-design) | MIT |
| SWOT Analysis (Evidence-Checked) | [research/swot-analysis](research/swot-analysis) | [product-on-purpose/thinking-framework-skills](https://github.com/product-on-purpose/thinking-framework-skills/tree/6ab95db2d6469e4b65f3eb3ed265e46a6a1e69a8/skills/think-swot) | Apache-2.0 |
| User Research Synthesizer | [research/synthesize-research](research/synthesize-research) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/product-management/skills/synthesize-research) | Apache-2.0 |
| Win-Loss and Churn Analysis | [research/win-loss-analysis](research/win-loss-analysis) | [thecraighewitt/skills](https://github.com/thecraighewitt/skills/tree/fdbf39b61fbc8cb7cea67949bfb5e8fc567bbc51/sales/win-loss-analysis) | MIT |

### Website (12)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Accessibility Audit (WCAG AA) | [website/accessibility-review](website/accessibility-review) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/design/skills/accessibility-review) | Apache-2.0 |
| Brand Colour Palette Generator | [website/brand-color-palette](website/brand-color-palette) | [jezweb/claude-skills](https://github.com/jezweb/claude-skills/tree/1260fa7439b36b18dbf16648ccc7fb44783f6c23/plugins/design-assets/skills/color-palette) | MIT |
| Generative Art Studio | [website/algorithmic-art](website/algorithmic-art) | [anthropics/skills](https://github.com/anthropics/skills/tree/ca45fc496a3436251f191354091d557da31c15b5/skills/algorithmic-art) | Apache-2.0 |
| Interactive Calculator Designer | [website/calculator-design](website/calculator-design) | [rampstackco/claude-skills](https://github.com/rampstackco/claude-skills/tree/9d281db6e7a5c4a0084ba89c91633a07f5f7e42b/skills/calculator-design) | MIT |
| Landing Page CRO Review | [website/cro](website/cro) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/cro) | MIT |
| Local Business SEO Pack | [website/local-business-seo-pack](website/local-business-seo-pack) | [jezweb/claude-skills](https://github.com/jezweb/claude-skills/tree/1260fa7439b36b18dbf16648ccc7fb44783f6c23/plugins/web-design/skills/seo-local-business) | MIT |
| Site Migration and Redirect Map Planner | [website/site-migration-redirect-plan](website/site-migration-redirect-plan) | [rampstackco/claude-skills](https://github.com/rampstackco/claude-skills/tree/9d281db6e7a5c4a0084ba89c91633a07f5f7e42b/skills/content-migration) | MIT |
| Swarm Rebuild Video | [website/swarm-rebuild](website/swarm-rebuild) | Written for EverAsk; `scripts/swarm.js` is from [DhvanilPatel/swarm-cursors](https://github.com/DhvanilPatel/swarm-cursors/tree/3d49e0ac96172eb6af7ae8229b2152121bed2092/swarm-rebuild) | None yet |
| UX Microcopy Writer | [website/ux-copy](website/ux-copy) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/design/skills/ux-copy) | Apache-2.0 |
| Web Form Designer and Auditor | [website/web-form-design](website/web-form-design) | [rampstackco/claude-skills](https://github.com/rampstackco/claude-skills/tree/9d281db6e7a5c4a0084ba89c91633a07f5f7e42b/skills/form-strategy) | MIT |
| Website Localisation Plan | [website/website-i18n-plan](website/website-i18n-plan) | [rampstackco/claude-skills](https://github.com/rampstackco/claude-skills/tree/9d281db6e7a5c4a0084ba89c91633a07f5f7e42b/skills/internationalization) | MIT |
| Website Structure Planner | [website/site-architecture](website/site-architecture) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/site-architecture) | MIT |
