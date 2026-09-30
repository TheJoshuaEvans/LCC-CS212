# LCC CS 212 — AI Programming 1

Coursework for CS 212 at Lane Community College. The course's own materials (lecture notes, lab instructions, notebooks) are included as a git submodule in [`course-materials/`](course-materials/).

# Spoiler Warning!
This repository contains solutions to many of the assignments in this course!

## Setup

### 1. Install the tools

**git** and **[uv](https://docs.astral.sh/uv/)** are required. Python doesn't need to be installed separately: uv downloads the right version (3.12) for this project by itself.

**Windows**

```powershell
winget install Git.Git
winget install astral-sh.uv
git config --global core.autocrlf true
```

**Linux / macOS**

Install git from your package manager, then:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your system afterwards so the new commands are on your PATH.

### 2. Clone the repo

Include the submodule:

```bash
git clone --recurse-submodules https://github.com/TheJoshuaEvans/LCC-CS212.git
```

If you already cloned without it, or `course-materials/` is empty:

```bash
git submodule update --init
```

### 3. Create the environment

From the project folder:

```bash
uv sync
```

This downloads Python 3.12 if needed, creates `.venv/`, and installs everything listed in `uv.lock`.

### 4. Editor (VS Code)

Install the recommended extensions when VS Code offers them (**Python**, **Ruff**, and **Code Spell Checker**). The Python extension should find `.venv` by itself. If it doesn't, run **Python: Select Interpreter** from the Command Palette and choose `.venv`.

Files are formatted with Ruff on save.

### 5. Canvas access (optional)

The Canvas lookup script used by Claude Code needs a personal API token. It lives in a `.env` file in the project folder, which is gitignored, so you have to create it on each machine:

```
CANVAS_KEY=your_token_here
```

Get a token from Canvas → **Account** → **Settings** → **Approved Integrations** → **+ New Access Token**. Lane's tokens expire after at most 90 days.

## Everyday commands

```bash
uv run python lab01/script.py   # run a script
uv run pytest                   # run tests
uv run ruff check .             # lint (add --fix to apply safe fixes)
uv run ruff format .            # format
uv add <package>                # add a library (updates pyproject.toml and uv.lock)
git submodule update --remote   # pull the latest course materials
```

Use `uv add`, not `pip install`: uv keeps `.venv` matched to `uv.lock` and removes anything installed with pip.

## Troubleshooting

- **`python` opens the Microsoft Store / "Python was not found"**: that's Windows' placeholder command. Use `uv run python` instead.
- **git shows every file as modified, but nothing changed**: a line-ending mismatch. On Windows, run `git config --global core.autocrlf true`. You can confirm the changes are only line endings with `git diff --ignore-cr-at-eol --stat`.
- **`ZoneInfoNotFoundError` on Windows**: Windows has no built-in timezone data. Run `uv sync` to install the `tzdata` package.
- **`uv` or `git` "not recognized" right after installing**: restart the terminal or editor so it picks up the new PATH.
