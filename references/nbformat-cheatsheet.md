# nbformat Quick Reference

## Notebook Structure

- Notebook files are JSON matching **nbformat v4** schema:
  - Top-level keys: `nbformat`, `nbformat_minor`, `metadata`, `cells`.
  - `cells` is an ordered list; each entry represents a cell dict.

## Cell Keys

| Key | Notes |
| --- | --- |
| `id` | Unique string identifier (UUID). Always target cells by this. |
| `cell_type` | `"markdown"` or `"code"` (common cases). |
| `source` | Cell body as a string or list of lines; nbformat can take either. |
| `metadata` | Arbitrary dict (ignored by current skill operations). |
| `outputs` | Only on code cells; list of output dicts. |
| `execution_count` | Integer or `null`; also code cells only. |

## Common Operations

- **Creating cells**: use helpers such as `nbformat.v4.new_markdown_cell(source=...)` or `new_code_cell`.
- **Writing files**: always round-trip via `nbformat.read(path, as_version=4)` and `nbformat.write(nb, path)` to ensure version tagging stays consistent.
- **UUID generation**: `uuid.uuid4().hex` yields a compact ID compatible with nbformat expectations.

## Helpful Links

- API overview: https://nbformat.readthedocs.io/en/latest/api.html
- File format reference: https://nbformat.readthedocs.io/en/latest/format_description.html

