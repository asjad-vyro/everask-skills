# Data processing agreement (DPA) checklist

Use this when a vendor or tool will process personal data for the company (an email platform, analytics tool, cloud host) or the data will cross borders. Turn each missing item into a row under Requirements, marked Not met or Unknown. This covers the data-protection side only; it is not a full review of the services contract.

## Required elements (GDPR Article 28)

- [ ] **Subject matter and duration**: clearly defined scope and term of processing
- [ ] **Nature and purpose**: specific description of what processing will occur and why
- [ ] **Type of personal data**: categories of personal data being processed
- [ ] **Categories of data subjects**: whose personal data is being processed
- [ ] **Controller obligations and rights**: the controller's instructions and oversight rights

## Processor obligations

- [ ] **Process only on documented instructions**: the processor commits to process only per the controller's instructions (with an exception for legal requirements)
- [ ] **Confidentiality**: personnel authorized to process have committed to confidentiality
- [ ] **Security measures**: appropriate technical and organizational measures described (Article 32 reference)
- [ ] **Sub-processor requirements**:
  - [ ] Written authorization requirement (general or specific)
  - [ ] If general authorization: notification of changes with an opportunity to object
  - [ ] Sub-processors bound by the same obligations through a written agreement
  - [ ] Processor remains liable for sub-processor performance
- [ ] **Data subject rights assistance**: the processor will assist the controller in responding to data subject requests
- [ ] **Security and breach assistance**: the processor will assist with security obligations, breach notification, DPIAs and prior consultation
- [ ] **Deletion or return**: on termination, delete or return all personal data (at the controller's choice) and delete existing copies unless the law requires retention
- [ ] **Audit rights**: the controller can conduct audits and inspections (or accept third-party audit reports)
- [ ] **Breach notification**: the processor will notify the controller of personal data breaches without undue delay (ideally within 24 to 48 hours; it must let the controller meet the 72-hour regulatory deadline)

## International transfers

- [ ] **Transfer mechanism identified**: SCCs, an adequacy decision (for US recipients, check whether they are certified under the EU-US Data Privacy Framework and that it is still valid), BCRs or another valid mechanism
- [ ] **SCCs version**: using the current EU SCCs (June 2021 version) if applicable
- [ ] **Correct module**: appropriate SCC module selected (C2P, C2C, P2P, P2C)
- [ ] **Transfer impact assessment**: completed if transferring to countries without adequacy decisions
- [ ] **Supplementary measures**: technical, organizational or contractual measures to address gaps identified in the transfer impact assessment
- [ ] **UK addendum**: if UK personal data is in scope, the UK International Data Transfer Addendum is included

## Practical considerations

- [ ] **Liability**: DPA liability provisions align with (or do not conflict with) the main services agreement
- [ ] **Termination alignment**: DPA term aligns with the services agreement
- [ ] **Data locations**: processing locations specified and acceptable
- [ ] **Security standards**: specific security standards or certifications required (SOC 2, ISO 27001, etc.)
- [ ] **Insurance**: adequate insurance coverage for data processing activities

## Common DPA issues

| Issue | Risk | Standard position |
|---|---|---|
| Blanket sub-processor authorization without notification | Loss of control over the processing chain | Require notification with a right to object |
| Breach notification timeline over 72 hours | May prevent timely regulatory notification | Require notification within 24 to 48 hours |
| No audit rights (or audit rights only via third-party reports) | Cannot verify compliance | Accept SOC 2 Type II plus a right to audit upon cause |
| Data deletion timeline not specified | Data retained indefinitely | Require deletion within 30 to 90 days of termination |
| No data processing locations specified | Data could be processed anywhere | Require disclosure of processing locations |
| Outdated SCCs | Invalid transfer mechanism | Require current EU SCCs (2021 version) |
