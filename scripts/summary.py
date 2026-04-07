#!/usr/bin/env python3
"""Generate GitHub Actions outputs from sync result JSON.

Writes has_changes and summary to GITHUB_OUTPUT format on stdout.
"""

import hashlib
import json
import os
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: summary.py <result.json>", file=sys.stderr)
        sys.exit(1)

    result_path = Path(sys.argv[1])
    r = json.loads(result_path.read_text())

    has_changes = bool(r["added"] or r["changed"] or r["removed"])
    print(f"has_changes={'true' if has_changes else 'false'}")

    lines = []
    if r["added"]:
        lines.append(f"Added ({len(r['added'])}):")
        lines.extend(f"  + {f}" for f in r["added"])
    if r["changed"]:
        lines.append(f"Changed ({len(r['changed'])}):")
        lines.extend(f"  ~ {f}" for f in r["changed"])
    if r["removed"]:
        lines.append(f"Removed ({len(r['removed'])}):")
        lines.extend(f"  - {f}" for f in r["removed"])
    if not has_changes:
        lines.append("All files up to date.")

    # Use a random delimiter to prevent injection via filenames
    delimiter = f"SUMMARY_{hashlib.sha256(os.urandom(16)).hexdigest()[:16]}"
    print(f"summary<<{delimiter}")
    print("\n".join(lines))
    print(delimiter)


if __name__ == "__main__":
    main()
