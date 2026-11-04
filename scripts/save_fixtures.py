"""Save ExplanationOfBenefit search results from the FHIR server as test fixtures.

Fixtures let unit tests run without a live FHIR server.
"""

import json
from pathlib import Path

import httpx2

FHIR_URL = "http://localhost:8080/fhir"
FIXTURE_DIR = Path("tests/fixtures")
PATIENT_COUNT = 3
EOBS_PER_PATIENT = 5


def main() -> None:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    with httpx2.Client(base_url=FHIR_URL, timeout=30) as client:
        response = client.get("/Patient", params={"_count": PATIENT_COUNT})
        response.raise_for_status()
        patients = response.json()

        for entry in patients["entry"]:
            patient_id = entry["resource"]["id"]
            response = client.get(
                "/ExplanationOfBenefit",
                params={"patient": patient_id, "_count": EOBS_PER_PATIENT},
            )
            response.raise_for_status()

            path = FIXTURE_DIR / f"eob_bundle_{patient_id}.json"
            path.write_text(json.dumps(response.json(), indent=2) + "\n")
            print(f"saved {path}")


if __name__ == "__main__":
    main()
