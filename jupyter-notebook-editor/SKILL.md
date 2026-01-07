---
name: jupyter-notebook-editor
description: Inspect and edit Jupyter notebook (.ipynb) listing, reading, updating, deleting, and inserting cells. Use whenever an agent must analyze or modify notebook cell content (e.g., reviewing markdown, tweaking code) with precise, per-cell control.
---

# Jupyter notebook interaction
- Interact with jupyter notebooks primarily through the script scripts/nb_api.py. It provides atomics to reliably work with notebook.  
- If it is not enough, write python code to interact, coding instructions and examples [here](references/nbformat-cheatsheet.md). You can also look at the [script](scripts/nb_api.py) for detailed python code example.  
- Avoid reading the notebook file directly

NOTE: All scripts and references path inside this doc are relative to the directory containing this doc  

## Dependencies

- Python 3.9+ and `nbformat` package (`pip install nbformat` if missing).

## Command Summary

Concise usage help instructions for the script
- nb_api.py [-h] {list,get,update,delete,insert} ...
- nb_api.py get [-h] --path PATH --id ID_TO_GET --fields COMMA_SEPARATED_FIELDS [--truncate TRUNCATE]
- nb_api.py update [-h] --path PATH --id ID_TO_UPDATE --field SINGLE_FIELD_TO_UPDATE [--content CONTENT] [--content-file CONTENT_FILE] [--dry-run]
- nb_api.py delete [-h] --path PATH --id ID_TO_DELETE [--dry-run] [--truncate TRUNCATE]
- nb_api.py list [-h] --path PATH --fields COMMA_SEPARATED_FIELDS [--truncate TRUNCATE] [--cell-type {markdown,code}]
- nb_api.py insert [-h] --path PATH [--before-id BEFORE_ID] --cell-type {markdown,code} [--content CONTENT] [--content-file CONTENT_FILE] [--dry-run]
  - Cell would be inserted before the cell with ID = BEFORE_ID. If no --before-id provided, append

Call the script with `-h` if you want more details.  


## Usage Notes

Important usage tips
- `field` is a key in the cell JSON, like `cell_type`, `id` or `source`.
  - `source` contains the actual data of notebooks (like markdown text or actual code)
  - `id` is the unique identifier of that cell
- **Truncate output generally**: Every reading operation (list, get, etc) takes a `--truncate` flag with default value of 100. It would truncate the output of each field inside each cell to the character limit. If you want to read the whole field, use `--truncate -1`.  
- **Always pass fields**. Make sure you do selective reads. 
- **Filter when possible**. `list` accepts `--cell-type markdown` or `--cell-type code` to keep responses focused; prefer filtering before dumping many cells.
- The commands print JSON lines output when successful.  
- All commands accept `--dry-run` when you want to preview changes without writing.
- If a command takes user input, it would be done using either `--content` or `--content-file`, use one of them
- **Avoid reading output field unless relevant** (output can clutter and eat up context).
- If a line in markdown contains extra spaces in the end, don't remove them (extra spaces at line end have semantic meaning in markdown)
- Always use the format below for multiline strings (example given using `cat`). 
```bash
cat << EndOfMessage
This is line 1.
This is line 2.
Line 3.
EndOfMessage
```


## References

- `references/nbformat-cheatsheet.md` — quick reminders on notebook/cell structure, common fields, and useful links to nbformat docs.
- `references/examples.md` — ready-to-run nb_api.py invocations covering common workflows (listing, reading, updating, inserting, deleting).
