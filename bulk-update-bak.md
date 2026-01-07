
- nb_api.py bulk-update-source [-h] --path PATH --update-file UPDATE_FILE [--update-file UPDATE_FILE ...] [--dry-run]
  - Each UPDATE_FILE: first line = cell ID, remaining lines (if any) = replacement source. Repeat `--update-file` for every cell you want to update in one run.

Note that `--content-file` is distinct from `--update-file`. `--update-file` is used for bulk updates and contains the `id` of the cell to update also. This is not true for `--content-file` (which is used in `--update`)
- **Always prefer `bulk-update-source` when updating multiple cell sources**. Create one file per cell: the first line must be the target cell ID and any subsequent lines (including blank ones) become the replacement source. Pass every file via repeated `--update-file` flags. See `references/bulk_update_example.md` for a full walkthrough.
- `references/bulk_update_example.md` - see this if you want examples for bulk updating