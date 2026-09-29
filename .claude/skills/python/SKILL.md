---
name: python
description: How Python work is done in this CS 212 project — running code, tests, linting, formatting, adding libraries, the uv/.venv setup and its gotchas, and the professor's style rules. Use whenever writing, running, testing, or reviewing Python here, or when changing dependencies or the environment.
---

# Python in this project

Standard Python packaging (`pyproject.toml` + `.venv`), managed with **uv**. Nothing is uv-only except `uv.lock`, so plain `venv`/`pip` remains a valid escape hatch.

## Environment

- **Python 3.12**, pinned in `.python-version`. Don't bump it: the course's TensorFlow unit needs ≤3.12 (per `course-materials/docs/LectureNotes/SetUpPythonAndLibrariesForAI.md`). Recheck that guide before changing.
- System `python3` is 3.10 — never use it for project code. Go through `uv run` or `.venv/bin/python`.
- The project is not an installable package; lab code is plain scripts.

## Everyday commands

```bash
uv run python lab01/script.py   # run a script
uv run pytest                   # tests (skips course-materials/)
uv run ruff check .             # lint; --fix applies safe fixes
uv run ruff format .            # format
```

After writing or editing Python, run `ruff check` and `ruff format` on the changed files, and pytest if there are tests.

## Dependencies

- Add runtime libraries with `uv add <pkg>`, dev tools with `uv add --dev <pkg>`. Both update `pyproject.toml` and `uv.lock` — commit the two together.
- Add libraries when a unit actually needs them, not ahead of time. The course's stack: numpy, scipy, matplotlib, scikit-learn, tensorflow, pillow, later an LLM SDK (Gemini) and MCP. Check the unit's lecture notes/lab for version pins before adding.
- Never `pip install` into `.venv` while also using `uv run`/`uv sync`: uv syncs the environment to the lock file exactly and **silently removes** anything pip added. If something needs pip (unusual build, experimental install), say so, and either add it through uv or agree with the user to work pip-only for that task.
- If uv itself is the obstacle (its standalone Python builds occasionally trip on tkinter or C-extension builds), stop and tell the user rather than working around it. The user has had trouble with uv on unusual setups and wants to know.

## Style — the professor's checklist

Source: `course-materials/docs/Labs/PythonStyleAndBestPracticesChecklist.md` (update the submodule and re-read it if it may have changed). Ruff config in `pyproject.toml` enforces the mechanical parts:

| Checklist item | Ruff rule |
|---|---|
| imports ordered stdlib → third-party → local | `I` |
| snake_case / PascalCase / ALL_CAPS names | `N` |
| no commented-out code | `ERA` |
| named constants, not magic numbers | `PLR2004` |
| no unused imports/variables | `F` |

Ruff can't check these, so check them when writing or reviewing code:
- Business logic separated from input/output. Put the decision logic in pure functions that take values and return results; keep `input()`/`print()` in a `main()` guarded by `if __name__ == "__main__":`. This also makes the logic testable.
- One job per function; DRY; `@dataclass` for simple data holders; local variables over instance attributes; `_prefix` for internal attributes; composition over needless inheritance.
- Docstrings on modules and non-trivial functions.
- Descriptive snake_case file names.

**Check the deliverable before splitting files.** The checklist suggests logic and CLI in separate modules, but some labs specify an exact file count (Lab 1: one `.py` per program). When the lab fixes the count, separate logic from I/O with functions inside one file instead.

## Graded work

Labs are graded and peer-reviewed. Ask how much help the user wants before writing a lab solution — they may want to write it themselves and have Claude review, set up tests, or explain concepts. For lab requirements, use the `course-materials` skill.
