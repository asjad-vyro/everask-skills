# Non-functional requirements checklist

Use this when the user gave few non-functional requirements. Pick targets to assume, mark each as `Assumed`, and put them in the Assumptions list. The ranges are common examples, not facts about the user's system.

| Area | Questions to settle | Common options |
|---|---|---|
| Scalability | Concurrent users, requests per second, data volume, growth rate, peak versus average | State the user's figure; if none, assume and label |
| Performance | API latency target (use p95), page load, query time, batch throughput | p95 targets in the tens to hundreds of milliseconds for interactive APIs |
| Availability | Target uptime, maintenance windows | See downtime table below |
| Reliability | Acceptable data loss (RPO), recovery time (RTO), backup frequency, multi-region or not | RPO and RTO from minutes to a day, by business impact |
| Security | Authentication, authorisation model, data sensitivity, compliance, encryption | OAuth or OIDC, RBAC or ABAC, GDPR, HIPAA, PCI DSS, SOC 2 where the data demands it |
| Maintainability | Deploy frequency and strategy, monitoring, on-call | Blue-green, canary or rolling; logs, metrics, traces, alerts |
| Cost | Infrastructure budget, staff time to operate | Per month, per user, per request |

## Downtime allowed by an availability target

Compute this in `execute_code` from the formula `(1 - target) x 365 x 24 hours` rather than quoting from memory. For reference, 99% is about 3.65 days a year, 99.9% about 8.76 hours, 99.99% about 52.6 minutes.

Higher targets cost more: each extra nine usually needs redundancy across zones or regions, automated failover and a real on-call rota. State that cost in the design.

## Assumed-requirements block

```
Performance: <target, Assumed or user-given>
Scalability: <users, requests per second, data volume, Assumed or user-given>
Availability: <target and the downtime it allows>
Reliability: RPO <...>, RTO <...>
Security: <authentication, authorisation, compliance>
Observability: <logs, metrics, traces, alerts>
Cost: <budget or "not given">
```
