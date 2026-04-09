"""Tests for sync.py — hovmester file sync logic."""

from __future__ import annotations

import json
from pathlib import Path

from sync import (
    LEGACY_MARKER,
    MANIFEST_PATH,
    SyncDiff,
    apply_sync,
    build_file_mapping,
    compute_diff,
    filter_mapping_by_collections,
    filter_mapping_by_exclude,
    find_stale_by_manifest,
    find_stale_legacy,
    read_manifest,
    resolve_collections,
    write_manifest,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_source(root: Path) -> Path:
    """Create a minimal source tree for testing."""
    _write(root / "dist" / "agents" / "bot.agent.md", "agent content")
    _write(root / "dist" / "instructions" / "kotlin.instructions.md", "instructions")
    _write(root / "dist" / "skills" / "tdd" / "SKILL.md", "skill")
    _write(root / "dist" / "skills" / "tdd" / "references" / "examples.md", "examples")
    _write(root / "dist" / "issue-templates" / "bug.yml", "bug template")
    _write(root / "dist" / "PULL_REQUEST_TEMPLATE.md", "pr template")
    return root


# ---------------------------------------------------------------------------
# build_file_mapping
# ---------------------------------------------------------------------------


class TestBuildFileMapping:
    def test_maps_agents(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        assert ".github/agents/bot.agent.md" in mapping

    def test_maps_skills_recursively(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        assert ".github/skills/tdd/SKILL.md" in mapping
        assert ".github/skills/tdd/references/examples.md" in mapping

    def test_excludes_workflows(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        assert not any(k.startswith(".github/workflows") for k in mapping)

    def test_maps_issue_templates(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        assert ".github/ISSUE_TEMPLATE/bug.yml" in mapping

    def test_maps_pr_template(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        assert ".github/PULL_REQUEST_TEMPLATE.md" in mapping


# ---------------------------------------------------------------------------
# compute_diff
# ---------------------------------------------------------------------------


class TestComputeDiff:
    def test_detects_new_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src" / "new.md"
        tgt = tmp_path / "tgt"
        _write(src, "new")
        tgt.mkdir()
        diff = compute_diff(
            {".github/agents/new.md": (src, "dist/agents/new.md")}, tgt
        )
        assert ".github/agents/new.md" in diff.added

    def test_detects_changed_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src" / "a.md"
        tgt = tmp_path / "tgt"
        _write(src, "v2")
        _write(tgt / ".github" / "agents" / "a.md", "v1")
        diff = compute_diff(
            {".github/agents/a.md": (src, "dist/agents/a.md")}, tgt
        )
        assert ".github/agents/a.md" in diff.changed

    def test_skips_unchanged_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src" / "a.md"
        tgt = tmp_path / "tgt"
        _write(src, "same")
        _write(tgt / ".github" / "agents" / "a.md", "same")
        diff = compute_diff(
            {".github/agents/a.md": (src, "dist/agents/a.md")}, tgt
        )
        assert ".github/agents/a.md" in diff.unchanged
        assert not diff.added and not diff.changed


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class TestManifest:
    def test_write_and_read_manifest(self, tmp_path: Path) -> None:
        write_manifest(tmp_path, [".github/agents/a.md"], source_sha="abc123")
        files = read_manifest(tmp_path)
        assert files == [".github/agents/a.md"]

    def test_read_manifest_returns_none_when_missing(self, tmp_path: Path) -> None:
        assert read_manifest(tmp_path) is None

    def test_read_manifest_returns_none_when_corrupt(self, tmp_path: Path) -> None:
        _write(tmp_path / MANIFEST_PATH, "not json{{{")
        assert read_manifest(tmp_path) is None

    def test_find_stale_by_manifest(self, tmp_path: Path) -> None:
        _write(tmp_path / ".github" / "agents" / "old.md", "old")
        stale = find_stale_by_manifest(
            tmp_path,
            current_files={".github/agents/new.md"},
            manifest_files=[".github/agents/old.md", ".github/agents/new.md"],
        )
        assert ".github/agents/old.md" in stale
        assert ".github/agents/new.md" not in stale

    def test_find_stale_by_manifest_ignores_already_deleted(self, tmp_path: Path) -> None:
        # File in manifest but doesn't exist on disk — should not be in stale
        stale = find_stale_by_manifest(
            tmp_path,
            current_files=set(),
            manifest_files=[".github/agents/gone.md"],
        )
        assert stale == []


# ---------------------------------------------------------------------------
# Legacy migration
# ---------------------------------------------------------------------------


class TestLegacyMigration:
    def test_finds_orphaned_legacy_file(self, tmp_path: Path) -> None:
        _write(
            tmp_path / ".github" / "agents" / "old.agent.md",
            f"<!-- {LEGACY_MARKER} -->\nold agent",
        )
        stale = find_stale_legacy(tmp_path, current_files=set())
        assert ".github/agents/old.agent.md" in stale

    def test_ignores_unmanaged_file(self, tmp_path: Path) -> None:
        _write(
            tmp_path / ".github" / "agents" / "custom.md",
            "No managed marker here",
        )
        stale = find_stale_legacy(tmp_path, current_files=set())
        assert stale == []

    def test_ignores_current_files(self, tmp_path: Path) -> None:
        _write(
            tmp_path / ".github" / "agents" / "active.md",
            f"<!-- {LEGACY_MARKER} -->\nactive agent",
        )
        stale = find_stale_legacy(
            tmp_path, current_files={".github/agents/active.md"}
        )
        assert stale == []

    def test_catches_extra_files_in_owned_skill_dirs(self, tmp_path: Path) -> None:
        # We own the "tdd" skill (SKILL.md is in current_files)
        # metadata.json is NOT in current_files and has no managed header
        _write(tmp_path / ".github" / "skills" / "tdd" / "SKILL.md", "skill")
        _write(tmp_path / ".github" / "skills" / "tdd" / "metadata.json", '{"no": "header"}')
        stale = find_stale_legacy(
            tmp_path,
            current_files={".github/skills/tdd/SKILL.md"},
        )
        assert ".github/skills/tdd/metadata.json" in stale

    def test_ignores_extra_files_in_unowned_skill_dirs(self, tmp_path: Path) -> None:
        # We do NOT own "custom-skill" — it's not in current_files at all
        _write(tmp_path / ".github" / "skills" / "custom-skill" / "SKILL.md", "custom")
        _write(tmp_path / ".github" / "skills" / "custom-skill" / "notes.md", "notes")
        stale = find_stale_legacy(tmp_path, current_files=set())
        assert stale == []

    def test_never_touches_workflows(self, tmp_path: Path) -> None:
        _write(
            tmp_path / ".github" / "workflows" / "old.yml",
            f"# {LEGACY_MARKER}\nname: old",
        )
        stale = find_stale_legacy(tmp_path, current_files=set())
        assert stale == []


# ---------------------------------------------------------------------------
# apply_sync (integration)
# ---------------------------------------------------------------------------


class TestApplySync:
    def test_copies_new_files_and_writes_manifest(self, tmp_path: Path) -> None:
        source = tmp_path / "src"
        target = tmp_path / "tgt"
        _make_source(source)
        target.mkdir()

        mapping = build_file_mapping(source)
        diff = apply_sync(mapping, target)

        assert len(diff.added) > 0
        for rel in diff.added:
            assert (target / rel).exists()

        # Manifest should exist
        manifest_files = read_manifest(target)
        assert manifest_files is not None
        assert ".github/agents/bot.agent.md" in manifest_files

    def test_deletes_stale_file_via_legacy_scan(self, tmp_path: Path) -> None:
        source = tmp_path / "src"
        target = tmp_path / "tgt"
        _make_source(source)

        # No manifest → first run → legacy scan
        orphan = target / ".github" / "agents" / "removed.agent.md"
        _write(orphan, f"<!-- {LEGACY_MARKER} -->\nwill be removed")

        mapping = build_file_mapping(source)
        diff = apply_sync(mapping, target)

        assert ".github/agents/removed.agent.md" in diff.removed
        assert not orphan.exists()

    def test_deletes_stale_file_via_manifest(self, tmp_path: Path) -> None:
        source = tmp_path / "src"
        target = tmp_path / "tgt"
        _make_source(source)
        target.mkdir()

        # Pre-existing manifest with a file that's no longer in source
        _write(
            target / ".github" / "agents" / "old.agent.md",
            "old content",
        )
        write_manifest(
            target,
            [".github/agents/bot.agent.md", ".github/agents/old.agent.md"],
        )

        mapping = build_file_mapping(source)
        diff = apply_sync(mapping, target)

        assert ".github/agents/old.agent.md" in diff.removed
        assert not (target / ".github" / "agents" / "old.agent.md").exists()

    def test_preserves_unmanaged_file(self, tmp_path: Path) -> None:
        source = tmp_path / "src"
        target = tmp_path / "tgt"
        _make_source(source)

        custom = target / ".github" / "agents" / "custom.md"
        _write(custom, "Team's own agent — no managed marker")

        mapping = build_file_mapping(source)
        diff = apply_sync(mapping, target)

        assert custom.exists()
        assert ".github/agents/custom.md" not in diff.removed

    def test_second_sync_uses_manifest(self, tmp_path: Path) -> None:
        source = tmp_path / "src"
        target = tmp_path / "tgt"
        _make_source(source)
        target.mkdir()

        # First sync — creates manifest
        mapping = build_file_mapping(source)
        apply_sync(mapping, target)
        assert read_manifest(target) is not None

        # Second sync — should use manifest, not legacy scan
        diff2 = apply_sync(mapping, target)
        assert diff2.removed == []
        assert len(diff2.unchanged) > 0


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

COLLECTIONS_YML = """\
hovmester:
  agents:
    - hovmester
    - kokk
  instructions:
    - security
  skills:
    - brainstorm
    - tdd
  issue_templates:
    - bug
  pull_request_template: PULL_REQUEST_TEMPLATE.md

backend:
  instructions:
    - kotlin
  skills:
    - kafka-topic
    - api-design

frontend:
  skills:
    - aksel-design
    - accessibility
"""


class TestCollections:
    def _make_full_source(self, root: Path) -> Path:
        """Source with files matching the collections above."""
        _write(root / "collections.yml", COLLECTIONS_YML)
        _write(root / "dist" / "agents" / "hovmester.agent.md", "hovmester")
        _write(root / "dist" / "agents" / "kokk.agent.md", "kokk")
        _write(root / "dist" / "agents" / "konditor.agent.md", "konditor")  # NOT in hovmester
        _write(root / "dist" / "instructions" / "security.instructions.md", "security")
        _write(root / "dist" / "instructions" / "kotlin.instructions.md", "kotlin")
        _write(root / "dist" / "skills" / "brainstorm" / "SKILL.md", "brainstorm")
        _write(root / "dist" / "skills" / "tdd" / "SKILL.md", "tdd")
        _write(root / "dist" / "skills" / "kafka-topic" / "SKILL.md", "kafka")
        _write(root / "dist" / "skills" / "api-design" / "SKILL.md", "api")
        _write(root / "dist" / "skills" / "aksel-design" / "SKILL.md", "aksel")
        _write(root / "dist" / "skills" / "aksel-design" / "references" / "tokens.md", "tokens")
        _write(root / "dist" / "skills" / "accessibility" / "SKILL.md", "a11y")
        _write(root / "dist" / "issue-templates" / "bug.yml", "bug")
        _write(root / "dist" / "issue-templates" / "feature.yml", "feature")  # NOT in hovmester
        _write(root / "dist" / "PULL_REQUEST_TEMPLATE.md", "pr template")
        return root

    def test_no_collections_returns_all_files(self, tmp_path: Path) -> None:
        source = self._make_full_source(tmp_path)
        mapping = build_file_mapping(source)
        allowed = resolve_collections(source, None)
        filtered = filter_mapping_by_collections(mapping, allowed)
        assert len(filtered) == len(mapping)

    def test_hovmester_only(self, tmp_path: Path) -> None:
        source = self._make_full_source(tmp_path)
        mapping = build_file_mapping(source)
        allowed = resolve_collections(source, "hovmester")
        filtered = filter_mapping_by_collections(mapping, allowed)

        # Should have hovmester agents but NOT konditor
        assert ".github/agents/hovmester.agent.md" in filtered
        assert ".github/agents/kokk.agent.md" in filtered
        assert ".github/agents/konditor.agent.md" not in filtered

        # Should have hovmester skills but NOT backend/frontend skills
        assert ".github/skills/brainstorm/SKILL.md" in filtered
        assert ".github/skills/kafka-topic/SKILL.md" not in filtered
        assert ".github/skills/aksel-design/SKILL.md" not in filtered

        # Should have hovmester instructions but NOT kotlin
        assert ".github/instructions/security.instructions.md" in filtered
        assert ".github/instructions/kotlin.instructions.md" not in filtered

        # Should have hovmester issue templates but NOT feature
        assert ".github/ISSUE_TEMPLATE/bug.yml" in filtered
        assert ".github/ISSUE_TEMPLATE/feature.yml" not in filtered

        # PR template
        assert ".github/PULL_REQUEST_TEMPLATE.md" in filtered

    def test_hovmester_backend(self, tmp_path: Path) -> None:
        source = self._make_full_source(tmp_path)
        mapping = build_file_mapping(source)
        allowed = resolve_collections(source, "hovmester,backend")
        filtered = filter_mapping_by_collections(mapping, allowed)

        # Backend skills included
        assert ".github/skills/kafka-topic/SKILL.md" in filtered
        assert ".github/skills/api-design/SKILL.md" in filtered
        # Backend instruction included
        assert ".github/instructions/kotlin.instructions.md" in filtered
        # Frontend skills NOT included
        assert ".github/skills/aksel-design/SKILL.md" not in filtered

    def test_hovmester_frontend(self, tmp_path: Path) -> None:
        source = self._make_full_source(tmp_path)
        mapping = build_file_mapping(source)
        allowed = resolve_collections(source, "hovmester,frontend")
        filtered = filter_mapping_by_collections(mapping, allowed)

        # Frontend skills included (with references)
        assert ".github/skills/aksel-design/SKILL.md" in filtered
        assert ".github/skills/aksel-design/references/tokens.md" in filtered
        assert ".github/skills/accessibility/SKILL.md" in filtered
        # Backend NOT included
        assert ".github/skills/kafka-topic/SKILL.md" not in filtered

    def test_hovmester_always_implicit(self, tmp_path: Path) -> None:
        source = self._make_full_source(tmp_path)
        mapping = build_file_mapping(source)
        # Only specify "backend" — hovmester should be included implicitly
        allowed = resolve_collections(source, "backend")
        filtered = filter_mapping_by_collections(mapping, allowed)

        assert ".github/agents/hovmester.agent.md" in filtered  # from hovmester
        assert ".github/skills/kafka-topic/SKILL.md" in filtered  # from backend


# ---------------------------------------------------------------------------
# Exclude
# ---------------------------------------------------------------------------


class TestExclude:
    def test_no_exclude_returns_all(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        filtered = filter_mapping_by_exclude(mapping, None)
        assert len(filtered) == len(mapping)

    def test_exclude_skill_removes_all_files(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        filtered = filter_mapping_by_exclude(mapping, "tdd")
        assert ".github/skills/tdd/SKILL.md" not in filtered
        assert ".github/skills/tdd/references/examples.md" not in filtered
        # Other files still present
        assert ".github/agents/bot.agent.md" in filtered

    def test_exclude_agent(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        filtered = filter_mapping_by_exclude(mapping, "bot")
        assert ".github/agents/bot.agent.md" not in filtered
        assert ".github/skills/tdd/SKILL.md" in filtered

    def test_exclude_instruction(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        filtered = filter_mapping_by_exclude(mapping, "kotlin")
        assert ".github/instructions/kotlin.instructions.md" not in filtered

    def test_exclude_multiple(self, tmp_path: Path) -> None:
        _make_source(tmp_path)
        mapping = build_file_mapping(tmp_path)
        filtered = filter_mapping_by_exclude(mapping, "tdd,bot")
        assert ".github/skills/tdd/SKILL.md" not in filtered
        assert ".github/agents/bot.agent.md" not in filtered
        assert ".github/instructions/kotlin.instructions.md" in filtered

    def test_exclude_with_collections(self, tmp_path: Path) -> None:
        """Exclude is applied after collections — can narrow further."""
        source = tmp_path / "src"
        _write(source / "collections.yml", COLLECTIONS_YML)
        _write(source / "dist" / "agents" / "hovmester.agent.md", "h")
        _write(source / "dist" / "agents" / "kokk.agent.md", "k")
        _write(source / "dist" / "skills" / "brainstorm" / "SKILL.md", "b")
        _write(source / "dist" / "skills" / "tdd" / "SKILL.md", "t")
        _write(source / "dist" / "skills" / "kafka-topic" / "SKILL.md", "kf")
        _write(source / "dist" / "instructions" / "security.instructions.md", "s")
        _write(source / "dist" / "instructions" / "kotlin.instructions.md", "kt")
        _write(source / "dist" / "issue-templates" / "bug.yml", "bug")
        _write(source / "dist" / "PULL_REQUEST_TEMPLATE.md", "pr")

        mapping = build_file_mapping(source)
        allowed = resolve_collections(source, "hovmester,backend")
        mapping = filter_mapping_by_collections(mapping, allowed)
        mapping = filter_mapping_by_exclude(mapping, "kafka-topic")

        assert ".github/skills/brainstorm/SKILL.md" in mapping  # hovmester
        assert ".github/skills/kafka-topic/SKILL.md" not in mapping  # excluded


# ---------------------------------------------------------------------------
# Template transform
# ---------------------------------------------------------------------------


class TestTransformIssueTemplate:
    def test_substitutes_placeholder_when_project_set(self) -> None:
        from sync import transform_issue_template

        content = 'name: Bug\nprojects: ["${GITHUB_PROJECT}"]\nbody:\n  - ...\n'
        result = transform_issue_template(content, "navikt/123")
        assert 'projects: ["navikt/123"]' in result
        assert "${GITHUB_PROJECT}" not in result

    def test_strips_projects_line_when_project_empty(self) -> None:
        from sync import transform_issue_template

        content = 'name: Bug\nprojects: ["${GITHUB_PROJECT}"]\nbody:\n  - ...\n'
        result = transform_issue_template(content, "")
        assert "projects:" not in result
        assert "name: Bug" in result
        assert "body:" in result

    def test_preserves_surrounding_content(self) -> None:
        from sync import transform_issue_template

        content = 'name: Bug\ndescription: Report a bug\nprojects: ["${GITHUB_PROJECT}"]\ntype: Bug\n'
        result = transform_issue_template(content, "navikt/999")
        assert "name: Bug" in result
        assert "description: Report a bug" in result
        assert "type: Bug" in result
        assert 'projects: ["navikt/999"]' in result

    def test_no_placeholder_content_unchanged(self) -> None:
        from sync import transform_issue_template

        content = "name: Bug\ndescription: Plain template without projects line\n"
        result = transform_issue_template(content, "navikt/123")
        assert result == content


# ---------------------------------------------------------------------------
# Source content reading
# ---------------------------------------------------------------------------


class TestReadSourceContent:
    def test_reads_non_template_unchanged(self, tmp_path: Path) -> None:
        from sync import _read_source_content

        src = tmp_path / "agent.md"
        src.write_bytes(b"# hovmester\nsome content\n")
        result = _read_source_content(src, "dist/agents/hovmester.agent.md", "navikt/123")
        assert result == b"# hovmester\nsome content\n"

    def test_transforms_issue_template_with_project(self, tmp_path: Path) -> None:
        from sync import _read_source_content

        src = tmp_path / "bug.yml"
        src.write_text(
            'name: Bug\nprojects: ["${GITHUB_PROJECT}"]\n', encoding="utf-8"
        )
        result = _read_source_content(src, "dist/issue-templates/bug.yml", "navikt/999")
        assert b'projects: ["navikt/999"]' in result
        assert b"${GITHUB_PROJECT}" not in result

    def test_strips_template_projects_when_empty(self, tmp_path: Path) -> None:
        from sync import _read_source_content

        src = tmp_path / "bug.yml"
        src.write_text(
            'name: Bug\nprojects: ["${GITHUB_PROJECT}"]\nbody:\n', encoding="utf-8"
        )
        result = _read_source_content(src, "dist/issue-templates/bug.yml", "")
        assert b"projects:" not in result
        assert b"name: Bug" in result
        assert b"body:" in result

    def test_yaml_templates_transformed(self, tmp_path: Path) -> None:
        """Both .yml and .yaml extensions are supported."""
        from sync import _read_source_content

        src = tmp_path / "feature.yaml"
        src.write_text(
            'name: Feature\nprojects: ["${GITHUB_PROJECT}"]\n', encoding="utf-8"
        )
        result = _read_source_content(src, "dist/issue-templates/feature.yaml", "navikt/42")
        assert b'projects: ["navikt/42"]' in result

    def test_pr_template_not_transformed(self, tmp_path: Path) -> None:
        """Files outside dist/issue-templates/ are returned as-is even if they contain the placeholder."""
        from sync import _read_source_content

        src = tmp_path / "PULL_REQUEST_TEMPLATE.md"
        src.write_bytes(b"# PR\nProjects: ${GITHUB_PROJECT} (should not change)\n")
        result = _read_source_content(src, "dist/PULL_REQUEST_TEMPLATE.md", "navikt/123")
        assert b"${GITHUB_PROJECT}" in result
