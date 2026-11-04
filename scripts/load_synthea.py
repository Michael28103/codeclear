"""Load Synthea FHIR bundles into a FHIR server.

Shared hospital and practitioner bundles are loaded first,
because patient bundles reference them.
"""

from pathlib import Path

import httpx2

FHIR_URL = "http://localhost:8080/fhir"
DATA_DIR = Path("data/synthea/fhir")
SHARED_PREFIXES = ("hospitalInformation", "practitionerInformation")


def load_bundle(client: httpx2.Client, path: Path) -> None:
    response = client.post(
        FHIR_URL,
        content=path.read_bytes(),
        headers={"Content-Type": "application/fhir+json"},
    )
    response.raise_for_status()


def main() -> None:
    files = sorted(DATA_DIR.glob("*.json"))
    shared = [f for f in files if f.name.startswith(SHARED_PREFIXES)]
    patients = [f for f in files if f not in shared]

    with httpx2.Client(timeout=120) as client:
        for path in shared + patients:
            load_bundle(client, path)
            print(f"loaded {path.name}")


if __name__ == "__main__":
    main()
