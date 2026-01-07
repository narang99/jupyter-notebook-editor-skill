# Bulk Update Multiple Cells

Create one file per cell where the first line is the cell ID and all following lines (if any) are the replacement source. Use as many files as needed, then pass them all via repeated `--update-file` flags.

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

Preview and then apply the updates:

```bash
python scripts/nb_api.py bulk-update-source \
  --path notebooks/report.ipynb \
  --update-file edits/intro_cell.txt \
  --update-file edits/recompute_cell.txt
```

`--dry-run` prints per-file character deltas; omit it once you are confident in the changes.
