# Plan: Claims Explainer on FHIR (Synthea + HAPI FHIR)

Assumes about 4 focused hours per day, about 10 working days. Data comes from Synthea (synthetic patients exported as FHIR R4, including `Claim` and `ExplanationOfBenefit`), loaded into a local HAPI FHIR server. No real PHI anywhere, ever.

Pitch: a patient logs in, the app syncs their claims from a FHIR server, and explains each claim in plain English: what was billed, what the payer allowed and paid, what the patient owes, and what's worth asking about. Deterministic code does the math; an optional LLM layer only explains.

Design note: sync code talks to a small `FhirClient` interface, so any FHIR R4 server (Blue Button 2.0, an EHR sandbox) can plug in later by adding an auth/token provider.

## Day 1: Foundations
- [ ] `git init`, pyproject (ruff, mypy, pytest), pre-commit, Makefile
- [ ] README skeleton: problem, "what this does NOT do," disclaimer
- [ ] Docker Compose: HAPI FHIR server + Postgres
- [ ] Generate about 50 Synthea patients (Java 17 in Docker), load bundles into HAPI
- [ ] Check the adjudication categories Synthea actually uses on EOB items; note them in `docs/fhir-mapping.md`
- [ ] Save EOB bundles for 3 or 4 patients as test fixtures (include at least one denied or zero-paid line)
- Done when: `GET /fhir/ExplanationOfBenefit?patient=<id>` on local HAPI returns claims, and fixtures are committed

## Day 2: App auth and FHIR client
- [ ] User accounts: password hashing (argon2), login, session or JWT, roles (patient, admin)
- [ ] Each patient user is linked to one FHIR `Patient` id
- [ ] `FhirClient` interface with a `HapiFhirClient` implementation (base URL from config, optional token provider hook)
- [ ] Tests: a patient can never read another patient's data
- Done when: login works and the authorization tests pass

## Day 3: FHIR ingestion
- [ ] Postgres + SQLAlchemy/Alembic schema: patient, claim, claim_line, sync_run
- [ ] Sync service: page through `ExplanationOfBenefit` bundles (`next` links), retry with backoff on 429/5xx
- [ ] Idempotent upserts keyed on EOB id; sync twice, get no duplicates
- [ ] Tests against saved fixtures (no network in unit tests)
- Done when: a full sync for a patient lands in Postgres, and a second sync changes nothing

## Day 4: Normalization and code tables
- [ ] Map FHIR EOB to internal Pydantic models; document the field mapping in `docs/fhir-mapping.md`
- [ ] Extract adjudication amounts: submitted, allowed, paid, deductible, coinsurance, patient responsibility
- [ ] Code lookup for the systems Synthea uses (SNOMED CT, ICD-10-CM, HCPCS where present). Show CPT codes without AMA descriptions and note the licensing limit
- [ ] Tolerant parsing: missing fields, unknown codes, and unexpected extensions are logged and skipped, not crashes
- Done when: every claim in the fixtures normalizes without errors and codes decode to plain English

## Day 5: Deterministic explainer
- [ ] Per-claim breakdown: billed vs. allowed vs. paid vs. patient owes, with a one-line reason per amount
- [ ] Flags: exact duplicate lines, patient responsibility greater than allowed, amounts that don't add up, unknown codes
- [ ] Year-to-date view: deductible progress across claims (assumptions documented)
- [ ] Unit tests: zero-dollar lines, denied lines, partial deductible, duplicates, rounding
- Done when: tests pass and each fixture claim produces a correct, explained breakdown

## Day 6: API surface
- [ ] Endpoints: `GET /claims`, `GET /claims/{id}`, `GET /claims/{id}/explanation`, `POST /sync`, `GET /codes/{code}`
- [ ] Typed responses, OpenAPI docs, consistent error format
- [ ] API tests with TestClient; auth required on every patient endpoint
- Done when: the OpenAPI page documents everything and API tests pass

## Day 7: Security and compliance posture
- [ ] Audit log table: who accessed which patient's data, when, through which endpoint
- [ ] Structured JSON logging with PHI redaction, plus a test that asserts no PHI reaches the logs
- [ ] "Delete my data" endpoint (purge the app's local copy of claims)
- [ ] `docs/threat-model.md`: data flows, what's stored, retention, what HIPAA/BAA would require in production
- Done when: the audit log records every patient-data read and the deletion flow is tested

## Day 8: UI
- [ ] Thin frontend (Streamlit or a small React page) that only calls the FastAPI API
- [ ] Flow: log in, sync, claim list, claim detail with explanation and flags
- [ ] Disclaimer visible on every page
- Done when: the full flow works end to end against local HAPI

## Day 9: Optional AI layer (cut first if behind)
- [ ] LLM rewrites the deterministic breakdown into plain language; it receives numbers, never computes them
- [ ] Guardrail: no coverage claims; coverage questions get a disclaimer and a pointer to the payer
- [ ] Small eval: 20 claims, check that every number in the LLM output matches the deterministic output
- [ ] App works fully with the LLM turned off
- Done when: the eval table exists with honest numbers

## Day 10: Ship it
- [ ] GitHub Actions: lint, type check, tests
- [ ] Dockerfile, Docker Compose (app + HAPI + Postgres), deployed demo (synthetic data only), rate limiting
- [ ] README: architecture diagram, FHIR mapping, security posture, test/eval results, limitations, "what production would require" (BAA, SMART on FHIR / OAuth2 for real servers, X12 835 ingestion, monitoring)
- [ ] 60 to 90 second screen recording
- Done when: a stranger can clone, run `docker compose up` and `make dev`, and see it work

## Cut order if behind
1. AI layer (Day 9)
2. Year-to-date deductible view
3. Deployed demo (keep Docker Compose and the recording)

Never cut: auth and authorization tests, idempotent sync, tests, audit log.

## Future work
Blue Button 2.0 or EHR sandbox via OAuth2 (plug into `FhirClient`), SMART on FHIR EHR launch, X12 835 ingestion, plan-document RAG with cited answers, NCCI unbundling checks, fee schedule comparison, appeal-letter drafter.
