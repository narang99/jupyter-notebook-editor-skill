# nb_api.py Usage Examples

Concrete invocations showing typical workflows.

## 1. Map Markdown Cells and Their IDs

```bash
python scripts/nb_api.py list \
  --path notebooks/report.ipynb \
  --fields id,cell_type \
  --cell-type markdown \
  --truncate 60
```

Outputs JSON lines like `{"id": "b3e8...", "cell_type": "markdown"}` so you can copy IDs for later edits.

## 2. Read a Markdown Cell Without Truncation

```bash
python scripts/nb_api.py get \
  --path notebooks/report.ipynb \
  --id b3e8d730c9de4f40ab0c9e9486f8e6ba \
  --fields id,source \
  --truncate -1
```

Prints the full `source` text for that cell only.

## 3. Update Markdown Source from a File

```bash
python scripts/nb_api.py update \
  --path notebooks/report.ipynb \
  --id b3e8d730c9de4f40ab0c9e9486f8e6ba \
  --field source \
  --content-file edits/intro.md
```

Replaces the cell’s `source` with the contents of `edits/intro.md`. Use `--dry-run` first if you want a preview.

## 4. Insert a Code Cell Before Another Cell

```bash
python scripts/nb_api.py insert \
  --path notebooks/report.ipynb \
  --before-id 9d54ac2b8da04ca6a75bb5f41d0c2c32 \
  --cell-type code \
  --content "print('Recomputing metrics')"
```

Creates a new code cell before the referenced ID. Omit `--before-id` to append at the end.

## 5. Dry-Run Delete

```bash
python scripts/nb_api.py delete \
  --path notebooks/report.ipynb \
  --id 4f5f0e7ba9c24388a5fb0a463d4e6b7b \
  --dry-run \
  --truncate 120
```

Shows what would be removed (cell type plus truncated source) without modifying the notebook.

## 6. Bulk Update Multiple Cells

Create one file per cell where the first line is the target cell ID and the remaining lines are the replacement source (multi-line friendly):

```bash
cat <<'EOF' > edits/intro_cell.txt
markdown-cell-id
## Updated intro section
- new bullet
- another bullet
EOF

cat <<'EOF' > edits/recompute_cell.txt
code-cell-id
print("Recomputed with new params")
EOF
```

Preview and then apply both updates in one command by repeating `--content-file`:

```bash
python scripts/nb_api.py bulk-update-source \
  --path notebooks/report.ipynb \
  --content-file edits/intro_cell.txt \
  --content-file edits/recompute_cell.txt \
  --dry-run

python scripts/nb_api.py bulk-update-source \
  --path notebooks/report.ipynb \
  --content-file edits/intro_cell.txt \
  --content-file edits/recompute_cell.txt
```

`--dry-run` prints per-file character deltas (including which file feeds each cell). Omit it once confident.
