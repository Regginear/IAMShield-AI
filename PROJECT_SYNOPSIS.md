# IAMShield AI: Project Synopsis

## 1. Overview
**Project Title**: IAMShield AI: Autonomous Least-Privilege IAM Policy Synthesizer

**Problem Statement**: Cloud teams often create broad IAM policies manually. Unused permissions, privilege creep, and configuration drift increase the attack surface and make compliance difficult to demonstrate.

**Goal**: Build an AI-assisted system that analyzes access behavior and synthesizes explainable least-privilege IAM policies with controlled human approval.

**Non-goals**: Fully autonomous production enforcement without approval, replacement of cloud-native identity services, and institution-grade compliance certification in v1.

**Value Proposition**: IAMShield AI turns access telemetry into reviewable policy recommendations, helping security teams reduce excessive permissions while preserving operational access.

## 2. Scope and Control
### 2.1 In-scope
- User authentication and role-based access control
- Access-log ingestion and access-pattern analysis
- Least-privilege policy synthesis and validation
- Policy review, approval, export, and version tracking
- Audit logging and security alerts
- Dashboard for policy status, confidence, and recommendations

### 2.2 Out-of-scope
- Unapproved autonomous policy enforcement in production
- Direct replacement of AWS, Azure, or GCP IAM
- Mobile application
- Multi-tenant enterprise billing and compliance certification

### 2.3 Assumptions
- Access logs and cloud audit events are available in a usable format
- Administrators review recommendations before activation
- Users have basic knowledge of cloud identity and access management

### 2.4 Constraints
- Academic project timeline and limited compute resources
- Limited access to representative production telemetry
- Cloud-provider API quotas and data privacy requirements

### 2.5 Dependencies
- Cloud audit logs such as AWS CloudTrail or Google Cloud Audit Logs
- Policy syntax and validation libraries
- MySQL or PostgreSQL database
- LLM or rule-based analysis provider for assisted explanations

### 2.6 Acceptance criteria and sign-off
- GIVEN access events WHEN a policy is synthesized THEN the result contains only observed or explicitly approved actions and resources.
- GIVEN a proposed policy WHEN validation finds excessive permissions THEN the system reports the issue before approval.
- GIVEN a policy change WHEN it is approved or rejected THEN the actor, timestamp, reason, and policy version are recorded.
- System must generate a reviewable recommendation within acceptable latency.

| Stakeholder | Role | Decision area | Signature/Approval | Date |
|---|---|---|---|---|
| Mr. Preshit Desai | Mentor | Scope and final acceptance | Pending | September 2026 |
| Vasu Agrawal | Product Lead | Release readiness | Pending | September 2026 |

## 3. Stakeholders and RACI
| Activity | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |
|---|---|---|---|---|
| Requirements | Vasu Agrawal | Vasu Agrawal | Mentor | Team |
| Design | Akash Gaurav | Vasu Agrawal | Mentor | Team |
| Implementation | Vasu Agrawal | Vasu Agrawal | Mentor | Team |
| Testing | Sarthak | Vasu Agrawal | Mentor | Team |
| Release | Sarthak | Vasu Agrawal | Mentor | Department |

## 4. Team and Roles
| Member | Role | Responsibilities | Key skills | Availability | Contact |
|---|---|---|---|---|---|
| Vasu Agrawal | Product and Technology Lead | Scope, architecture, APIs, security, documentation | Python, FastAPI, React, SQL | 10 hrs/wk | Project team contact |
| Akash Gaurav | Frontend and Design | Dashboard UI, accessibility, user workflows | React, CSS, UX | 8 hrs/wk | Project team contact |
| Sarthak | QA and Documentation | Test planning, validation, reports | Testing, technical writing | 8 hrs/wk | Project team contact |

## 5. Week-wise Plan and Assignments
| Week | Dates | Milestones | Primary work | Deliverables | Status |
|---|---|---|---|---|---|
| 1 | 1-7 Sep | Requirements freeze | Scope and threat model | Draft SRS | Planned |
| 2 | 8-14 Sep | Architecture and database | ERD, API contracts, migrations | Architecture review | Planned |
| 3 | 15-21 Sep | Backend foundation | Authentication and policy APIs | Backend smoke test | Planned |
| 4 | 22-28 Sep | Frontend foundation | Dashboard, forms, routing | UI shell | Planned |
| 5 | 29 Sep-5 Oct | Analysis feature | Log ingestion and pattern extraction | Analysis demo | Planned |
| 6 | 6-12 Oct | Synthesis feature | Policy generation and validation | Policy demo | Planned |
| 7 | 13-19 Oct | Hardening | Security fixes and regression tests | Test report | Planned |
| 8 | 20-26 Oct | Release and deck | Documentation and final review | v1.0 submission | Planned |

## 6. Users and UX
### 6.1 Personas
- **Cloud Security Administrator**: Needs auditable, explainable recommendations and strong approval controls.
- **Application Developer**: Needs a clear policy that grants required access without learning every IAM rule.

### 6.2 Top User Journey
User -> Login -> Connect or upload access logs -> Review access patterns -> Generate policy -> Validate -> Approve or reject -> Export and audit

### 6.3 User Story
As a cloud administrator, I want IAMShield AI to explain why each permission is recommended so that I can safely approve a least-privilege policy.

### 6.4 Accessibility and Localization
- Plain-language explanations for policy findings
- Keyboard-accessible dashboard and visible focus states
- Responsive web interface
- English language support in v1

## 7. Market and Competitors
### 7.1 Competitor table
| Competitor | Product | Target users | Key features | Pricing | Strengths | Weaknesses | Our differentiator |
|---|---|---|---|---|---|---|---|
| AWS IAM Access Analyzer | Cloud IAM analysis | AWS administrators | External access and unused permission analysis | AWS service pricing | Native AWS integration | AWS-focused, limited synthesis workflow | Explainable recommendations with review and versioning |
| Microsoft Entra PIM | Privileged access management | Enterprise administrators | Just-in-time access and approvals | Microsoft licensing | Strong governance controls | Microsoft ecosystem focus | Behavioral evidence informs least-privilege policy drafts |
| Wiz | Cloud security platform | Security teams | Cloud risk and posture analysis | Enterprise pricing | Broad cloud visibility | Expensive and broad for small teams | Focused academic prototype for policy synthesis |

### 7.2 Positioning
IAMShield AI focuses on explainable, behavior-driven, and approval-controlled IAM policy synthesis.

**Measurable Delta**:
- Policy draft generation target: <= 5 seconds for a normal test dataset
- Review traceability: 100% of approved changes linked to an actor and version
- Least-privilege focus: recommendations are based on observed access rather than broad templates

## 8. Objectives and Success Metrics
- **O1: Policy quality** - At least 95% of generated policies pass syntax and baseline validation.
- **O2: Performance** - p95 synthesis response time <= 5 seconds for the project dataset.
- **O3: Security** - Zero critical security defects in the release candidate.
- **O4: Usability** - At least 90% of evaluation users can review and export a policy without assistance.

## 9. Key Features
| Feature | Description | Priority | Dependencies | Acceptance criteria |
|---|---|---|---|---|
| Access Pattern Analysis | Extracts identities, actions, resources, and time patterns from access logs. | Must | Audit logs, storage | A valid log produces a searchable access summary. |
| Policy Synthesis | Creates minimal JSON IAM policies from approved access evidence. | Must | Analysis engine | A recommendation contains actions, resources, conditions, and reasoning. |
| Policy Validation | Checks syntax, wildcards, missing resources, and baseline violations. | Must | Policy parser, rules | Invalid or excessive policies are flagged before approval. |
| Approval Workflow | Supports review, comments, approval, rejection, and version history. | Should | Auth, database | Every decision is stored with actor, time, and reason. |
| Audit and Alerts | Records policy events and highlights unusual or risky access. | Should | Auth, logging | A risky event creates an alert and an audit record. |
| Dashboard | Displays policy status, confidence, findings, and recent activity. | Could | Frontend APIs | Users can filter findings and export a policy. |

## 10. Architecture
### 10.1 High-Level Architecture
The system uses a modular web architecture for secure ingestion, analysis, policy generation, validation, and human approval.

- **Client**: React and Tailwind CSS dashboard for access analysis, policy review, and audit history.
- **Backend services**: FastAPI routes for authentication, log ingestion, analysis, synthesis, validation, approval, and audit events.
- **Analysis layer**: Rule-based least-privilege logic supported by an optional LLM explanation layer.
- **Data stores**: MySQL or PostgreSQL for users, policies, findings, and audit records; object storage for reports and sample logs.
- **Integrations**: Cloud audit-log sources, policy validators, and optional LLM provider.

### 10.2 API specification snapshot
| Endpoint | Method | Auth | Purpose | Request schema | Response schema | Codes |
|---|---|---|---|---|---|---|
| /api/auth/register | POST | - | Create account | email, password | 201 {id} | 201, 400 |
| /api/logs/ingest | POST | JWT | Ingest access events | source, events[] | 202 {jobId} | 202, 400, 401 |
| /api/policies/synthesize | POST | JWT | Generate policy draft | identity, scope | 200 {policy, findings} | 200, 400, 401 |
| /api/policies/{id}/approve | POST | JWT | Approve policy | comment | 200 {version} | 200, 401, 403 |

### 10.3 Configuration and Secrets
- Environment variables are managed through `.env` files that are Git-ignored.
- Password and API credentials are never stored in source control.
- Secrets are rotated periodically and access is restricted to authorized services.

## 11. Data Design
### 11.1 Core Entities
- User
- Role
- Access Event
- Access Pattern
- Policy
- Policy Finding
- Approval
- Audit Log

User and policy data is protected with authentication, authorization, validation, and controlled retention.

### 11.2 Data dictionary
| Entity | Field | Type | Null? | Allowed values | Source | Notes |
|---|---|---|---|---|---|---|
| User | id | UUID | No | - | System | Primary key |
| User | email | String | No | Valid email | User | Unique |
| Access Event | action | String | No | Provider action | Audit log | Indexed |
| Access Event | resource | String | No | Provider resource | Audit log | Normalized |
| Policy | document | JSON | No | Valid IAM policy | Synthesizer | Versioned |
| Policy Finding | severity | Enum | No | Low/Medium/High/Critical | Validator | Review required |

### 11.3 Schemas and Migrations
- ER diagram is maintained with the database documentation.
- Database migrations are version-controlled.
- Rollback procedures are tested in the staging environment.

### 11.4 Privacy, Retention, Backup, and DR
- Personally identifiable information: email and account metadata.
- Raw access logs are minimized and retained only for the project evaluation period.
- Nightly database backups are planned.
- Target RTO: 4 hours; target RPO: 24 hours.

## 12. Technical Workflow Diagrams
The documentation includes a state transition diagram, sequence diagram, use case diagram, data flow diagram, entity relationship diagram, and system architecture diagram.

**Primary flow**: Access Logs -> Analysis -> Pattern Extraction -> Policy Synthesis -> Validation -> User Review -> Approval -> Audit Logging

## 13. Quality: NFRs and Testing
### 13.1 Non-functional requirements
| Metric | SLI | Target (SLO) | Measurement |
|---|---|---|---|
| Availability | Uptime % | >= 99.0% during evaluation | Uptime monitor |
| Latency | p95 synthesis time | <= 5000 ms | Application logs |
| Error rate | 5xx % | <= 1% | Logs |
| Security | Critical vulnerabilities | 0 | Dependency scanner |

### 13.2 Test plan
| Area | Type | Tools | Owner | Coverage target | Exit criteria |
|---|---|---|---|---|---|
| Backend | Unit | Pytest | Vasu Agrawal | 70% | No P1/P2 defects |
| UI | E2E | Playwright | Akash Gaurav | 60% | Pass rate >= 95% |
| API | Integration | Pytest/httpx | Sarthak | All critical scenarios | All critical tests pass |

### 13.3 Environments
- Development -> Staging -> Production-like demonstration
- Feature flags are used for experimental analysis and enforcement features.

## 14. Security and Compliance
### 14.1 Threat model (STRIDE)
| Asset | Threat | STRIDE | Impact | Likelihood | Mitigation | Owner |
|---|---|---|---|---|---|---|
| Auth tokens | Theft | Spoofing | High | Medium | HTTPS, short TTL, rotation | Vasu Agrawal |
| Policy data | Unauthorized change | Tampering | High | Low | RBAC, approval workflow, audit log | Vasu Agrawal |
| Access logs | Sensitive disclosure | Information disclosure | High | Medium | Redaction, encryption, restricted access | Vasu Agrawal |

### 14.2 AuthN/AuthZ
- Email and password authentication with secure password hashing
- JWT-based authorization with expiry and refresh controls
- Role-based access control for reviewers and administrators

### 14.3 Audit and logging
- Log signups, logins, log ingestion, policy generation, approvals, exports, and configuration changes.
- Retain audit records for at least 90 days in the demonstration environment.

### 14.4 Compliance
- Academic project following institute policy and responsible disclosure practices.
- No third-party production data is used without authorization.

## 15. Delivery and Operations
### 15.1 Release plan
- Version v1.0 demonstration at project submission
- Incremental rollout of analysis, synthesis, validation, and approval features

### 15.2 CI/CD and rollback
- CI pipeline: lint -> test -> build -> deploy
- Rollback uses the previous container image and database migration plan.

### 15.3 Monitoring and alerting
| Metric | Threshold | Alert to | Runbook |
|---|---|---|---|
| p95 synthesis latency | > 6000 ms | Technology Lead | API Latency runbook |
| Error rate | > 2% | Technology Lead | Error Spike runbook |
| Critical finding count | Unexpected increase | Technology Lead | Policy Review runbook |

### 15.4 Runbooks
- **API Latency**: inspect logs and database queries -> check resource usage -> scale or revert the change.
- **Error Spike**: inspect logs -> disable the affected feature flag -> roll back -> create an incident note.

### 15.5 Communication plan
- Weekly progress review and mentor update.
- Demonstration at the end of each major feature phase.

## 16. Risks and Mitigations
### 16.1 Risk heatmap
| Risk | Probability | Impact | Score | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| Incorrect policy recommendation | Medium | High | 12 | Validation rules, test fixtures, mandatory review | Vasu Agrawal | Open |
| Sensitive log exposure | Low | High | 8 | Redaction, access control, encrypted storage | Vasu Agrawal | Open |
| Provider integration failure | Medium | Medium | 9 | Mock adapters, retries, sample datasets | Vasu Agrawal | Open |
| Model or rule bias | Low | Medium | 6 | Explainability checks and human approval | Vasu Agrawal | Open |

## 17. Research and Evaluation
### 17.1 Study of existing platforms
Cloud-native tools provide access analysis and privileged-access controls, but policy synthesis is often provider-specific or requires substantial manual interpretation. IAMShield AI focuses on converting observed behavior into explainable, reviewable policy drafts.

### 17.2 Evaluation using historical or sample data
The prototype will be evaluated with representative access-log datasets covering normal access, unused permissions, privilege creep, and anomalous activity. Generated policies will be compared with expected minimum permission sets.

### 17.3 User feedback
Students and simulated administrators will review the clarity of findings, ease of approval, confidence explanations, and export workflow. Feedback will guide usability and validation improvements.

### 17.4 KPI tracking
Key metrics include policy precision, excessive-permission reduction, synthesis latency, validation coverage, approval time, and system error rate.

## 18. Appendices
### 18.1 Glossary
- **IAM**: Identity and Access Management.
- **Least privilege**: Granting only the access required for a task.
- **RBAC**: Role-Based Access Control.
- **JIT**: Just-in-time access with limited duration.
- **p95**: 95th percentile response time.

### 18.2 References
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- AWS IAM Best Practices: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- OWASP Application Security Verification Standard: https://owasp.org/www-project-application-security-verification-standard/
- React: https://react.dev
- FastAPI: https://fastapi.tiangolo.com
- PostgreSQL: https://www.postgresql.org/docs/
