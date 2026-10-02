---
name: python
description: How Python work is done in this CS 212 project — running code, tests, linting, formatting, adding libraries, the uv/.venv setup and its gotchas, and the professor's style rules. Use whenever writing, running, testing, or reviewing Python here, or when changing dependencies or the environment.
---

# Python in this project

Standard Python packaging (`pyproject.toml` + `.venv`), managed with **uv**. Nothing is uv-only except `uv.lock`, so plain `venv`/`pip` remains a valid escape hatch.

## Environment

- **Python 3.12**, pinned in `.python-version`. Don't bump it: the course's TensorFlow unit needs ≤3.12 (per `course-materials/docs/LectureNotes/SetUpPythonAndLibrariesForAI.md`). Recheck that guide before changing.
- Never use a system Python for project code; it may be the wrong version or missing entirely. Go through `uv run`, which works the same on every machine. If you need the interpreter path: `.venv/bin/python` on Linux/macOS, `.venv\Scripts\python.exe` on Windows.
- The project is not an installable package; lab code is plain scripts.

### Machines

The repo may be cloned on any OS, so keep project files OS-neutral:
- **Paths:** forward slashes work in `uv run` commands and Python code on both. Use `pathlib`, not hard-coded separators.
- **Settings:** don't pin OS-specific paths in `.vscode/settings.json`; the Python extension finds `.venv` by itself.
- **Line endings:** Windows uses `core.autocrlf=true`. If git suddenly shows every file modified with no real changes, check `git diff --ignore-cr-at-eol --stat` before assuming edits.
- **Timezones:** Windows has no system tz database, so `zoneinfo` needs the `tzdata` package (a Windows-only dev dependency here). Add it as a runtime dependency too if lab code ever uses `zoneinfo`.
- **Fresh machine setup:** install uv (Windows: `winget install astral-sh.uv`), then `uv sync`. uv downloads Python 3.12 itself; no separate Python install is needed. The Canvas key in `.env` is gitignored, so it doesn't come with the clone.

## Everyday commands

```bash
uv run python lab01/script.py   # run a script
uv run pytest                   # tests (skips course-materials/)
uv run ruff check .             # lint; --fix applies safe fixes
uv run ruff format .            # format
```

After writing or editing Python, run `ruff check` and `ruff format` on the changed files, and pytest if there are tests.

## Testing

**pytest**, with plain `assert`s and plain test functions (no `unittest` classes). The course doesn't require tests; they're ours, for confidence and for code reviews.

- Put tests next to the code they test, named with a `_test.py` suffix: `lab01/A_shipping_cost.py` → `lab01/A_shipping_cost_test.py`. pytest's default import mode makes `from A_shipping_cost import ...` work from there.
- End every test file with a block that lets it run directly (`uv run python lab01/A_shipping_cost_test.py`, or VS Code's Run button): `if __name__ == "__main__": sys.exit(pytest.main([__file__]))`, with `import sys` at the top. `uv run pytest` ignores the block.
- Test the logic functions, not `input()`/`print()`. That's another reason to keep I/O in `main()`.
- **Rule tables → `@pytest.mark.parametrize`**, one tuple per table row, so every case passes or fails on its own. Spelled `parametrize`; pytest rejects `parameterize`.
- Always include the boundary values (exactly 5 kg, exactly 90 points). Off-by-one mistakes like `<` vs `<=` are the most likely bug in these labs.
- Use `ids=[...]` or `pytest.param(..., id="...")` when the auto-generated IDs aren't readable.
- Test files are **not** part of lab submissions. When a lab specifies exact deliverables, remind the user to upload only those.

## Dependencies

- Add runtime libraries with `uv add <pkg>`, dev tools with `uv add --dev <pkg>`. Both update `pyproject.toml` and `uv.lock` — commit the two together.
- Add libraries when a unit actually needs them, not ahead of time. The course's stack: numpy, scipy, matplotlib, scikit-learn, tensorflow, pillow, later an LLM SDK (Gemini) and MCP. Check the unit's lecture notes/lab for version pins before adding.
- Never `pip install` into `.venv` while also using `uv run`/`uv sync`: uv syncs the environment to the lock file exactly and **silently removes** anything pip added. If something needs pip (unusual build, experimental install), say so, and either add it through uv or agree with the user to work pip-only for that task.
- If uv itself is the obstacle (its standalone Python builds occasionally trip on tkinter or C-extension builds), stop and tell the user rather than working around it, so they can decide how to proceed.

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
