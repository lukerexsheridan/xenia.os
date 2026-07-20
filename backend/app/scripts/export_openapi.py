"""Export the public OpenAPI schema (AP4).

The schema is the contract: frontend types are generated from this file, so
frontend/backend drift is a build error rather than a runtime surprise.
Internal routes are excluded at the router level (include_in_schema=False).

Usage: python -m app.scripts.export_openapi [output_path]
"""

import json
import sys
from pathlib import Path

from app.main import create_app


def main(output: str = "openapi.json") -> None:
    schema = create_app().openapi()
    path = Path(output)
    path.write_text(json.dumps(schema, indent=2) + "\n")
    sys.stdout.write(f"OpenAPI schema written to {path}\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "openapi.json")
