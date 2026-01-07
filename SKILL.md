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

Concise usage help instructions for the script
- nb_api.py [-h] {list,get,update,delete,insert} ...

- nb_api.py get [-h] --path PATH --id ID_TO_GET --fields COMMA_SEPARATED_FIELDS [--truncate TRUNCATE]
- nb_api.py update [-h] --path PATH --id ID_TO_UPDATE --field SINGLE_FIELD_TO_UPDATE [--content CONTENT] [--content-file CONTENT_FILE] [--dry-run]
- nb_api.py delete [-h] --path PATH --id ID_TO_DELETE [--dry-run] [--truncate TRUNCATE]
- nb_api.py list [-h] --path PATH --fields COMMA_SEPARATED_FIELDS [--truncate TRUNCATE]
- nb_api.py insert [-h] --path PATH [--before-id BEFORE_ID] --type {markdown,code} [--content CONTENT] [--content-file CONTENT_FILE] [--dry-run]
  - Cell would be inserted before the cell with ID = BEFORE_ID. If no --before-id provided, append


## Usage Notes

Important usage tips
- **Truncate output generally**: Every reading operation (list, get, etc) takes a `--truncate` flag with default value of 100. It would truncate the output of each field inside each cell to the character limit. If you want to read the whole field, use `--truncate -1`.  
- **Always pass fields**. Make sure you do selective reads. 
- The commands print JSON output when successful.  
- All commands accept `--dry-run` when you want to preview changes without writing.
- If a command takes user input, it would be done using either `--content` or `--content-file`, use one of them
- **Avoid reading output field unless relevant** (output can clutter and eat up context).
- If you expect doing bulk updates in cells, you can read untruncated outputs in `list` to decrease subsequent `get` calls. (untruncated `output` is not supported in `list` though). Do this if you expect to read all cells returned by `list`.  

## References

- `references/nbformat-cheatsheet.md` — quick reminders on notebook/cell structure, common fields, and useful links to nbformat docs.
