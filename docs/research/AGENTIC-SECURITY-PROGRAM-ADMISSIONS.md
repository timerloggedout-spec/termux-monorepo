# Agentic Security — Program Admissions

- **Existing lane:** `agentic-security`
- **Program anchor:** `google-fairwind`
- **Status:** admission opportunity identified; no application, referral, or acceptance is asserted
- **Owner boundary:** Research-Astute owns the research and ethical-use evidence; Termux-MonoRepo supplies relevant engineering, security, and operational evidence

## Google Fairwind Program

Google's official program name is **Fairwind Program**. It is a restricted cyber-defender access program, not a grant, general cloud-credit offer, or public model entitlement.

Official source: https://deepmind.google/fairwind-program/

The program offers trusted partners early access to advanced cyber-defense models, including Gemini for cyber, and use with CodeMender. Google prioritizes governments and national cyber authorities, critical-infrastructure operators, and core technology platforms. Google also welcomes academic labs focused on defensive benchmarking. All applicants are subject to organizational due diligence and must demonstrate an established record of ethical operations and research.

Google's published admission route is to contact the organization's Google Cloud account team. Organizations that are not yet Google Cloud customers are directed to Google's Cloud getting-started path:
https://docs.cloud.google.com/docs/get-started

## Published governance constraints

Any admission assessment must account for the program's published controls:

- Access is limited to internal cybersecurity, incident-response, or penetration-testing teams.
- User-level authentication, phishing-resistant MFA, applicable access controls, and employee access/use tracking are required.
- Program access may not be shared, redistributed, or sold.
- Permitted dual-use work is limited to authorized defensive and academic research, including threat simulation, reverse engineering, and malware analysis.
- Malicious activity, including malware creation, is prohibited.

These are program conditions, not optional implementation preferences. Do not place credentials, private vulnerability details, or sensitive customer data in public registry records.

## Admission assessment workflow

1. Identify the actual applicant organization and confirm its Google Cloud customer/account-team relationship.
2. Assemble evidence of organizational security history, ethical operations, defensive research, and downstream defensive impact.
3. Define the eligible internal team, named users, authentication, phishing-resistant MFA, access controls, and usage/audit monitoring.
4. Document authorized use cases, target ownership/authorization, isolation boundaries, data handling, and prohibited-use controls.
5. Request access through the Cloud account team and record Google's response as an external decision.

## Initial fit — unverified

Research-Astute's defensive research and Termux-MonoRepo's security/engineering work may provide relevant evidence, but the official criteria do not establish that either organization qualifies. No Cloud account status, account-team relationship, security-history package, or admission decision is asserted here. The next valid state is an evidence-backed organization assessment, not an assumed application.

## State model

`IDENTIFIED → SOURCE_VERIFIED → ORGANIZATION_ASSESSED →
CONTROL_GAPS_IDENTIFIED → ACCOUNT_TEAM_CONTACTED → UNDER_REVIEW →
ADMITTED | DECLINED | NOT_ELIGIBLE → ACCESS_GOVERNED`

Record source, observed date, owner, evidence, open gaps, and external response for each transition.
