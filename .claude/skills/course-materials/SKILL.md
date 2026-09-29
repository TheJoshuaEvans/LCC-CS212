---
name: course-materials
description: Look up anything about CS 212 (AI Programming 1 at Lane CC) — lab instructions, lecture notes, readings, syllabus, rubrics, due dates, quizzes, announcements, Canvas pages. Use whenever the user asks what a lab/unit/assignment requires, what's due, what the professor said, or needs course context before writing code. Also covers updating the course-materials submodule.
---

# CS 212 course materials

Two sources. The professor (Brian Bird) writes content in the GitHub repo; Canvas holds the schedule, due dates, pages, and announcements, and links out to the repo's published site.

## 1. `course-materials/` — the professor's repo (git submodule)

Upstream: https://github.com/lcc-cit/CS212-CourseMaterials, published at https://lcc-cit.github.io/CS212-CourseMaterials/. Search it locally with Grep/Glob/Read — no network needed.

**Update first** when the question is about current work (the professor iterates often):
```bash
git submodule update --remote course-materials
```
If that moved the pointer, tell the user; they may want to commit it (`git commit -m "Update course materials" course-materials`).

**Published URL → local file:** `https://lcc-cit.github.io/CS212-CourseMaterials/<path>.html` → `course-materials/docs/<path>.md`. Canvas links to these URLs, so resolve them locally instead of fetching.

Layout:
- `docs/CS212_Syllabus.md`, `CS212_CourseOutline.md`, `CS212_GettingStartedGuide.md`, `ReadingAssignments.md`
- `docs/LectureNotes/CS212-UnitNN-*.md` — per-unit notes; `-0-Overview` files have the weekly overview. Also `SetUpPythonAndLibrariesForAI.md`, `PythonCodingStyleCheatSheet.md`, `MathReviewForAI.md`. `FutureTopics/` is not current coursework.
- `docs/Labs/LabNN-*/Group{A,B,C}/` — per-group lab instructions and starter code; shared files (rubrics, code review forms) sit one level up. `CodeReviewProcedure.md` and `PythonStyleAndBestPracticesChecklist.md` apply to every lab.
- `docs/Labs/TermProject/` — requirements, presentation guide, rubric.
- `Tutorials/scikit-learn-1.7/`, `JupyterNotebooks/`, `ResearchNotes/` — supporting material.

Files named `*-old`, `*-draft`, `*_Draft`, or `.html` copies inside other labs' folders are stale or in progress; prefer the `.md` in the matching folder and mention it if only a draft exists.

### Lab numbers differ between Canvas and the repo

Canvas has no Lab 3, so from Lab 4 on each Canvas number is one higher than the repo folder:

| Canvas | Repo folder |
|---|---|
| Lab 1 | `Lab01-Python` |
| Lab 2 | `Lab02-RuleBasedSystems` |
| Lab 4 | `Lab03-TextClassification` |
| Lab 5 | `Lab04-ANN` |
| Lab 6 | `Lab05-AI-Coding` |
| Lab 7 | `Lab06-ChatCompletion` |
| Lab 8 | `Lab07-MCP` |

The user speaks in Canvas numbers. Verify against the Canvas module links if this table seems off — it may change.

Some lab instructions are Canvas pages, not repo links (currently Lab 4 Versions B/C, Labs 6–8). Check `modules` for the item type: for a `Page`, read it with `canvas.py page <slug>`, and compare with the repo version, since they can differ.

## 2. Canvas — course 3948 at canvas.lanecc.edu

Use the bundled read-only script (it loads `CANVAS_KEY` from the project `.env` and never prints it):

```bash
python3 .claude/skills/course-materials/scripts/canvas.py <command>
```

| Command | Gives |
|---|---|
| `assignments` | every assignment with id, due date (Pacific), points |
| `assignment <id>` | one assignment's description as text |
| `modules` | module structure with each item's page slug or external URL |
| `page <slug-or-title>` | a Canvas wiki page as text |
| `announcements` | recent announcements |
| `syllabus` | Canvas syllabus body |
| `get <path>` | raw JSON for any GET under `/courses/3948` (e.g. `/quizzes`, `/files`) |

**The key expires.** Lane's Canvas tokens last at most 90 days (this one was working on 2026-09-29, so expect expiry no later than about 2026-12-28 — near the end of term). An expired or revoked key makes the script exit with `CANVAS AUTH FAILED (401)`. When you see that, stop retrying and tell the user to renew: Canvas → Account → Settings → Approved Integrations → + New Access Token, then replace `CANVAS_KEY` in `.env`. A 403 or 404 is a permissions or path problem, not an expired key.

Rules:
- **Read only.** Never submit, post, or modify anything on Canvas — the key acts as the user.
- Never echo, log, or pass the key on a command line; go through the script.
- Canvas due dates are what count. If they disagree with dates in the repo, trust Canvas and point out the mismatch.

## The user

- Lab group (A/B/C): unknown yet. Once the user says, note it here so lab lookups can go straight to their group's folder.
- Lab workflow: beta posted to team Discord → peer code review (submitted on Canvas) → production version with the partner's review, "Prod." column filled in.
