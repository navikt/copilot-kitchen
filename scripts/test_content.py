# scripts/test_content.py
"""Strukturelle innholdssjekker for dist/skills, dist/agents, dist/instructions."""

import os
import re
import yaml

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
DIST = os.path.join(REPO_ROOT, "dist")
GITHUB = os.path.join(REPO_ROOT, ".github")

# Pre-existing violations som ikke skal blokkere nav-pilot-adopsjon.
# Disse skal splittes opp i egen oppfølging.
LINE_CAP_ALLOWLIST = {"lumi-survey"}  # pre-existing; split in follow-up

# Skills som lever KUN i .github/ (hovmester-repoets egen Copilot-config)
# og ikke i dist/. Disse parity-testen ignorerer.
GITHUB_ONLY_SKILLS = {"copilot-upstream-sync"}


def _iter_md_files(root):
    """Yield (abspath, relpath) for every .md-file under root."""
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".md"):
                abspath = os.path.join(dirpath, fn)
                yield abspath, os.path.relpath(abspath, root)


def test_all_skills_have_valid_frontmatter():
    skills_dir = os.path.join(DIST, "skills")
    for skill_name in os.listdir(skills_dir):
        skill_md = os.path.join(skills_dir, skill_name, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        with open(skill_md, encoding="utf-8") as f:
            content = f.read()
        assert content.startswith("---\n"), f"{skill_name}: missing frontmatter"
        end = content.find("\n---\n", 4)
        assert end > 0, f"{skill_name}: frontmatter not closed"
        fm = yaml.safe_load(content[4:end])
        assert "name" in fm, f"{skill_name}: missing name"
        assert "description" in fm, f"{skill_name}: missing description"
        assert fm["name"] == skill_name, f"{skill_name}: name mismatch ({fm['name']})"


def test_no_duplicate_skill_names():
    """Sjekk at SKILL.md frontmatter-name er unik på tvers av alle skills.

    Katalognavn kan aldri duplisere (filsystemet krever unike), men frontmatter-name
    kan feilaktig sette to skills til samme `name:`-verdi. Det bryter skill-resolveren.
    """
    skills_dir = os.path.join(DIST, "skills")
    frontmatter_names = []
    for skill_name in os.listdir(skills_dir):
        skill_md = os.path.join(skills_dir, skill_name, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        with open(skill_md, encoding="utf-8") as f:
            content = f.read()
        if not content.startswith("---\n"):
            continue
        end = content.find("\n---\n", 4)
        if end <= 0:
            continue
        fm = yaml.safe_load(content[4:end])
        if fm and "name" in fm:
            frontmatter_names.append(fm["name"])
    duplicates = [n for n in frontmatter_names if frontmatter_names.count(n) > 1]
    assert not duplicates, f"duplicate frontmatter names: {sorted(set(duplicates))}"


def test_all_references_exist():
    skills_dir = os.path.join(DIST, "skills")
    ref_pattern = re.compile(r"references/([a-z0-9\-]+\.md)")
    for skill_name in os.listdir(skills_dir):
        skill_md = os.path.join(skills_dir, skill_name, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        with open(skill_md, encoding="utf-8") as f:
            body = f.read()
        for ref_name in ref_pattern.findall(body):
            ref_path = os.path.join(skills_dir, skill_name, "references", ref_name)
            assert os.path.isfile(ref_path), f"{skill_name}: broken reference to references/{ref_name}"


def test_no_agent_refs_in_dist():
    """Scan for deprecated @*-agent-referanser.

    Etter nav-pilot-adopsjon er agent-mention-mønsteret (f.eks. `@nais-agent`,
    `@auth-agent`) avløst av skill-referanser. Disse skal ikke finnes i dist.
    """
    pattern = re.compile(
        r"@(nais|auth|kafka|nav-pilot|observability|aksel|"
        r"security-champion|accessibility|forfatter)-?agent",
        re.IGNORECASE,
    )
    violations = []
    for abspath, relpath in _iter_md_files(DIST):
        with open(abspath, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if pattern.search(line):
                    violations.append(f"{relpath}:{i}: {line.strip()}")
    assert not violations, "deprecated agent-refs:\n" + "\n".join(violations)


def test_no_real_fnr_in_dist():
    """Scan for 11-sifrede tall som ser ut som ekte fnr.

    Placeholder-regel: bruk alltid `00000000000` i eksempler.
    Skatteetatens syntetiske testserie (eksplisitt markert) kan allowlistes
    senere hvis behov oppstår.
    """
    # 11-siffer som starter med 1-9 (ekskluderer 00000000000)
    fnr_pattern = re.compile(r"\b[1-9]\d{10}\b")
    violations = []
    for abspath, relpath in _iter_md_files(DIST):
        with open(abspath, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for match in fnr_pattern.finditer(line):
                    violations.append(f"{relpath}:{i}: {match.group(0)} in: {line.strip()}")
    assert not violations, "possible real fnr (use 00000000000):\n" + "\n".join(violations)


def test_no_unpinned_actions_in_dist():
    """Scan for upinnete GitHub Actions i dist.

    Actions skal pinnes til full commit SHA. Unntak er lines som eksplisitt er
    markert som eksempler (`❌` bad-example-marker, eller kommentar med
    `erstatt` / `example`).
    """
    # Matcher <org>/<repo>@(v<N>|main|master) for alle 3rd-party actions
    # (actions/*, aquasecurity/*, docker/*, osv.).
    # (?<![\w/]) sikrer at sub-paths som "nais/deploy/actions/deploy@v2"
    # ikke dobbelt-matcher. (?!nais/) allowlister nais/*-actions som er
    # dokumentert unntak fra SHA-pinning-kravet.
    action_pattern = re.compile(
        r"(?<![\w/])(?!nais/)[\w.-]+/[\w.-]+@(v\d+|main|master)\b"
    )
    violations = []
    for abspath, relpath in _iter_md_files(DIST):
        with open(abspath, encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if not action_pattern.search(line):
                continue
            low = line.lower()
            if "erstatt" in low or "example" in low:
                continue
            if "\u274c" in line:  # ❌-markert bad example på samme linje
                continue
            # Sjekk opp til 2 foregående linjer for bad-example-marker
            prev_window = "".join(lines[max(0, i - 3) : i - 1])
            if "\u274c" in prev_window:
                continue
            violations.append(f"{relpath}:{i}: {line.strip()}")
    assert not violations, "unpinned actions (pin to SHA):\n" + "\n".join(violations)


def test_skill_line_cap():
    """SKILL.md hard-cap på 200 linjer.

    Innhold som krever mer skal splittes til references/. lumi-survey er
    pre-existing violation (422 linjer) og allowlistet — skal splittes i
    egen follow-up PR.
    """
    skills_dir = os.path.join(DIST, "skills")
    violations = []
    warnings = []
    for skill_name in sorted(os.listdir(skills_dir)):
        if skill_name in LINE_CAP_ALLOWLIST:
            continue
        skill_md = os.path.join(skills_dir, skill_name, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        with open(skill_md, encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        if lines > 200:
            violations.append(f"{skill_name}: {lines} lines (cap: 200)")
        elif lines >= 180:
            warnings.append(f"{skill_name}: {lines} lines (soft-warn at 180+)")
    if warnings:
        print("\nSKILL.md line-count soft-warnings:\n  " + "\n  ".join(warnings))
    assert not violations, "SKILL.md over 200-line cap:\n  " + "\n  ".join(violations)


def _collect_parity_pairs():
    """Yield (dist_abspath, github_abspath, relpath) for hver fil-type som skal speiles."""
    for subtree in ("skills", "agents", "instructions"):
        dist_root = os.path.join(DIST, subtree)
        gh_root = os.path.join(GITHUB, subtree)
        if not os.path.isdir(dist_root):
            continue
        for abspath, relpath in _iter_md_files(dist_root):
            # For skills/, hopp over eventuelle GITHUB_ONLY_SKILLS (skulle ikke
            # treffe på dist-siden, men vi sjekker for framtidig allowlisting).
            parts = relpath.split(os.sep)
            if subtree == "skills" and parts and parts[0] in GITHUB_ONLY_SKILLS:
                continue
            yield abspath, os.path.join(gh_root, relpath), f"{subtree}/{relpath}"


def test_github_mirror_parity_with_dist():
    """Hver fil under dist/{skills,agents,instructions}/ skal ha identisk motpart
    under .github/. Kjør `python3 scripts/sync.py --source . --target .` hvis testen
    feiler. GITHUB_ONLY_SKILLS-allowlisten er for repo-lokale meta-skills som kun
    finnes i .github/."""
    missing = []
    mismatched = []
    for dist_path, gh_path, relpath in _collect_parity_pairs():
        if not os.path.isfile(gh_path):
            missing.append(relpath)
            continue
        with open(dist_path, encoding="utf-8") as a, open(gh_path, encoding="utf-8") as b:
            if a.read() != b.read():
                mismatched.append(relpath)
    problems = []
    if missing:
        problems.append("mangler i .github/:\n  " + "\n  ".join(missing))
    if mismatched:
        problems.append("innhold divergerer fra dist/:\n  " + "\n  ".join(mismatched))
    assert not problems, (
        ".github/-mirror er ikke i sync med dist/. "
        "Kjør: python3 scripts/sync.py --source . --target . "
        "--output /tmp/sync.json --source-sha $(git rev-parse HEAD) "
        "--collections hovmester,backend,frontend\n\n" + "\n\n".join(problems)
    )
