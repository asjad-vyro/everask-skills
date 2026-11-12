# Automation Playbooks

Workflow recipes for the marketing-to-sales handoff, written as trigger, actions and outcome so they can be built in any CRM's workflow tool. HubSpot and Salesforce build notes come first, then a short mapping for other CRMs, scheduling tools and cross-tool automation.

How to use them:
- Time values are templates. Use the SLAs set for the user (first contact, qualification decision) in place of the ones shown.
- Property, object and menu names are general knowledge of each platform and change between versions. When the user needs exact click paths, look up the vendor's current help page with `web_search` and link it.
- Everything here is a spec for the user to build. Apply nothing to a live CRM, Slack workspace or calendar until the user says to go ahead, and list the exact changes first.
- Slack channels in the recipes (#sales-alerts, #meetings, #new-leads) are examples; Slack is optional.

## HubSpot Workflow Recipes

### 1. MQL Alert and Assignment

**Name:** MQL Notification and Task Creation
**Trigger:** Contact property "Lifecycle Stage" is changed to "Marketing Qualified Lead"
**Actions:**
1. Rotate contact owner among sales team (round-robin)
2. Send internal email notification to contact owner with lead context
3. Create task: "Follow up with [Contact Name]" — due at the first-contact SLA (4 hours in the template)
4. Send Slack notification to #sales-alerts channel (optional)
5. Enroll in "MQL Follow-Up" sequence (if using HubSpot Sequences)
**Outcome:** Every MQL gets assigned instantly with a clear SLA
**Notes:** Set enrollment criteria to exclude leads already owned by a rep

---

### 2. MQL SLA Escalation

**Name:** MQL SLA Breach Alert
**Trigger:** Contact property "Lifecycle Stage" equals "MQL" and no call, email or meeting has been logged since the MQL date, checked after each delay below
**Actions:**
1. At the first-contact SLA (4 business hours in the template): send internal email to contact owner: "SLA warning: [Contact Name] has not been contacted"
2. At 2x the first-contact SLA: send alert to sales manager
3. At the qualification deadline (48 hours in the template): alert the manager and ask for a decision; reassign contact owner via rotation only if the team has agreed a reassignment rule, otherwise keep the owner (see `references/inbound-routing.md`)
4. If reassigned, create task for new owner: "Urgent: Contact [Contact Name] — reassigned due to SLA breach"
**Outcome:** No MQL goes unworked past the qualification deadline
**Notes:** Exclude contacts where last activity type is "Call" or "Meeting" (already engaged)

---

### 3. Lead Scoring Update and MQL Promotion

**Name:** Auto-MQL on Score Threshold
**Trigger:** The contact's score property (the "HubSpot Score" property or a custom score property) is at or above the MQL threshold (65 in the template) and the fit and engagement minimums are met
**Actions:**
1. Set lifecycle stage to "Marketing Qualified Lead"
2. Set "MQL Date" to current date
3. Suppress from marketing nurture workflows
4. Trigger MQL Alert workflow (recipe #1)
**Outcome:** Leads automatically promote to MQL when they meet the MQL rule
**Notes:** Add suppression list for existing customers and competitors

---

### 4. Meeting Booked Notification

**Name:** Meeting Booked Alert to AE
**Trigger:** Meeting activity is logged for contact (via Calendly/HubSpot meetings)
**Actions:**
1. Send internal email to contact owner with meeting details
2. Update contact property "Last Meeting Booked" to current date
3. If lifecycle stage is "Lead" → update to "MQL"
4. Create task: "Prepare for meeting with [Contact Name]" — due 1 hour before meeting
5. Send Slack notification to #meetings channel (optional)
**Outcome:** AEs are prepared for every meeting with full context
**Notes:** Include recent page views and content downloads in notification email

---

### 5. Closed-Won Handoff to CS

**Name:** Customer Onboarding Trigger
**Trigger:** Deal stage is changed to "Closed Won"
**Actions:**
1. Update associated contact lifecycle stage to "Customer"
2. Set "Customer Since" date to current date
3. Assign contact owner to CS team member (based on segment/territory)
4. Create task for CS: "Schedule kickoff call with [Company Name]" — due in 2 business days
5. Enroll contact in "Customer Onboarding" email sequence
6. Send internal notification to CS manager
7. Remove from all sales sequences
**Outcome:** Seamless handoff from sales to customer success
**Notes:** Include deal notes, contract value, and key stakeholders in CS notification

---

### 6. Stale Deal Alert

**Name:** Pipeline Hygiene — Stale Deal Detection
**Trigger:** Deal property "Days in current stage" is greater than [2x average for that stage]
**Actions:**
1. Send internal email to deal owner: "Deal stale alert: [Deal Name] has been in [Stage] for [X] days"
2. Create task: "Update or close [Deal Name]" — due in 3 business days
3. If no update after 7 days → alert sales manager
4. Add to "Stale Deals" dashboard list
**Outcome:** Pipeline stays clean and forecast stays accurate
**Notes:** Customize thresholds per stage from the user's own average days in stage (for example Discovery 14 days, Proposal 10 days, Negotiation 21 days are placeholders)

---

### 7. Recycled Lead Nurture Re-Entry

**Name:** MQL Recycling to Nurture
**Trigger:** Contact property "Sales Rejection Reason" is known (any value)
**Actions:**
1. Update lifecycle stage to "Recycled"
2. Reset engagement score to baseline (keep fit score)
3. Enroll in "Recycled Lead Nurture" sequence (lower frequency)
4. Set "Recycle Date" to current date
5. Set re-enrollment trigger: if the score meets the MQL rule again, re-trigger MQL workflow
**Outcome:** Rejected leads get a second chance without clogging the pipeline
**Notes:** Track recycled-to-MQL conversion rate as a separate metric

---

### 8. Lead Activity Digest

**Name:** Daily Lead Activity Summary
**Trigger:** Scheduled — daily at 8:00 AM local time
**Actions:**
1. Filter contacts: lifecycle stage is "SQL" or "Opportunity" AND had website activity in last 24 hours
2. Send digest email to each contact owner with their leads' activity
3. Include: pages visited, content downloaded, emails opened/clicked
**Outcome:** Sales reps start each day knowing which leads are active
**Notes:** Only include leads with meaningful activity (exclude single homepage visits)

---

## Salesforce Flow Equivalents

### 1. MQL Alert and Assignment (Salesforce Flow)

**Type:** Record-Triggered Flow
**Object:** Lead
**Trigger:** Lead field "Status" is changed to "MQL"
**Flow steps:**
1. Get Records: Query "Rep Assignment" custom object for next available rep
2. Update Records: Set Lead Owner to assigned rep
3. Create Records: Create Task — "Contact MQL: {Lead.Name}" with due date = NOW + 4 hours
4. Action: Send email alert to new lead owner
5. Update Records: Update "Rep Assignment" last-assigned timestamp
**Notes:** Use a custom "Rep Assignment" object to manage round-robin state

### 2. SLA Escalation (Salesforce Flow)

**Type:** Scheduled-Triggered Flow
**Schedule:** Every 4 hours during business hours
**Flow steps:**
1. Get Records: Leads where Status = "MQL" AND LastActivityDate < TODAY - 1
2. Decision: Is lead older than 48 hours with no activity?
   - YES → Alert manager and create urgent task; reassign to the next rep only under an agreed reassignment rule
   - NO → Send reminder email to current owner
**Notes:** Pair with a record-triggered flow for real-time alerts on initial assignment

### 3. Pipeline Stage Automation (Salesforce Flow)

**Type:** Record-Triggered Flow
**Object:** Opportunity
**Trigger:** Stage field is updated
**Flow steps:**
1. Decision: Which stage was it changed to?
2. For each stage:
   - **Discovery:** Create task "Complete discovery questionnaire"
   - **Demo:** Create task "Prepare demo environment"
   - **Proposal:** Create task "Send proposal" + alert deal desk if the deal is above the deal-desk threshold
   - **Closed Won:** Trigger CS handoff (create Case, assign CS owner, send welcome email)
   - **Closed Lost:** Create task "Log loss reason" + add to win/loss analysis report

### 4. Stale Deal Detection (Salesforce Flow)

**Type:** Scheduled-Triggered Flow
**Schedule:** Daily at 7:00 AM
**Flow steps:**
1. Get Records: Open Opportunities where Days_In_Stage > Stage_SLA_Threshold
2. Loop through results:
   - Create Task: "Update stale deal: {Opportunity.Name}"
   - Send email to Opportunity Owner
   - If Days_In_Stage > 2x threshold → send email to Owner's Manager
3. Update custom field "Stale Flag" = true for dashboard visibility

---

## Other CRMs (Pipedrive, Attio, Close)

Every recipe above has the same shape: a trigger (a record is created or changed, or a schedule fires), conditions, then actions (assign an owner, create a task, send a notification, update a field). To build one in Pipedrive, Attio, Close or another CRM:
1. Pick the recipe closest to the job and keep its trigger, conditions and actions.
2. Map the lifecycle stages to that CRM's own stage or status fields (a custom "Lifecycle stage" field if it has none), and say which you chose.
3. Build it in that CRM's automation or workflow tool. If the CRM has no built-in owner rotation, use a counter field or a scheduling tool's round-robin.
4. If the user wants step-by-step instructions for that CRM, look up its current automation help page with `web_search` and link it; do not invent menu paths.

---

## Scheduling Tool Patterns (Calendly or any scheduling tool)

### Round-Robin Meeting Scheduling

**Setup:**
1. Create a team event type with all eligible reps
2. Distribution: equal distribution across the team
3. Availability: each rep manages their own calendar
4. Buffer: 15 min before and after meetings
5. Minimum notice: 4 hours (avoid last-minute bookings)

**CRM integration:**
1. The scheduling tool fires a webhook or integration event on booking
2. Match invitee email to CRM contact
3. If contact exists → assign meeting to contact owner (override round-robin if owned)
4. If new contact → create lead, assign via routing rules, log meeting
5. Set lifecycle stage to MQL (meeting = high intent)

### Meeting Routing by Criteria

```
Booking form submitted
├─ Company size > 500? (form field)
│  ├─ YES → Route to enterprise AE calendar
│  └─ NO ↓
├─ Existing customer? (CRM lookup)
│  ├─ YES → Route to account owner's calendar
│  └─ NO ↓
└─ Round-robin across SDR team
```

Replace the size cutoff and the calendars with the user's own.

### No-Show Workflow

**Trigger:** Meeting time passes + no meeting notes logged within 30 minutes
**Actions:**
1. Wait 30 minutes after scheduled meeting time
2. Check: Was a call or meeting logged?
   - YES → No action
   - NO → Send "Sorry we missed you" email to prospect
3. Create task: "Reschedule with [Contact Name]" — due next business day
4. If second no-show → flag contact and alert manager

---

## Cross-Tool Recipes (native CRM workflows, Zapier, Make or similar)

### 1. New Lead → CRM + Slack + Task

**Trigger:** New form submission (Typeform, HubSpot, Webflow)
**Actions:**
1. Create/update contact in CRM
2. Enrich with the user's enrichment provider (the CRM's built-in enrichment, Clay, Apollo, or similar)
3. Post to Slack #new-leads with enriched data (optional)
4. Create task in project management tool (Asana, Linear)

### 2. Meeting Booked → CRM + Prep Email

**Trigger:** New booking in the scheduling tool
**Actions:**
1. Find or create CRM contact
2. Update lifecycle stage to MQL
3. Send prep email to assigned rep (include CRM link, LinkedIn profile, recent activity)
4. Create pre-meeting task

### 3. Deal Closed → Onboarding Stack

**Trigger:** CRM deal stage changed to "Closed Won"
**Actions:**
1. Create customer record in CS tool (Vitally, Gainsight, ChurnZero)
2. Add to onboarding project template
3. Send welcome email via email tool
4. Create Slack channel: #customer-[company-name] (optional)
5. Notify CS team

### 4. Lead Scoring → Cross-Tool Sync

**Trigger:** CRM lead score meets the MQL rule
**Actions:**
1. Update marketing automation platform status
2. Add to retargeting audience (Facebook, Google Ads)
3. Trigger SDR outreach sequence
4. Log event in analytics (Mixpanel, Amplitude)

### 5. SLA Breach → Multi-Channel Alert

**Trigger:** CRM task overdue (MQL follow-up task)
**Actions:**
1. Send Slack DM or email to rep
2. If 2+ hours overdue → notify manager
3. If 4+ hours overdue → reassign in CRM (via webhook back to CRM), only under an agreed reassignment rule; otherwise escalate to the manager

### 6. Weekly Pipeline Digest

**Trigger:** Schedule — every Monday at 8:00 AM
**Actions:**
1. Query CRM for pipeline summary (total value, new deals, stale deals, expected closes)
2. Format as summary
3. Post to Slack #sales-team (optional)
4. Send email digest to sales leadership
