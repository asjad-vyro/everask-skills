# EverAsk Skills

The 99 skills for the EverAsk Skills Library. Each skill is a folder with a `SKILL.md` at its top.

- 58 are copied unchanged from open-source repos at pinned commits, except for the `name` in `SKILL.md`, which is set to the Library card title. The tables below link each one's source and give its licence.
- The 3 slides skills are our own. They plan the deck, then build it with EverAsk's built-in slide maker.
- The 10 video, voice, music and image skills in Marketing are our own too. They run on EverAsk's own tools (`media_analyze`, `audio_transcribe`, `audio_generate`, `music_generate`, `image_generate`, `video_generate`, and ffmpeg in the sandbox) and use ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b)'s video production notes and provider guides; none of its text is copied.
- Swarm Rebuild Video in Website is our own `SKILL.md` and recorder around the page script of [Swarm Rebuild](https://github.com/DhvanilPatel/swarm-cursors/tree/3d49e0ac96172eb6af7ae8229b2152121bed2092), a tribute to Joel Califa's [Swarm](https://califa.github.io/swarm-site/). Its `scripts/swarm.js` is copied unchanged. That project has no licence yet and asks that its code not be reused without checking with its author and Joel Califa.
- 27 more (added November 2026) are adapted for EverAsk rather than copied: rewritten as numbered steps for its agent, with other products' machinery and promotion removed, connectors made optional, and each one tested end to end. 24 come from the open-source repos linked in the tables; Job Search, arXiv Paper Finder and Songwriter are our own, rebuilt from skills bundled with the agent.

Each folder also has two files of our own: a `skill.config.json`, with the skill's Library type, example prompts and connector badges, and a `cover.webp` for its Library card.

## Import

One import gives every skill the same type, so import each type folder with its own link and pick the matching type:

| Type | Link | Skills |
|---|---|---|
| Document | https://github.com/asjad-vyro/everask-skills/tree/main/document | 23 |
| Slides | https://github.com/asjad-vyro/everask-skills/tree/main/slides | 3 |
| Email | https://github.com/asjad-vyro/everask-skills/tree/main/email | 9 |
| Data | https://github.com/asjad-vyro/everask-skills/tree/main/data | 12 |
| Engineering | https://github.com/asjad-vyro/everask-skills/tree/main/engineering | 4 |
| Marketing | https://github.com/asjad-vyro/everask-skills/tree/main/marketing | 31 |
| Research | https://github.com/asjad-vyro/everask-skills/tree/main/research | 11 |
| Website | https://github.com/asjad-vyro/everask-skills/tree/main/website | 6 |

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

### Document (23)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Academic Writing Coach | [document/research-writing](document/research-writing) | [zLanqing/codex-claude-academic-skills](https://github.com/zLanqing/codex-claude-academic-skills/tree/7ed6377f0efb6a38951b48ef03b19d996e454b1f/research-writing-skill) | MIT |
| Business Model Canvas | [document/business-model](document/business-model) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-product-strategy/skills/business-model) | MIT |
| Compliance Check | [document/compliance-check](document/compliance-check) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/legal/skills/compliance-check) | Apache-2.0 |
| Cover Letter Writer | [document/cover-letter-generator](document/cover-letter-generator) | [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills/tree/74ae19e7c62b0516d1c298328e5544976c12da5d/skills/cover-letter-generator) | MIT |
| Customer Interview Script | [document/interview-script](document/interview-script) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-product-discovery/skills/interview-script) | MIT |
| Document Comparison | [document/compare-documents](document/compare-documents) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/assistant-workflows/compare-documents) | MIT |
| Document Proofreader | [document/proofread](document/proofread) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/assistant-workflows/proofread) | MIT |
| Grammar and Flow Check | [document/grammar-check](document/grammar-check) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-toolkit/skills/grammar-check) | MIT |
| Hiring Packet Builder | [document/job-post-builder](document/job-post-builder) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/job-post-builder) | Apache-2.0 |
| Interview Prep | [document/interview-prep-generator](document/interview-prep-generator) | [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills/tree/74ae19e7c62b0516d1c298328e5544976c12da5d/skills/interview-prep-generator) | MIT |
| Meeting Brief | [document/meeting-briefing](document/meeting-briefing) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/legal/skills/meeting-briefing) | Apache-2.0 |
| Meeting Minutes | [document/meeting-minutes](document/meeting-minutes) | [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/61fa1fa8fcc63d6dbd2f07a75aeb8e214df5acfb/skills/meeting-minutes) | MIT |
| Notion Knowledge Capture | [document/notion-knowledge-capture](document/notion-knowledge-capture) | [openai/skills](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/notion-knowledge-capture) | MIT |
| Performance Review Writer | [document/performance-review](document/performance-review) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/human-resources/skills/performance-review) | Apache-2.0 |
| PRD Writer | [document/create-prd](document/create-prd) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-execution/skills/create-prd) | MIT |
| Pricing Strategy | [document/pricing](document/pricing) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/pricing) | MIT |
| Proposal and Quote Builder | [document/proposal-builder](document/proposal-builder) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/proposal-builder) | Apache-2.0 |
| Public Speaking Coach | [document/public-speaking](document/public-speaking) | [RefoundAI/lenny-skills](https://github.com/RefoundAI/lenny-skills/tree/13598cc54e09399bc1bc1398b0fca284110efb2f/skills/public-speaking) | MIT |
| RFP Responder | [document/rfp-responder](document/rfp-responder) | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/e4a1dc3695908dd5a6c811cc76ab7aa4cf95f2f0/commercial/skills/rfp-responder) | MIT |
| SEO Content Brief | [document/seo-content-brief](document/seo-content-brief) | [calm-north/seojuice-skills](https://github.com/calm-north/seojuice-skills/tree/c1f633bea512365ba04477076369e418ecc82ffd/skills/brief) | MIT |
| SOP and Process Writer | [document/process-doc](document/process-doc) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/operations/skills/process-doc) | Apache-2.0 |
| Stakeholder Update Writer | [document/stakeholder-update](document/stakeholder-update) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/product-management/skills/stakeholder-update) | Apache-2.0 |
| Startup Team Planner | [document/team-composition-analysis](document/team-composition-analysis) | [wshobson/agents](https://github.com/wshobson/agents/tree/7e2fb559cf4b824b27f1fec49fe88f7511066d26/plugins/startup-business-analyst/skills/team-composition-analysis) | MIT |

### Slides (3)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Lecture and Lesson Slides | [slides/lecture-slides](slides/lecture-slides) | Written for EverAsk | — |
| Pitch Deck Builder | [slides/pitch-deck](slides/pitch-deck) | Written for EverAsk | — |
| Quarterly Business Review Deck | [slides/quarterly-business-review](slides/quarterly-business-review) | Written for EverAsk | — |

### Email (9)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Cold Email Writer | [email/cold-email](email/cold-email) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/cold-email) | MIT |
| Customer Reply Writer | [email/draft-response](email/draft-response) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/customer-support/skills/draft-response) | Apache-2.0 |
| Email Sequence Builder | [email/email-sequence](email/email-sequence) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/email-sequence) | Apache-2.0 |
| Inbox Triage and Replies | [email/inbox-manager](email/inbox-manager) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/inbox-manager) | Apache-2.0 |
| Meeting Follow-Ups | [email/meeting-follow-up-pipeline](email/meeting-follow-up-pipeline) | [zapier/wade-skills](https://github.com/zapier/wade-skills/tree/b7b86e78ae2e1235bebac8668edd834b34176c19/skills/meeting-follow-up-pipeline) | MIT |
| Objection Handler | [email/handle-objection](email/handle-objection) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/sales/skills/handle-objection) | Apache-2.0 |
| Overdue Invoice Chaser | [email/invoice-chase](email/invoice-chase) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/invoice-chase) | Apache-2.0 |
| Support Ticket Triage | [email/ticket-triage](email/ticket-triage) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/customer-support/skills/ticket-triage) | Apache-2.0 |
| Suspicious Email Analyzer | [email/suspicious-email](email/suspicious-email) | [claude-office-skills/skills](https://github.com/claude-office-skills/skills/tree/9c4c7d5cd2813a8936bf2c9fdb174ea883b85a11/suspicious-email) | MIT |

### Data (12)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| A/B Test and Stats Checker | [data/statistical-analyst](data/statistical-analyst) | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/e4a1dc3695908dd5a6c811cc76ab7aa4cf95f2f0/engineering/statistical-analyst/skills/statistical-analyst) | MIT |
| Account Reconciliation | [data/reconciliation](data/reconciliation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/reconciliation) | Apache-2.0 |
| Analysis QA Check | [data/validate-data](data/validate-data) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/validate-data) | Apache-2.0 |
| Budget vs Actual Variance Analysis | [data/variance-analysis](data/variance-analysis) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/variance-analysis) | Apache-2.0 |
| Cash Flow Snapshot | [data/cash-flow-snapshot](data/cash-flow-snapshot) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/cash-flow-snapshot) | Apache-2.0 |
| Contract Terms Table | [data/commercial-agreement-tabular-review](data/commercial-agreement-tabular-review) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/tabular-review-workflows/commercial-agreement-tabular-review) | MIT |
| Dataset Profiler | [data/explore-data](data/explore-data) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/explore-data) | Apache-2.0 |
| DCF Valuation Model | [data/dcf-valuation](data/dcf-valuation) | [claude-office-skills/skills](https://github.com/claude-office-skills/skills/tree/9c4c7d5cd2813a8936bf2c9fdb174ea883b85a11/dcf-valuation) | MIT |
| Journal Entry Prep | [data/journal-entry](data/journal-entry) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/journal-entry) | Apache-2.0 |
| P&L and Financial Statements | [data/financial-statements](data/financial-statements) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/financial-statements) | Apache-2.0 |
| Reorder Planner | [data/inventory-planner](data/inventory-planner) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/inventory-planner) | Apache-2.0 |
| SQL Query Writer | [data/sql-queries](data/sql-queries) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/sql-queries) | Apache-2.0 |

### Engineering (4)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Code Reviewer | [engineering/code-reviewer](engineering/code-reviewer) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/078a25cc5bfd8011459be7b91d004e900c1d02d3/skills/code-reviewer) | MIT |
| Incident Response and Postmortem | [engineering/incident-response](engineering/incident-response) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/engineering/skills/incident-response) | Apache-2.0 |
| Prompt Engineer | [engineering/prompt-engineer](engineering/prompt-engineer) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/078a25cc5bfd8011459be7b91d004e900c1d02d3/skills/prompt-engineer) | MIT |
| README Writer | [engineering/crafting-effective-readmes](engineering/crafting-effective-readmes) | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/3027f20f3181758385a1bb8c022d4041dfb4de84/skills/crafting-effective-readmes) | MIT |

### Marketing (31)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Ad Copy Generator | [marketing/ad-creative](marketing/ad-creative) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/ad-creative) | MIT |
| AI Image Prompt Writer | [marketing/ai-image-prompts](marketing/ai-image-prompts) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| AI Search Visibility (GEO) | [marketing/ai-seo](marketing/ai-seo) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/ai-seo) | MIT |
| AI Video Prompt Writer | [marketing/ai-video-prompts](marketing/ai-video-prompts) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Brand Message Clarifier | [marketing/brand-messaging](marketing/brand-messaging) | [wondelai/skills](https://github.com/wondelai/skills/tree/c172996495bed0fcd26896a9416b2093fd7073f0/storybrand-messaging) | MIT |
| Brand Voice Guide Builder | [marketing/guideline-generation](marketing/guideline-generation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/partner-built/brand-voice/skills/guideline-generation) | MIT |
| Churn Prevention | [marketing/churn-prevention](marketing/churn-prevention) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/churn-prevention) | MIT |
| Comparison & Alternative Pages | [marketing/competitors](marketing/competitors) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/competitors) | MIT |
| Content Strategy Planner | [marketing/content-strategy](marketing/content-strategy) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/content-strategy) | MIT |
| Lead Qualifier | [marketing/lead-triage](marketing/lead-triage) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/sales/skills/lead-triage) | Apache-2.0 |
| Long Video to Social Clips | [marketing/long-video-to-clips](marketing/long-video-to-clips) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Marketing Copywriter | [marketing/copywriting](marketing/copywriting) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/copywriting) | MIT |
| Marketing Plan Builder | [marketing/marketing-plan](marketing/marketing-plan) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/marketing-plan) | MIT |
| Multichannel Content Writer | [marketing/content-creation](marketing/content-creation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/content-creation) | Apache-2.0 |
| Music and Soundtrack Maker | [marketing/soundtrack](marketing/soundtrack) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| Persuasion Audit | [marketing/influence-psychology](marketing/influence-psychology) | [wondelai/skills](https://github.com/wondelai/skills/tree/c172996495bed0fcd26896a9416b2093fd7073f0/influence-psychology) | MIT |
| Positioning & Messaging Doc | [marketing/product-marketing](marketing/product-marketing) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/product-marketing) | MIT |
| Programmatic SEO Planner | [marketing/programmatic-seo](marketing/programmatic-seo) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/programmatic-seo) | MIT |
| Referral Program Builder | [marketing/referrals](marketing/referrals) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/referrals) | MIT |
| RevOps Designer | [marketing/revops](marketing/revops) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/revops) | MIT |
| Sales Collateral Builder | [marketing/sales-enablement](marketing/sales-enablement) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/sales-enablement) | MIT |
| SEO Audit | [marketing/seo-audit](marketing/seo-audit) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/seo-audit) | MIT |
| Social Media Content | [marketing/social](marketing/social) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/social) | MIT |
| Songwriter | [marketing/songwriter](marketing/songwriter) | Written for EverAsk, from a skill bundled with the agent | — |
| Talking Avatar Video | [marketing/talking-avatar](marketing/talking-avatar) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| Topic Cluster Builder | [marketing/build-clusters](marketing/build-clusters) | [calm-north/seojuice-skills](https://github.com/calm-north/seojuice-skills/tree/c1f633bea512365ba04477076369e418ecc82ffd/skills/build-clusters) | MIT |
| Video Breakdown and Remix | [marketing/video-breakdown-remix](marketing/video-breakdown-remix) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Video Script and Shot List | [marketing/video-script](marketing/video-script) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Video Subtitles and Translations | [marketing/video-subtitles](marketing/video-subtitles) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |
| Voiceover Producer | [marketing/voiceover](marketing/voiceover) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/.agents/skills) | — |
| YouTube Publish Pack | [marketing/youtube-publish-pack](marketing/youtube-publish-pack) | Written for EverAsk, using ideas from [OpenMontage](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b/skills) | — |

### Research (11)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Article Quality Audit (E-E-A-T) | [research/seo-content-audit](research/seo-content-audit) | [seranking/seo-skills](https://github.com/seranking/seo-skills/tree/fd6d1408f2e6a06454d81c07c29e0f04342eb9ba/skills/seo-content-audit) | MIT |
| arXiv Paper Finder | [research/paper-finder](research/paper-finder) | Written for EverAsk, from a skill bundled with the agent | — |
| Catch-Up Digest | [research/activity-digest](research/activity-digest) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/enterprise-search/skills/digest) | Apache-2.0 |
| Competitor Brief and Battlecard | [research/competitive-brief](research/competitive-brief) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/competitive-brief) | Apache-2.0 |
| Fact Checker | [research/blog-factcheck](research/blog-factcheck) | [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog/tree/354442348815a7f0327077ad89af2c43cf4b4ab4/skills/blog-factcheck) | MIT |
| Job Search | [research/job-search](research/job-search) | Written for EverAsk, from a skill bundled with the agent | — |
| Market Sizing (TAM, SAM, SOM) | [research/market-sizing-analysis](research/market-sizing-analysis) | [wshobson/agents](https://github.com/wshobson/agents/tree/7e2fb559cf4b824b27f1fec49fe88f7511066d26/plugins/startup-business-analyst/skills/market-sizing-analysis) | MIT |
| Prospect Research Brief | [research/account-research](research/account-research) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/sales/skills/account-research) | Apache-2.0 |
| Reddit Opportunity Finder | [research/reddit-opportunity-research](research/reddit-opportunity-research) | [onvoyage-ai/gtm-engineer-skills](https://github.com/onvoyage-ai/gtm-engineer-skills/tree/cfdb9edd84109077153fa7faf776eb35f6c04370/reddit-opportunity-research) | MIT |
| Search Across Your Apps | [research/enterprise-search](research/enterprise-search) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/enterprise-search/skills/search) | Apache-2.0 |
| User Research Synthesizer | [research/synthesize-research](research/synthesize-research) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/product-management/skills/synthesize-research) | Apache-2.0 |

### Website (6)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Accessibility Audit (WCAG AA) | [website/accessibility-review](website/accessibility-review) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/design/skills/accessibility-review) | Apache-2.0 |
| Generative Art Studio | [website/algorithmic-art](website/algorithmic-art) | [anthropics/skills](https://github.com/anthropics/skills/tree/ca45fc496a3436251f191354091d557da31c15b5/skills/algorithmic-art) | Apache-2.0 |
| Landing Page CRO Review | [website/cro](website/cro) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/cro) | MIT |
| Swarm Rebuild Video | [website/swarm-rebuild](website/swarm-rebuild) | Written for EverAsk; `scripts/swarm.js` is from [DhvanilPatel/swarm-cursors](https://github.com/DhvanilPatel/swarm-cursors/tree/3d49e0ac96172eb6af7ae8229b2152121bed2092/swarm-rebuild) | None yet |
| UX Microcopy Writer | [website/ux-copy](website/ux-copy) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/design/skills/ux-copy) | Apache-2.0 |
| Website Structure Planner | [website/site-architecture](website/site-architecture) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/site-architecture) | MIT |
