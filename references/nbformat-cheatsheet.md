# nbformat Quick Reference

Use this cheat sheet when the bundled `nb_api.py` script cannot handle a task and you must write custom Python. It distills the workflow shown in [Manipulating Jupyter Notebooks with nbformat (GeeksforGeeks)](https://www.geeksforgeeks.org/python/manipulating-jupyter-notebooks-with-the-nbformat-python-library/).

## Core Schema (v4)

- Notebook JSON keys: `nbformat`, `nbformat_minor`, `metadata`, `cells`.
- `cells` is an ordered list; each cell dict typically includes:
  - `id`: unique string (UUID-like). Prefer IDs instead of indexes.
  - `cell_type`: `"markdown"` or `"code"` (others exist but are rare).
  - `source`: string or list of strings containing the cell body.
  - `metadata`: arbitrary dict; preserve unless explicitly editing.
  - Code-cell extras: `outputs` (list of output dicts) and `execution_count` (int or `null`).

## Boilerplate Workflow

```python
import nbformat as nbf
from pathlib import Path

path = Path("notebook.ipynb")
nb = nbf.read(path.open(), as_version=4)

# work with nb.cells (list of NotebookNode)

nbf.write(nb, path.open("w"))
```

Always read/write with `as_version=4` to normalize schema versions. The article shows the same structure and demonstrates iterating through `nb.cells` to inspect or mutate content.

## Common Tasks

1. **Listing / reading cells**
   ```python
   for cell in nb.cells:
       print(cell["id"], cell["cell_type"])
       print(cell["source"])
   ```
   Use conditionals on `cell["cell_type"]` to separate markdown vs code.

2. **Updating existing cells**
   ```python
   target = next(c for c in nb.cells if c["id"] == CELL_ID)
   target["source"] = "New multiline\ncontent"
   ```
   Preserve other keys (metadata, outputs) unless they must change.

3. **Inserting new cells**
   ```python
   new_md = nbf.v4.new_markdown_cell(source="## Heading")
   new_md["id"] = uuid.uuid4().hex
   nb.cells.insert(index, new_md)  # or append with nb.cells.append(new_md)
   ```
   For code cells use `new_code_cell`. The article shows both patterns.

4. **Deleting cells**
   ```python
   nb.cells = [cell for cell in nb.cells if cell["id"] != CELL_ID]
   ```
   When iterating directly, delete by index to avoid reallocation surprises.

5. **Manipulating outputs**
   - Clear outputs: `cell["outputs"] = []` and `cell["execution_count"] = None`.
   - Add outputs: append dicts shaped like `nbformat.v4.new_output(...)`.

6. **Notebook-level metadata**
   - Access via `nb["metadata"]`. The article uses this to store authors, kernelspec tweaks, etc. Maintain required keys such as `kernelspec` and `language_info`.

## Tips

- When editing via Python, let nbformat handle serialization—avoid manual JSON string manipulation.
- After writing, consider running `jupyter nbconvert --clear-output --inplace notebook.ipynb` if kernel output hygiene matters.

## Helpful Links

- nbformat API: https://nbformat.readthedocs.io/en/latest/api.html
- nbformat file format: https://nbformat.readthedocs.io/en/latest/format_description.html
- GeeksforGeeks tutorial (step-by-step examples): https://www.geeksforgeeks.org/python/manipulating-jupyter-notebooks-with-the-nbformat-python-library/
