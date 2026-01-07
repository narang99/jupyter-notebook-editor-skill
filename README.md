# Jupyter Notebook Editor Skill

A codex skill to interact with jupyter notebooks. I was using codex for reviewing my jupyter notebooks for grammar and it had a lot of difficulty in working with the format (reading or editing cells in the notebook).  
This skill allows codex to use a packaged script to work with notebooks (allowing it to read/list/write specific cells).  

Example prompt that can work after you install this skill
```
Review this jupyter notebook <file> for grammar in markdown cells
```

## Installation
Clone this repository in your `~/.codex/skills` directory.  

## Requirements
- Python 3.9+
- [`nbformat`](https://nbformat.readthedocs.io/) (install with `pip install nbformat`)


## Repository Layout
- `jupyter-notebook-editor/SKILL.md` – authoritative instructions for agents using the skill.
- `jupyter-notebook-editor/scripts/nb_api.py` – CLI used for listing, reading, updating, deleting, and inserting notebook cells.
- `jupyter-notebook-editor/references/` – cheatsheets and worked examples covering common notebook operations and nbformat tips.

## Basic Usage
All notebook interactions run through `scripts/nb_api.py`:

```bash
python jupyter-notebook-editor/scripts/nb_api.py <command> [options]
```

Key commands:
- `list` – enumerate cells, optionally filtering by `--cell-type markdown|code` and selecting fields via `--fields`.
- `get` – fetch a specific cell by `--id`.
- `update` – change a single field (commonly `source`) on a specific cell.
- `insert` – add a code or markdown cell, optionally placing it before another cell ID.
- `delete` – remove a cell by ID.

Most commands support `--truncate` to control how much of each field prints and `--dry-run` for previewing changes.
