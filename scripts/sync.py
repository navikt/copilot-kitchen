#!/usr/bin/env python3
"""Sync hovmester source files to target repositories.

Compares files, copies new/changed ones, removes stale files via manifest,
and outputs a JSON result for the GitHub Actions workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MANIFEST_PATH = ".github/.hovmester-manifest.json"
LEGACY_MANIFEST_PATH = ".github/.copilot-kitchen-manifest.json"
LEGACY_MARKER = "Managed by esyfo-cli"

DIR_MAPPING: dict[str, str] = {
    "dist/agents": ".github/agents",
    "dist/instructions": ".github/instructions",
    "dist/skills": ".github/skills",
    "dist/issue-templates": ".github/ISSUE_TEMPLATE",
}

SINGLE_FILE_MAPPING: dict[str, str] = {
    "dist/PULL_REQUEST_TEMPLATE.md": ".github/PULL_REQUEST_TEMPLATE.md",
}

# Never sync or clean these target directories
EXCLUDED_TARGET_DIRS: set[str] = {".github/workflows"}

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class SyncDiff:
    added: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def transform_issue_template(content: str, github_project: str) -> str:
    """Substitute or strip the ${GITHUB_PROJECT} placeholder in issue templates.

    Template files under dist/issue-templates/ MUST use the exact format:
        projects: ["${GITHUB_PROJECT}"]
    (double quotes, no extra whitespace inside the brackets). The stripping
    regex is tied to this format — if the template format changes, update
    the regex accordingly.
    """
    if github_project:
        return content.replace("${GITHUB_PROJECT}", github_project)
    # Strip the entire projects line when no project is configured
    return re.sub(
        r'^projects:\s*\["\$\{GITHUB_PROJECT\}"\]\s*\n',
        '',
        content,
        flags=re.MULTILINE,
    )


def build_file_mapping(source: Path) -> dict[str, tuple[Path, str]]:
    """Scan source directories and return {target_rel: (source_abs, source_rel)}.

    DIR_MAPPING entries are scanned recursively (important for skills/
    which contains references/ subdirectories).
    SINGLE_FILE_MAPPING entries are checked individually.
    Nothing under EXCLUDED_TARGET_DIRS is ever included.
    Symlinks are skipped to prevent traversal and infinite loops.

    The source_rel is the path relative to the source repo root (e.g.
    'dist/agents/hovmester.agent.md'), needed by _read_source_content
    to decide whether to apply template transforms.
    """
    mapping: dict[str, tuple[Path, str]] = {}

    for src_dir_name, tgt_dir in DIR_MAPPING.items():
        src_dir = source / src_dir_name
        if not src_dir.is_dir():
            continue
        for src_file in src_dir.rglob("*"):
            if src_file.is_symlink():
                continue
            if not src_file.is_file():
                continue
            rel = src_file.relative_to(src_dir)
            target_rel = f"{tgt_dir}/{rel}"
            if any(target_rel.startswith(excl) for excl in EXCLUDED_TARGET_DIRS):
                continue
            source_rel = f"{src_dir_name}/{rel}"
            mapping[target_rel] = (src_file, source_rel)

    for src_name, tgt_rel in SINGLE_FILE_MAPPING.items():
        src_file = source / src_name
        if src_file.is_symlink():
            continue
        if src_file.is_file():
            if any(tgt_rel.startswith(excl) for excl in EXCLUDED_TARGET_DIRS):
                continue
            mapping[tgt_rel] = (src_file, src_name)

    return mapping


def _read_source_content(
    source_path: Path, source_rel: str, github_project: str
) -> bytes:
    """Read source file content, applying template transforms where applicable.

    For files under dist/issue-templates/ with a .yml or .yaml extension,
    applies transform_issue_template() to substitute or strip the
    ${GITHUB_PROJECT} placeholder. All other files are returned as raw bytes.

    source_rel is the path relative to the source repo root (e.g.
    'dist/issue-templates/bug.yml'), used to decide whether to apply
    transforms. It is NOT the target path.
    """
    content = source_path.read_bytes()
    if source_rel.startswith("dist/issue-templates/") and source_path.suffix in (".yml", ".yaml"):
        text = content.decode("utf-8")
        transformed = transform_issue_template(text, github_project)
        return transformed.encode("utf-8")
    return content


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_diff(
    mapping: dict[str, tuple[Path, str]],
    target_root: Path,
    github_project: str = "",
) -> SyncDiff:
    """Compare SHA-256 hashes of source vs target files.

    The source content is read via _read_source_content so that
    issue-template transforms are applied before hashing — without
    this, templates would always be detected as 'changed' because
    the target file contains the substituted project ID while the
    raw source file still contains the placeholder.
    """
    diff = SyncDiff()
    for target_rel, (source_path, source_rel) in mapping.items():
        target_path = target_root / target_rel
        source_content = _read_source_content(source_path, source_rel, github_project)
        if not target_path.exists():
            diff.added.append(target_rel)
        elif _sha256(source_content) != _sha256(target_path.read_bytes()):
            diff.changed.append(target_rel)
        else:
            diff.unchanged.append(target_rel)
    return diff


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------


def resolve_collections(
    source: Path, collections_input: str | None
) -> dict[str, set[str]] | None:
    """Resolve which files to include based on collections input.

    Returns None if no filtering (all files). Returns a dict mapping
    category -> set of allowed names when filtering is active.
    """
    collections_path = source / "collections.yml"
    if not collections_path.exists():
        return None
    if not collections_input:
        return None

    collections_data = yaml.safe_load(collections_path.read_text(encoding="utf-8")) or {}
    requested = {c.strip() for c in collections_input.split(",")}

    # hovmester is always included
    requested.add("hovmester")

    allowed: dict[str, set[str]] = {
        "agents": set(),
        "instructions": set(),
        "skills": set(),
        "issue_templates": set(),
        "pull_request_template": set(),
    }

    for collection_name in requested:
        collection = collections_data.get(collection_name, {})
        if not isinstance(collection, dict):
            continue
        for category, items in collection.items():
            if category not in allowed:
                continue
            if isinstance(items, list):
                allowed[category].update(items)
            elif isinstance(items, str):
                allowed[category].add(items)

    return allowed


def filter_mapping_by_collections(
    mapping: dict[str, tuple[Path, str]],
    allowed: dict[str, set[str]] | None,
) -> dict[str, tuple[Path, str]]:
    """Filter a file mapping based on resolved collections."""
    if allowed is None:
        return mapping

    filtered: dict[str, tuple[Path, str]] = {}
    for target_rel, source_path in mapping.items():
        if _file_allowed_by_collections(target_rel, allowed):
            filtered[target_rel] = source_path
    return filtered


def filter_mapping_by_exclude(
    mapping: dict[str, tuple[Path, str]],
    exclude_input: str | None,
) -> dict[str, tuple[Path, str]]:
    """Remove files matching exclude names from the mapping.

    Exclude names are matched against:
    - Agent filenames (e.g. 'hovmester.agent.md')
    - Instruction filenames (e.g. 'kotlin.instructions.md')
    - Skill directory names (e.g. 'kafka-topic' matches all files under that skill)
    - Issue template filenames (e.g. 'bug.yml')
    """
    if not exclude_input:
        return mapping

    excluded = {name.strip() for name in exclude_input.split(",")}

    filtered: dict[str, tuple[Path, str]] = {}
    for target_rel, source_path in mapping.items():
        if _file_excluded(target_rel, excluded):
            continue
        filtered[target_rel] = source_path
    return filtered


def _file_excluded(target_rel: str, excluded: set[str]) -> bool:
    """Check if a target file path matches any excluded name."""
    if target_rel.startswith(".github/agents/"):
        name = target_rel.split("/")[-1].replace(".agent.md", "")
        return name in excluded

    if target_rel.startswith(".github/instructions/"):
        name = target_rel.split("/")[-1].replace(".instructions.md", "")
        return name in excluded

    if target_rel.startswith(".github/skills/"):
        parts = target_rel.replace(".github/skills/", "").split("/")
        skill_name = parts[0] if parts else ""
        return skill_name in excluded

    if target_rel.startswith(".github/ISSUE_TEMPLATE/"):
        name = target_rel.split("/")[-1].replace(".yml", "").replace(".yaml", "")
        return name in excluded

    return False


def _file_allowed_by_collections(
    target_rel: str, allowed: dict[str, set[str]]
) -> bool:
    """Check if a target file path is allowed by the resolved collections."""
    if target_rel.startswith(".github/agents/"):
        name = target_rel.split("/")[-1].replace(".agent.md", "")
        return name in allowed.get("agents", set())

    if target_rel.startswith(".github/instructions/"):
        name = target_rel.split("/")[-1].replace(".instructions.md", "")
        return name in allowed.get("instructions", set())

    if target_rel.startswith(".github/skills/"):
        parts = target_rel.replace(".github/skills/", "").split("/")
        skill_name = parts[0] if parts else ""
        return skill_name in allowed.get("skills", set())

    if target_rel.startswith(".github/ISSUE_TEMPLATE/"):
        name = target_rel.split("/")[-1].replace(".yml", "").replace(".yaml", "")
        return name in allowed.get("issue_templates", set())

    if target_rel == ".github/PULL_REQUEST_TEMPLATE.md":
        return "PULL_REQUEST_TEMPLATE.md" in allowed.get("pull_request_template", set())

    # Unknown paths are excluded when collections filtering is active
    return False


# ---------------------------------------------------------------------------
# Manifest-based stale cleanup
# ---------------------------------------------------------------------------


def migrate_legacy_manifest(target_root: Path) -> None:
    """One-time migration from copilot-kitchen manifest to hovmester manifest.

    If the legacy manifest (.copilot-kitchen-manifest.json) exists and the
    new hovmester manifest does not, move the legacy file to the new path.
    If the new manifest already exists, leave both files alone (this lets
    the user clean up the orphaned legacy file manually once they are sure
    the new manifest is authoritative).
    """
    legacy = target_root / LEGACY_MANIFEST_PATH
    new = target_root / MANIFEST_PATH
    if legacy.exists() and not new.exists():
        new.parent.mkdir(parents=True, exist_ok=True)
        new.write_bytes(legacy.read_bytes())
        legacy.unlink()


def read_manifest(target_root: Path) -> list[str] | None:
    """Read the manifest file. Returns None if it doesn't exist or is corrupt."""
    manifest_path = target_root / MANIFEST_PATH
    if not manifest_path.exists():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return data.get("files", [])
    except (json.JSONDecodeError, OSError):
        return None


def write_manifest(target_root: Path, files: list[str], source_sha: str = "") -> None:
    """Write the manifest file."""
    manifest_path = target_root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "source": "navikt/hovmester",
        "source_sha": source_sha,
        "files": sorted(files),
    }
    manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def find_stale_by_manifest(
    target_root: Path, current_files: set[str], manifest_files: list[str]
) -> list[str]:
    """Find files that are in the manifest but no longer in the current file list."""
    stale: list[str] = []
    for rel in manifest_files:
        if rel in current_files:
            continue
        target_path = target_root / rel
        if target_path.exists():
            stale.append(rel)
    return stale


def find_stale_legacy(target_root: Path, current_files: set[str]) -> list[str]:
    """One-time migration: find orphaned files from previous sync tools.

    Only runs when no manifest exists (first sync). After the first successful
    sync writes a manifest, this function is never called again for that repo.
    Can be removed once all consuming repos have completed at least one sync.

    Catches two types of stale files:
    1. Files with 'Managed by esyfo-cli' header (any file type)
    2. Extra files inside skill directories we own (e.g. metadata.json that
       was synced by esyfo-cli but never had a managed header)
    """
    print(
        "INFO: No manifest found — running one-time legacy scan for esyfo-cli files.",
        file=sys.stderr,
    )
    stale: list[str] = []

    # Build set of skill directories we own (based on current files)
    owned_skill_dirs: set[str] = set()
    for rel in current_files:
        if rel.startswith(".github/skills/"):
            parts = rel.replace(".github/skills/", "").split("/")
            if parts:
                owned_skill_dirs.add(f".github/skills/{parts[0]}")

    for scan_dir in DIR_MAPPING.values():
        full_dir = target_root / scan_dir
        if not full_dir.is_dir():
            continue
        for path in full_dir.rglob("*"):
            if path.is_symlink():
                continue
            if not path.is_file():
                continue
            rel = str(path.relative_to(target_root))
            if any(rel.startswith(excl) for excl in EXCLUDED_TARGET_DIRS):
                continue
            if rel in current_files:
                continue

            # Check 1: file has legacy managed header
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                content = ""
            if LEGACY_MARKER in content:
                stale.append(rel)
                continue

            # Check 2: file is inside a skill directory we own but not in our file list
            # (catches metadata.json and other files that never had managed headers)
            if any(rel.startswith(d + "/") for d in owned_skill_dirs):
                stale.append(rel)

    return stale


def _find_extra_files_in_owned_skills(
    target_root: Path, current_files: set[str]
) -> list[str]:
    """Find files in owned skill directories that are not in the current file list.

    Catches files like metadata.json that were synced by previous tools
    but are not tracked by the manifest.
    """
    owned_skill_dirs: set[str] = set()
    for rel in current_files:
        if rel.startswith(".github/skills/"):
            parts = rel.replace(".github/skills/", "").split("/")
            if parts:
                owned_skill_dirs.add(f".github/skills/{parts[0]}")

    extra: list[str] = []
    skills_dir = target_root / ".github" / "skills"
    if not skills_dir.is_dir():
        return extra

    for path in skills_dir.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        rel = str(path.relative_to(target_root))
        if rel in current_files:
            continue
        if any(rel.startswith(d + "/") for d in owned_skill_dirs):
            extra.append(rel)

    return extra


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def apply_sync(
    mapping: dict[str, tuple[Path, str]],
    target_root: Path,
    source_sha: str = "",
    github_project: str = "",
) -> SyncDiff:
    """Apply the full sync: copy new/changed, remove stale, write manifest."""
    migrate_legacy_manifest(target_root)
    diff = compute_diff(mapping, target_root, github_project)
    current_files = set(mapping.keys())

    # Copy added and changed files (via helper so template transforms apply)
    failed: set[str] = set()
    for target_rel in diff.added + diff.changed:
        source_path, source_rel = mapping[target_rel]
        target_path = target_root / target_rel
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = _read_source_content(source_path, source_rel, github_project)
            target_path.write_bytes(content)
        except OSError as e:
            print(f"WARNING: Failed to copy {target_rel}: {e}", file=sys.stderr)
            failed.add(target_rel)

    # Find stale files via manifest or legacy scan
    manifest_files = read_manifest(target_root)
    if manifest_files is not None:
        stale = find_stale_by_manifest(target_root, current_files, manifest_files)
    else:
        stale = find_stale_legacy(target_root, current_files)

    # Always clean up extra files in owned skill directories (e.g. metadata.json
    # that was never in any manifest but lives inside a skill dir we own)
    stale.extend(_find_extra_files_in_owned_skills(target_root, current_files))

    # Deduplicate (manifest and extra-files scan can overlap)
    stale = list(dict.fromkeys(stale))

    for rel in stale:
        try:
            (target_root / rel).unlink(missing_ok=True)
        except OSError as e:
            print(f"WARNING: Failed to remove stale {rel}: {e}", file=sys.stderr)
    diff.removed = stale

    # Clean up empty directories
    for scan_dir in DIR_MAPPING.values():
        full_dir = target_root / scan_dir
        if not full_dir.is_dir():
            continue
        for dirpath in sorted(full_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                try:
                    dirpath.rmdir()
                except OSError:
                    pass

    # Write manifest — exclude files that failed to copy
    write_manifest(target_root, list(current_files - failed), source_sha)

    return diff


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync hovmester files to a target repository."
    )
    parser.add_argument(
        "--source", type=Path, required=True,
        help="Path to the hovmester source checkout.",
    )
    parser.add_argument(
        "--target", type=Path, required=True,
        help="Path to the target repository checkout.",
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="Path to write the JSON result file.",
    )
    parser.add_argument(
        "--source-sha", type=str, default="",
        help="Source commit SHA for manifest metadata.",
    )
    parser.add_argument(
        "--collections", type=str, default=None,
        help="Comma-separated collections to sync (default: all files).",
    )
    parser.add_argument(
        "--exclude", type=str, default=None,
        help="Comma-separated names to exclude (e.g. 'kafka-topic,grill-me').",
    )
    parser.add_argument(
        "--github-project", type=str, default="",
        help="GitHub project reference (e.g. 'navikt/123') for issue template substitution. If empty, the projects line is stripped from templates.",
    )
    args = parser.parse_args()

    source: Path = args.source.resolve()
    target: Path = args.target.resolve()
    output: Path = args.output.resolve()

    if not source.is_dir():
        print(f"ERROR: source directory does not exist: {source}", file=sys.stderr)
        sys.exit(1)
    if not target.is_dir():
        print(f"ERROR: target directory does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    mapping = build_file_mapping(source)

    # Apply collections filter if specified
    allowed = resolve_collections(source, args.collections)
    mapping = filter_mapping_by_collections(mapping, allowed)

    # Apply exclude filter if specified
    mapping = filter_mapping_by_exclude(mapping, args.exclude)

    diff = apply_sync(
        mapping, target, source_sha=args.source_sha, github_project=args.github_project
    )

    result = asdict(diff)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    total_changes = len(diff.added) + len(diff.changed) + len(diff.removed)
    print(
        f"Sync complete: {len(diff.added)} added, {len(diff.changed)} changed, "
        f"{len(diff.removed)} removed, {len(diff.unchanged)} unchanged."
    )
    if total_changes == 0:
        print("No changes — target is up to date.")


if __name__ == "__main__":
    main()
