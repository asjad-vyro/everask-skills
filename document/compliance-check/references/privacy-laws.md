# Privacy law quick reference

Starting points for spotting which privacy laws bear on an action and what they ask for. Deadlines, thresholds and rules change, so confirm the ones you rely on (Step 3) before you state them.

## GDPR (EU General Data Protection Regulation)

**Scope**: applies to organizations established in the EU/EEA (whoever the data is about), and to organizations elsewhere that offer goods or services to people in the EU/EEA or monitor their behavior. A company based outside the EU is covered if it targets people there.

**Key obligations**:
- **Lawful basis**: identify and document a lawful basis for each processing activity (consent, contract, legitimate interest, legal obligation, vital interest, public task).
- **Valid consent** (when consent is the basis): freely given, specific, informed and unambiguous, given by a clear affirmative act. Pre-ticked boxes, silence and bundled consent do not count. The company must be able to prove it, and withdrawing must be as easy as giving it.
- **Transparency**: a privacy notice at collection saying who collects the data, why, on what basis, who receives it and what rights people have.
- **Data subject rights**: respond to access, rectification, erasure, portability, restriction and objection requests within one month (extendable by two further months for complex requests). The right to object to direct marketing is absolute: stop when asked.
- **Data protection impact assessments (DPIAs)**: required for processing likely to result in high risk to individuals.
- **Breach notification**: notify the supervisory authority within 72 hours of becoming aware of a personal data breach; notify affected individuals without undue delay if the risk is high.
- **Records of processing**: maintain Article 30 records of processing activities.
- **International transfers**: ensure appropriate safeguards for transfers outside the EEA (adequacy decisions, SCCs, BCRs).
- **DPO**: appoint a Data Protection Officer if required (public authority, large-scale processing of special categories, large-scale systematic monitoring).
- **Special categories** (health, biometric data used to identify someone, and similar) need an extra legal condition, usually explicit consent.

Marketing emails and texts also fall under the EU e-privacy rules, which are separate from GDPR: see `references/marketing-and-advertising.md`.

## CCPA / CPRA (California Consumer Privacy Act / California Privacy Rights Act)

**Scope**: applies to businesses that collect personal information of California residents and meet revenue, data volume or data sale thresholds. Look up the current thresholds before saying whether a company is covered. Many other US states (for example Virginia, Colorado, Connecticut and Texas) have their own privacy laws with their own thresholds and rights, so check which states the people live in.

**Key obligations**:
- **Right to know**: consumers can request disclosure of personal information collected, used and shared
- **Right to delete**: consumers can request deletion of their personal information
- **Right to opt out**: consumers can opt out of the sale or sharing of personal information
- **Right to correct**: consumers can request correction of inaccurate personal information (CPRA addition)
- **Right to limit use of sensitive personal information**: consumers can limit use of sensitive PI to specific purposes (CPRA addition)
- **Non-discrimination**: cannot discriminate against consumers who exercise their rights
- **Privacy notice**: must provide a privacy notice at or before collection describing the categories of PI collected and the purposes
- **Service provider agreements**: contracts with service providers must restrict use of PI to the specified business purpose

**Response timelines**:
- Acknowledge receipt within 10 business days
- Respond substantively within 45 calendar days (extendable by 45 days with notice)

## Other privacy laws to watch

| Law | Jurisdiction | Key differentiators |
|---|---|---|
| **UK GDPR** and **PECR** | United Kingdom | Post-Brexit UK version of GDPR, with ICO oversight; PECR covers marketing emails, texts, calls and cookies |
| **LGPD** | Brazil | Similar to GDPR; DPO appointment generally required; ANPD enforcement |
| **POPIA** | South Africa | Information Regulator oversight; an Information Officer must be registered; prior authorization needed for some processing |
| **PIPEDA** | Canada (federal) | Consent-based framework; OPC oversight; some provinces (for example Quebec) have their own laws; check the status of reform |
| **PDPA** | Singapore | Do Not Call registry; mandatory breach notification; PDPC enforcement |
| **Privacy Act** | Australia | Australian Privacy Principles (APPs); notifiable data breaches scheme |
| **PIPL** | China | Strict cross-border transfer rules; data localization requirements; CAC oversight |

## Special cases

- **Biometrics** (face, fingerprint or voice used to identify someone): special-category data under GDPR. Some US states have specific biometric laws; Illinois' BIPA requires written notice and consent and lets people sue. First find out whether the company itself collects or stores the biometric data, or the app only uses the phone's built-in unlock and gets a yes or no back. The duties are very different.
- **Children**: COPPA in the US (under 13), GDPR Article 8 in the EU (the age for a child's own consent is set by each country, between 13 and 16), and the UK Children's Code.
- **Health**: HIPAA covers only certain US health organizations and their business associates. Other health data is still covered by GDPR special-category rules and by state and consumer-protection laws.
