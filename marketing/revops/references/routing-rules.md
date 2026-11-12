# Lead Routing Rules

Decision trees, platform-specific configurations, territory routing, ABM routing, and speed-to-lead escalation.

## Routing Decision Tree

Use this template to map the routing logic. Replace every test, cutoff and owner with the user's own segments, people and thresholds (the $50K and territory tests below are examples):

```
New Lead Arrives
│
├─ Is this a named/target account?
│  ├─ YES → Route to assigned account owner
│  └─ NO ↓
│
├─ Is ACV likely > $50K? (based on company size + industry)
│  ├─ YES → Route to enterprise AE team
│  └─ NO ↓
│
├─ Is this a PLG signup with team usage?
│  ├─ YES → Route to PLG sales specialist
│  └─ NO ↓
│
├─ Does lead match a territory?
│  ├─ YES → Route to territory owner
│  └─ NO ↓
│
└─ Default: Round-robin across available reps
   └─ If no rep available: Assign to team queue with 1-hour SLA
```

Customize this tree for your business. The key principle: **route to the most specific match first, fall back to general.**

---

## Round-Robin Configuration

The platform setups below are general knowledge of HubSpot and Salesforce. Menu paths and actions change between versions: when the user needs exact click paths, look up the vendor's current help page with `web_search` and link it. For Pipedrive, Attio, Close or another CRM, write the rules as above and build them with that CRM's own automation or workflow tool.

### Basic Round-Robin Rules

1. Distribute leads evenly across eligible reps
2. Skip reps who are on PTO, at capacity, or have a full pipeline
3. Weight by quota attainment (reps below quota get slight priority)
4. Reset distribution count weekly or monthly
5. Log every assignment for auditing

### HubSpot Round-Robin Setup

**Using HubSpot's rotation tool:**
- Navigate to Automation → Workflows
- Trigger: Contact property "Lifecycle Stage" equals "MQL"
- Action: Rotate contact owner among selected users
- Options (confirm what the user's plan offers): even distribution, skipping unavailable owners
- Add delay + task creation after assignment

**Custom rotation with workflows:**
1. Create a custom property "Rotation Counter" (number)
2. Workflow trigger: New MQL created
3. Branch by rotation counter value (0, 1, 2... for each rep)
4. Set contact owner to corresponding rep
5. Increment counter (reset at max)
6. Create follow-up task with SLA deadline

### Salesforce Round-Robin Setup

**Using Lead Assignment Rules:**
1. Setup → Feature Settings → Marketing → Lead Assignment Rules
2. Create rule entries in priority order (most specific first)
3. For round-robin: Use assignment rule + custom logic

**Using Flow for advanced routing:**
1. Create a Record-Triggered Flow on Lead creation
2. Get Records: Query a custom "Rep Queue" object for next available rep
3. Decision element: Check rep availability, capacity, territory
4. Update Records: Assign lead owner
5. Create Task: Follow-up task with SLA
6. Update "Rep Queue" to track last assignment

---

## Territory Routing

### By Geography

| Territory | Regions | Assigned Team |
|-----------|---------|---------------|
| West | CA, WA, OR, NV, AZ, UT, CO, HI | Team West |
| Central | TX, IL, MN, MO, OH, MI, WI, IN | Team Central |
| East | NY, MA, PA, NJ, CT, VA, FL, GA | Team East |
| International | All non-US | International team |

### By Company Size

| Segment | Company Size | Team |
|---------|-------------|------|
| SMB | 1-50 employees | Inside sales |
| Mid-market | 51-500 employees | Mid-market AEs |
| Enterprise | 501-5000 employees | Enterprise AEs |
| Strategic | 5000+ employees | Strategic account team |

### By Industry

| Vertical | Industries | Specialist |
|----------|-----------|------------|
| Tech | SaaS, IT services, hardware | Tech vertical rep |
| Financial | Banking, insurance, fintech | Financial vertical rep |
| Healthcare | Hospitals, pharma, healthtech | Healthcare vertical rep |
| General | All others | General pool (round-robin) |

### Hybrid Territory Model

Combine multiple dimensions for precision:

```
Lead arrives
├─ Company size > 1000?
│  ├─ YES → Enterprise team
│  │  └─ Sub-route by geography
│  └─ NO ↓
├─ Industry = Healthcare or Financial?
│  ├─ YES → Vertical specialist
│  └─ NO ↓
└─ Round-robin across general pool
   └─ Weighted by geography preference
```

---

## Named Account / ABM Routing

### Setup

1. **Define target account list** (sized to what the named-account owners can actually work)
2. **Assign account owners** in CRM (1 rep per account)
3. **Match logic:** Any lead from a target account domain routes to account owner
4. **Matching rules:**
   - Email domain match (primary)
   - Company name fuzzy match (secondary, requires manual review)
   - IP-to-company resolution (tertiary, for anonymous visitors)

### ABM Routing Rules (example tiers and times: replace with the user's own)

| Tier | Account Type | Routing | Response SLA |
|------|-------------|---------|--------------|
| Tier 1 | Top 20 strategic accounts | Named owner, instant alert | 1 hour |
| Tier 2 | Top 100 target accounts | Named owner, standard alert | 4 hours |
| Tier 3 | Target industry / size match | Territory or round-robin | Same business day |

### Multi-Contact Handling

When multiple contacts from the same account engage:
- Route all contacts to the **same account owner**
- Notify the owner of new contacts entering
- Track account-level engagement score (sum of all contacts)
- Trigger "buying committee" alert when 3+ contacts from one account engage

---

## Speed-to-Lead

Faster first contact helps. Widely repeated studies claim large gains in qualification for contact within minutes, but those figures are old, vendor-sourced and not verified here, so do not quote a multiplier or promise one. Use them only as the reason to set a tight target.

Set the target from the team's real coverage (people, working hours, time zones): a target nobody can meet teaches reps to ignore alerts. Give different lead types different targets (for example hand-raisers such as demo requests in minutes, scored MQLs in hours, trial signups the same day). Then measure the user's own conversion by response time and tune the targets from that.

### Implementing Speed-to-Lead

1. **Instant notification** — Push notification + email to rep on MQL creation
2. **Auto-task with timer** — Create task with 5-minute SLA countdown
3. **Escalation chain** (example timings: scale them to the response target you set; reassign only under a rule the team has agreed, otherwise alert the owner and manager):
   - 5 min: Original rep alerted
   - 15 min: Backup rep alerted
   - 30 min: Manager alerted
   - 1 hour: Lead reassigned to next available rep
4. **Measure and report** — Track actual response times weekly; recognize fast responders

### Speed-to-Lead Automation

**Trigger:** New MQL created
**Actions:**
1. Assign to rep via routing rules (instant)
2. Send push notification + email to rep
3. Create task: "Contact [Lead Name] — 5 min SLA"
4. Start SLA timer
5. If no activity logged in 15 min → alert backup rep
6. If no activity in 30 min → alert manager
7. If no activity in 60 min → reassign via round-robin

### Measuring Speed-to-Lead

Track these metrics weekly:
- **Average time to first contact** (from MQL creation to first call/email)
- **Median time to first contact** (less skewed by outliers)
- **% of leads contacted within SLA** (set a target with the user; 90% is a common starting point)
- **Contact rate by time of day** (identify coverage gaps)
- **Conversion rate by response time** (prove the ROI of speed)
