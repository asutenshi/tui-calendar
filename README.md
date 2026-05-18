# 📅 TUI Calendar-Task Manager

An aesthetic and fast terminal-based calendar for those who live in the console and appreciate Vim-style control.

This project combines the convenience of a classic calendar with the flexibility of Markdown notes. All data is stored locally in `.md` files with YAML frontmatter, making the app fully compatible with **Obsidian**, **Logseq**, or your favorite **Vim/Neovim** setup.

## ✨ Key Features

- **Vim-style Navigation**: Move through days and weeks seamlessly using `h`, `j`, `k`, `l`.
- **Markdown-backed**: Every event is a plain-text file. No proprietary databases, no vendor lock-in.
- **Seamless Views**: Switch between Month (grid) and Week (columns) layouts.
- **$EDITOR Integration**: Open and edit your notes instantly in your system's editor (Vim, Nano, etc.).
- **Knowledge Base Ready**: Designed to work as a part of your existing second brain (compatible with Obsidian/Logseq).

## 🛠 Tech Stack

- **Language:** Python 3.12+
- **UI Framework:** [Textual](https://textual.textualize.io/)
- **Data Format:** Markdown (.md) + YAML Frontmatter

## 🚀 Quick Start

> **Note:** This project is currently in the MVP (active development) stage.

1. **Install dependencies:**
   ```bash
   pip install .
   ```

2. **Run the application:**
   ```bash
   tcal
   ```

## ⌨️ Keymap Specification

- `h`, `j`, `k`, `l` — **Navigate** (Left, Down, Up, Right).
- `m`, `w` — **Switch views**: Month / Week.
- `t` — Go to **Today**.
- `n` — Create a **New note** for the selected date.
- `d` — **Delete** focused note.
- `shift + h / l` — **Move note** date (previous/next day).
- `Enter` — **Focus** on a day or **Open** file in your `$EDITOR`.
- `q` — **Quit** application.

## 🤝 Contributing

We welcome contributions! Before you start, please read our [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code style, commit standards, and development workflow.

---
*Inspired by Vim and the spirit of plain-text productivity.*
