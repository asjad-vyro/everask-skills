# EverAsk Skills

The 61 launch skills for the EverAsk Skills Library. Each skill is a folder with a `SKILL.md` at its top.

- 58 are copied unchanged from open-source repos at pinned commits, except for the `name` in `SKILL.md`, which is set to the Library card title. The tables below link each one's source and give its licence.
- The 3 slides skills are our own. They plan the deck, then build it with EverAsk's built-in slide maker.

Each folder also has a `skill.config.json` of our own, with the skill's Library type, example prompts and connector badges, and the 58 open-source skills each have a `cover.webp` for their Library card.

## Import

One import gives every skill the same type, so import each type folder with its own link and pick the matching type:

| Type | Link | Skills |
|---|---|---|
| Document | https://github.com/asjad-vyro/everask-skills/tree/main/document | 15 |
| Slides | https://github.com/asjad-vyro/everask-skills/tree/main/slides | 3 |
| Email | https://github.com/asjad-vyro/everask-skills/tree/main/email | 7 |
| Data | https://github.com/asjad-vyro/everask-skills/tree/main/data | 9 |
| Engineering | https://github.com/asjad-vyro/everask-skills/tree/main/engineering | 3 |
| Marketing | https://github.com/asjad-vyro/everask-skills/tree/main/marketing | 14 |
| Research | https://github.com/asjad-vyro/everask-skills/tree/main/research | 7 |
| Website | https://github.com/asjad-vyro/everask-skills/tree/main/website | 3 |

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
- **Covers** are optional: one image named `cover` next to `SKILL.md`, as `.webp` (preferred), `.png`, `.jpg`, `.jpeg` or `.gif`, up to 5 MB and kept small. The 58 open-source skills each have a 600×800 `cover.webp`; the 3 slides skills have no cover yet.
- **Before you push**, run `uv run scripts/validate.py` (or `pip install pyyaml`, then `python3 scripts/validate.py`). It checks the import rules and exits non-zero on any failure. Add `--connectors <file>`, with the backend's slugs one per line, to check that every connector exists.

## Skills

### Document (15)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Business Model Canvas | [document/business-model](document/business-model) | [phuryn/pm-skills](https://github.com/phuryn/pm-skills/tree/2a12295a7717569baa7be181b4cfebe3ca38a6bb/pm-product-strategy/skills/business-model) | MIT |
| Cover Letter Writer | [document/cover-letter-generator](document/cover-letter-generator) | [Paramchoudhary/ResumeSkills](https://github.com/Paramchoudhary/ResumeSkills/tree/74ae19e7c62b0516d1c298328e5544976c12da5d/skills/cover-letter-generator) | MIT |
| Document Comparison | [document/compare-documents](document/compare-documents) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/assistant-workflows/compare-documents) | MIT |
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
| RFP Responder | [document/rfp-responder](document/rfp-responder) | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/e4a1dc3695908dd5a6c811cc76ab7aa4cf95f2f0/commercial/skills/rfp-responder) | MIT |
| SOP and Process Writer | [document/process-doc](document/process-doc) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/operations/skills/process-doc) | Apache-2.0 |

### Slides (3)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Lecture and Lesson Slides | [slides/lecture-slides](slides/lecture-slides) | Written for EverAsk | — |
| Pitch Deck Builder | [slides/pitch-deck](slides/pitch-deck) | Written for EverAsk | — |
| Quarterly Business Review Deck | [slides/quarterly-business-review](slides/quarterly-business-review) | Written for EverAsk | — |

### Email (7)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Cold Email Writer | [email/cold-email](email/cold-email) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/cold-email) | MIT |
| Customer Reply Writer | [email/draft-response](email/draft-response) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/customer-support/skills/draft-response) | Apache-2.0 |
| Email Sequence Builder | [email/email-sequence](email/email-sequence) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/email-sequence) | Apache-2.0 |
| Inbox Triage and Replies | [email/inbox-manager](email/inbox-manager) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/inbox-manager) | Apache-2.0 |
| Meeting Follow-Ups | [email/meeting-follow-up-pipeline](email/meeting-follow-up-pipeline) | [zapier/wade-skills](https://github.com/zapier/wade-skills/tree/b7b86e78ae2e1235bebac8668edd834b34176c19/skills/meeting-follow-up-pipeline) | MIT |
| Overdue Invoice Chaser | [email/invoice-chase](email/invoice-chase) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/invoice-chase) | Apache-2.0 |
| Suspicious Email Analyzer | [email/suspicious-email](email/suspicious-email) | [claude-office-skills/skills](https://github.com/claude-office-skills/skills/tree/9c4c7d5cd2813a8936bf2c9fdb174ea883b85a11/suspicious-email) | MIT |

### Data (9)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| A/B Test and Stats Checker | [data/statistical-analyst](data/statistical-analyst) | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills/tree/e4a1dc3695908dd5a6c811cc76ab7aa4cf95f2f0/engineering/statistical-analyst/skills/statistical-analyst) | MIT |
| Account Reconciliation | [data/reconciliation](data/reconciliation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/reconciliation) | Apache-2.0 |
| Analysis QA Check | [data/validate-data](data/validate-data) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/validate-data) | Apache-2.0 |
| Budget vs Actual Variance Analysis | [data/variance-analysis](data/variance-analysis) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/variance-analysis) | Apache-2.0 |
| Cash Flow Snapshot | [data/cash-flow-snapshot](data/cash-flow-snapshot) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/small-business/skills/cash-flow-snapshot) | Apache-2.0 |
| Contract Terms Table | [data/commercial-agreement-tabular-review](data/commercial-agreement-tabular-review) | [open-legal-products/mike-workflows](https://github.com/open-legal-products/mike-workflows/tree/20bed204ce9ef07e1bc2df0b16b35ee8ad997fb1/tabular-review-workflows/commercial-agreement-tabular-review) | MIT |
| Dataset Profiler | [data/explore-data](data/explore-data) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/explore-data) | Apache-2.0 |
| Journal Entry Prep | [data/journal-entry](data/journal-entry) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/finance/skills/journal-entry) | Apache-2.0 |
| SQL Query Writer | [data/sql-queries](data/sql-queries) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/data/skills/sql-queries) | Apache-2.0 |

### Engineering (3)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Code Reviewer | [engineering/code-reviewer](engineering/code-reviewer) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/078a25cc5bfd8011459be7b91d004e900c1d02d3/skills/code-reviewer) | MIT |
| Prompt Engineer | [engineering/prompt-engineer](engineering/prompt-engineer) | [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills/tree/078a25cc5bfd8011459be7b91d004e900c1d02d3/skills/prompt-engineer) | MIT |
| README Writer | [engineering/crafting-effective-readmes](engineering/crafting-effective-readmes) | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/3027f20f3181758385a1bb8c022d4041dfb4de84/skills/crafting-effective-readmes) | MIT |

### Marketing (14)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Ad Copy Generator | [marketing/ad-creative](marketing/ad-creative) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/ad-creative) | MIT |
| AI Search Visibility (GEO) | [marketing/ai-seo](marketing/ai-seo) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/ai-seo) | MIT |
| Brand Voice Guide Builder | [marketing/guideline-generation](marketing/guideline-generation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/partner-built/brand-voice/skills/guideline-generation) | MIT |
| Churn Prevention | [marketing/churn-prevention](marketing/churn-prevention) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/churn-prevention) | MIT |
| Comparison & Alternative Pages | [marketing/competitors](marketing/competitors) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/competitors) | MIT |
| Content Strategy Planner | [marketing/content-strategy](marketing/content-strategy) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/content-strategy) | MIT |
| Marketing Copywriter | [marketing/copywriting](marketing/copywriting) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/copywriting) | MIT |
| Marketing Plan Builder | [marketing/marketing-plan](marketing/marketing-plan) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/marketing-plan) | MIT |
| Multichannel Content Writer | [marketing/content-creation](marketing/content-creation) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/content-creation) | Apache-2.0 |
| Positioning & Messaging Doc | [marketing/product-marketing](marketing/product-marketing) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/product-marketing) | MIT |
| Programmatic SEO Planner | [marketing/programmatic-seo](marketing/programmatic-seo) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/programmatic-seo) | MIT |
| Sales Collateral Builder | [marketing/sales-enablement](marketing/sales-enablement) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/sales-enablement) | MIT |
| SEO Audit | [marketing/seo-audit](marketing/seo-audit) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/seo-audit) | MIT |
| Social Media Content | [marketing/social](marketing/social) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/social) | MIT |

### Research (7)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Catch-Up Digest | [research/activity-digest](research/activity-digest) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/enterprise-search/skills/digest) | Apache-2.0 |
| Competitor Brief and Battlecard | [research/competitive-brief](research/competitive-brief) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/marketing/skills/competitive-brief) | Apache-2.0 |
| Fact Checker | [research/blog-factcheck](research/blog-factcheck) | [AgriciDaniel/claude-blog](https://github.com/AgriciDaniel/claude-blog/tree/354442348815a7f0327077ad89af2c43cf4b4ab4/skills/blog-factcheck) | MIT |
| Market Sizing (TAM, SAM, SOM) | [research/market-sizing-analysis](research/market-sizing-analysis) | [wshobson/agents](https://github.com/wshobson/agents/tree/7e2fb559cf4b824b27f1fec49fe88f7511066d26/plugins/startup-business-analyst/skills/market-sizing-analysis) | MIT |
| Reddit Opportunity Finder | [research/reddit-opportunity-research](research/reddit-opportunity-research) | [onvoyage-ai/gtm-engineer-skills](https://github.com/onvoyage-ai/gtm-engineer-skills/tree/cfdb9edd84109077153fa7faf776eb35f6c04370/reddit-opportunity-research) | MIT |
| Search Across Your Apps | [research/enterprise-search](research/enterprise-search) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/enterprise-search/skills/search) | Apache-2.0 |
| User Research Synthesizer | [research/synthesize-research](research/synthesize-research) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/product-management/skills/synthesize-research) | Apache-2.0 |

### Website (3)

| Skill | Folder | Source | Licence |
|---|---|---|---|
| Landing Page CRO Review | [website/cro](website/cro) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/cro) | MIT |
| UX Microcopy Writer | [website/ux-copy](website/ux-copy) | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/design/skills/ux-copy) | Apache-2.0 |
| Website Structure Planner | [website/site-architecture](website/site-architecture) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills/tree/88c79f6528a9347420e57ceb1fff9a60de651768/skills/site-architecture) | MIT |
