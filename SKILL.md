---
name: jupyter-notebook-editor
description: Inspect and edit Jupyter notebook (.ipynb) for listing, reading, updating, deleting, and inserting cells. Use whenever an agent must analyze or modify notebook cell content (e.g., reviewing markdown, tweaking code) with precise, per-cell control.
---

# Overview

Work entirely through `scripts/nb_api.py`, which wraps nbformat so you can safely script atomic edits. Every action targets the notebook path (`--path`) and a cell `id` rather than positional indexes, making operations resilient to reorderings.

Before destructive changes, run `list` to capture current IDs and consider backing up the notebook (copy file or commit).

## Dependencies

- Python 3.9+ and `nbformat` installed in the runtime executing the script (`pip install nbformat` if missing).

## Command Summary

| Task | Command |
| --- | --- |
| List all cells with chosen fields | `python scripts/nb_api.py list --path NOTEBOOK --fields id,type,summary` |
| Read specific fields from a cell | `python scripts/nb_api.py get --path NOTEBOOK --id CELL_ID --fields source` |
| Update a field (source only) | `python scripts/nb_api.py update --path NOTEBOOK --id CELL_ID --field source --content-file edited.md [--dry-run]` |
| Delete a cell | `python scripts/nb_api.py delete --path NOTEBOOK --id CELL_ID [--dry-run]` |
| Insert a new cell | `python scripts/nb_api.py insert --path NOTEBOOK --type markdown --content-file new.md [--before-id TARGET_ID] [--dry-run]` |

All commands accept `--dry-run` when you want to preview changes without writing.

## Usage Notes

1. **Capture IDs first**  
   Run `list` with tailored fields (defaults: `id,type,summary`). Special field `summary` renders a trimmed, newline-flattened preview. `type` automatically maps to nbformat's `cell_type`.

2. **Selective reads**  
   `get` limits output via `--fields id,type,source,...`. Avoid dumping large outputs into context unless necessary.

3. **Editing cell source**  
   `update` only supports `source`. Provide new text via either `--content "..."` (wrap multiline strings with shell heredocs) or `--content-file PATH`. The script normalizes newline endings and writes back using nbformat to keep metadata intact.

4. **Insertion semantics**  
   `insert` creates a new cell with a fresh UUID. Use `--before-id CELL_ID` to place it ahead of an existing cell; omit to append at the end. Supported `--type` values: `markdown` or `code`.

5. **Safety**  
   Combine `--dry-run` with delete/update/insert to preview the operation, then rerun without the flag to apply. Always keep a backup or rely on version control before large batches.

## References

- `references/nbformat-cheatsheet.md` — quick reminders on notebook/cell structure, common fields, and useful links to nbformat docs.

