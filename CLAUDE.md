Project: Claims Explainer on FHIR (Synthea + HAPI FHIR)

Portfolio project for a software engineer job search at healthcare app companies. Built to show healthcare interoperability (FHIR R4), solid backend engineering (FastAPI, idempotent sync, typed APIs, tests), and a compliance-minded posture (authorization, audit logging, no PHI in logs).

What it does

A patient logs in. The FastAPI backend syncs their FHIR ExplanationOfBenefit resources from a FHIR server (local HAPI FHIR loaded with Synthea data), decodes the codes into plain English, explains each claim (billed vs. allowed vs. paid vs. patient owes), and flags issues worth asking about.

Architecture
FastAPI is the backend and owns all business logic, auth, and the API.
HAPI FHIR is only an upstream data source, standing in for a payer or EHR FHIR API. The app never exposes it directly.
Postgres holds users, synced claims, sync runs, and the audit log.
The UI (Streamlit or a small React page) is only a client of the FastAPI API.

What it must NOT do
Never states that a claim "is covered" or "should be covered." Wording is always "estimate," "the claim record shows," or "worth asking about."
Synthetic (Synthea) data only. Never commit .env, secrets, or anything resembling real patient data.
Never log passwords, tokens, or patient data. Logs are structured and redacted.
Educational tool, not a coverage determination, not medical or legal advice. Disclaimer appears in the README and on every UI page.

Core design rule

Deterministic code does all math, flags, and rules. The optional LLM layer only rewrites the deterministic output in plain language; it never computes amounts or makes coverage claims. The app must work fully with the LLM turned off.

Services (inside the FastAPI app)

auth: user accounts, argon2 password hashing, login, roles (patient, admin); each patient user maps to one FHIR Patient id; a patient can never read another patient's data
fhir client: FhirClient interface with a HapiFhirClient implementation and an optional token provider hook, so Blue Button 2.0 or an EHR sandbox can plug in later
sync: pages through ExplanationOfBenefit bundles, retry with backoff on 429/5xx, idempotent upserts keyed on EOB id
normalizer: FHIR EOB to internal Pydantic models, field mapping documented in docs/fhir-mapping.md, tolerant parsing (log and skip, never crash)
explainer: per-claim breakdown plus flags (duplicate lines, patient responsibility above allowed, amounts that don't add up, unknown codes)
audit: records every read of patient data (who, which patient, when, which endpoint)
codes: lookup for code systems found in the data (SNOMED CT, ICD-10-CM, HCPCS)

Stack

Python 3.10+, FastAPI, Pydantic, Postgres with SQLAlchemy and Alembic, HAPI FHIR (Docker), Synthea (Java 17 in Docker), Docker Compose, pytest, ruff, mypy (strict), pre-commit, GitHub Actions. Development happens in WSL2 Ubuntu in ~/CodeClear, not under /mnt/c.

Code licensing note

CPT descriptions are AMA-licensed. CPT codes may be shown but their descriptions are not bundled. Document the limitation in the README.

Layout
app/        FastAPI app: api, auth, fhir client, sync, models, explainer, audit
scripts/    generate_synthea.sh, load_hapi.sh
data/       code tables; generated Synthea output is gitignored
tests/      unit and API tests; fixtures are saved EOB bundles, no network in unit tests
docs/       fhir-mapping.md, threat-model.md
evals/      optional AI-layer eval (numbers in LLM output match deterministic output)

Working rules
Write tests alongside the code (zero-dollar lines, denied lines, partial deductible, duplicates, rounding, re-sync idempotency, cross-patient access denied).
Every endpoint that returns patient data requires auth and writes to the audit log.
Commit in small steps with clear messages. Commit history is part of the portfolio.
Report honest numbers, including unflattering ones.

See plan.md for the schedule and current progress.
