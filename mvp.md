# MVP: TUI Calendar-Task Manager (Vim-style, Markdown-backed & Sync)

## 1. Introduction
An aesthetic and fast terminal application (TUI) built with Python. It is a hybrid between a calendar and a note manager, where data is stored in local Markdown files with YAML frontmatter. The system is fully compatible with Obsidian/Logseq.

## 2. Problem and Solution
**Problem:** Existing calendars are either closed ecosystems (Google/Apple) or too primitive. It is difficult to combine personal Markdown notes with external schedules (iCal) within a single Vim-friendly interface.
**Solution:** A TUI aggregator that indexes local folders and cloud subscriptions, displaying everything on a single grid. Navigation and control are strictly keyboard-driven (Vim-style).

## 3. MVP Goals
* Create a seamless TUI interface (Month/Week/Day views).
* Implement parsing of local `.md` files based on the `date` YAML property.
* Ensure quick invocation of the system `$EDITOR` (Vim/Neovim/Nano).

## 4. Mandatory Functions (Scope)

**4.1. Interface (TUI):**
* **Views:** Month (grid), Week (columns).
* **Navigation:** `h`, `j`, `k`, `l` for movement; `m`, `w`, for switching views; `Enter` to browse throw notes in day.
* **Input:** `n` — create a new note with auto-filled YAML date. `d` — delete focused note. `shift+h/l` — change note date. `Enter` — open file in `$EDITOR`.

**4.2. Core Logic:**
* **Indexing:** Scanning the directory and building an event map in RAM.
* **Markdown Engine:** Reading/writing YAML frontmatter (date, tags, status).
* **Watcher:** Automatic interface refresh when files are modified externally.

## 5. Team Roles

### Role 1: UI/UX Developer (Frontend TUI)
* **Stack:** Python, Textual.
* **Tasks:** Rendering the interface, handling hotkeys, animations, integration with the terminal and editor.

### Role 2: Core Developer (Engine & Logic)
* **Stack:** Python, python-frontmatter, PyYAML, Pydantic.
* **Tasks:** File indexer, metadata search, event filtering logic, local storage and caching, iCal subscription processing.

### Role 3: Tech Lead / Product Owner
* **Stack**: GitHub (Projects/Issues), Project Architecture, Markdown.
* **Tasks**: System architecture design (Data Specs), task decomposition and prioritization, code review (QA), milestone management, and high-level technical guidance.

## 6. Tech Stack
* **Language:** Python 3.10+ (core).
* **UI:** Textual (TUI framework).
* **Data Format:** Markdown (.md) + YAML.

## 7. Definition of Done
1. The application correctly displays local notes on the calendar grid.
2. File creation via `c` and opening in `$EDITOR` works correctly.
3. The client application can be installed via pip or another package manager.

## 8. Keymap Specification
* `h`, `j`, `k`, `l` — Navigation (Left, Down, Up, Right).
* `m`, `w`, — Switch views: Month / Week.
* `t` — Go to Today.
* `n` — New note for the selected date.
* `d` — Delete focused note.
* `Enter` — Focus on a day or open a file in the editor.
* `q` — Quit application.
* `shift+h/l` — Change note date.

## 9. Release Plan

*   **Stage 0: Contracts & Specs.** 
    *   Agreement on the YAML schema (required fields).
    *   Creation of a `dummy_notes/` set (test files) for development.
    *   Defining the data exchange interface between `core` and `ui`.

*   **Stage 1: Read-only MVP.** 
    *   Core: Folder indexing, YAML parsing, data validation.
    *   UI: Rendering the grid (Month/Week) and event list.

*   **Stage 2: Interactive MVP.** 
    *   Integration with `$EDITOR`.
    *   Logic for creating new files (`c` / `n`) and navigation hotkeys.

*   **Stage 3: Integration & External Data.** 
    *   Support for iCal links (local or server-side parsing).

*   **Stage 4: Polishing & Distribution.** 
    *   Final testing, fixing TUI bugs (rendering artifacts).
    *   Documentation (README) and package publication (pip/PyPI).
