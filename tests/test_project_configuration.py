from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]


def test_ci_workflow_contains_required_course_steps() -> None:
    workflow = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    required_fragments = [
        "push:",
        "pull_request:",
        "actions/checkout@v6",
        "actions/setup-python@v5",
        "python -m pytest",
        "--junitxml=reports/junit-offline.xml",
        "python -m build",
        "actions/upload-artifact@v4",
        "dist/*",
    ]
    for fragment in required_fragments:
        assert fragment in workflow


def test_package_metadata_declares_src_layout_and_readme() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'where = ["src"]' in pyproject
    assert 'readme = "README.md"' in pyproject
    assert 'requires-python = ">=3.11"' in pyproject


def test_generated_evidence_and_packages_are_ignored() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "reports/" in gitignore
    assert "dist/" in gitignore
    assert ".local-packages/" in gitignore
