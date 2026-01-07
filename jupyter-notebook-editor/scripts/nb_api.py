#!/usr/bin/env python3
"""
ID-based helpers for inspecting and editing Jupyter notebooks via nbformat.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import nbformat


def load_notebook(path: Path) -> nbformat.NotebookNode:
    if not path.exists():
        sys.exit(f"Notebook not found: {path}")
    return nbformat.read(path, as_version=4)


def write_notebook(nb: nbformat.NotebookNode, path: Path) -> None:
    nbformat.write(nb, path)


def find_cell_by_id(
    nb: nbformat.NotebookNode, cell_id: str
) -> tuple[nbformat.NotebookNode, int]:
    for idx, cell in enumerate(nb.cells):
        if cell.get("id") == cell_id:
            return cell, idx
    sys.exit(f"Cell with id '{cell_id}' not found.")


def stringify_source(value: Any) -> str:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return "".join(value)
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def truncate_text(text: str, limit: int) -> str:
    if limit is None or limit < 0:
        return text
    if len(text) <= limit:
        return text
    return text[:limit]


def parse_fields(raw: Optional[str]) -> List[str]:
    if not raw:
        sys.exit("--fields is required.")
    fields = [field.strip() for field in raw.split(",") if field.strip()]
    if not fields:
        sys.exit("Provide at least one field.")
    return fields


def render_field(cell: nbformat.NotebookNode, field: str, limit: int) -> str:
    if field not in cell:
        sys.exit(f"Field '{field}' not present on the cell.")
    value = cell[field]
    return truncate_text(stringify_source(value), limit)


def command_list(args: argparse.Namespace) -> None:
    nb = load_notebook(args.path)
    fields = parse_fields(args.fields)
    if args.truncate == -1 and "outputs" in fields:
        sys.exit("Listing all outputs without truncation is not allowed.")
    for cell in nb.cells:
        if args.cell_type and cell.get("cell_type") != args.cell_type:
            continue
        payload: Dict[str, Any] = {field: render_field(cell, field, args.truncate) for field in fields}
        print(json.dumps(payload, ensure_ascii=False))


def command_get(args: argparse.Namespace) -> None:
    nb = load_notebook(args.path)
    cell, _ = find_cell_by_id(nb, args.id)
    fields = parse_fields(args.fields)
    payload = {field: render_field(cell, field, args.truncate) for field in fields}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def read_content(args: argparse.Namespace) -> str:
    if args.content_file:
        return Path(args.content_file).read_text()
    if args.content is not None:
        return args.content
    sys.exit("Provide --content or --content-file.")


def read_bulk_instructions(paths: Sequence[Path]) -> List[Tuple[str, str, Path]]:
    if not paths:
        sys.exit("Provide at least one --update-file.")
    instructions: List[Tuple[str, str, Path]] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            sys.exit(f"Content file not found: {path}")
        text = path.read_text()
        if not text.strip():
            sys.exit(f"{path}: File has no content.")
        lines = text.splitlines(keepends=True)
        if not lines:
            sys.exit(f"{path}: File has no content.")
        cell_id = lines[0].strip()
        if not cell_id:
            sys.exit(f"{path}: First line must contain the target cell ID.")
        new_content = "".join(lines[1:])
        instructions.append((cell_id, new_content, path))
    return instructions


def command_update(args: argparse.Namespace) -> None:
    if args.field != "source":
        sys.exit("Only the 'source' field is supported for updates.")
    nb = load_notebook(args.path)
    cell, _ = find_cell_by_id(nb, args.id)
    new_content = read_content(args)
    previous = stringify_source(cell.get("source", ""))
    cell["source"] = new_content
    if args.dry_run:
        print(
            json.dumps(
                {
                    "action": "update",
                    "id": args.id,
                    "field": args.field,
                    "old_chars": len(previous),
                    "new_chars": len(new_content),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    write_notebook(nb, args.path)
    print(
        json.dumps(
            {
                "status": "updated",
                "id": args.id,
                "field": args.field,
                "chars": len(new_content),
            },
            ensure_ascii=False,
        )
    )


def command_delete(args: argparse.Namespace) -> None:
    nb = load_notebook(args.path)
    _, idx = find_cell_by_id(nb, args.id)
    cell = nb.cells[idx]
    if args.dry_run:
        print(
            json.dumps(
                {
                    "action": "delete",
                    "id": args.id,
                    "cell_type": cell.get("cell_type"),
                    "source": truncate_text(stringify_source(cell.get("source", "")), args.truncate),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    nb.cells.pop(idx)
    write_notebook(nb, args.path)
    print(json.dumps({"status": "deleted", "id": args.id}, ensure_ascii=False))


def create_cell(cell_type: str, content: str) -> nbformat.NotebookNode:
    if cell_type == "markdown":
        cell = nbformat.v4.new_markdown_cell(source=content)
    elif cell_type == "code":
        cell = nbformat.v4.new_code_cell(source=content)
    else:
        sys.exit("Cell type must be 'markdown' or 'code'.")
    cell["id"] = uuid.uuid4().hex
    return cell


def command_insert(args: argparse.Namespace) -> None:
    nb = load_notebook(args.path)
    content = read_content(args)
    cell = create_cell(args.cell_type, content)
    target_id = args.before_id

    if target_id:
        _, idx = find_cell_by_id(nb, target_id)
        insert_at = idx
    else:
        insert_at = len(nb.cells)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "action": "insert",
                    "new_id": cell["id"],
                    "cell_type": cell["cell_type"],
                    "chars": len(content),
                    "position": insert_at,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    nb.cells.insert(insert_at, cell)
    write_notebook(nb, args.path)
    print(
        json.dumps(
            {"status": "inserted", "new_id": cell["id"], "cell_type": cell["cell_type"], "position": insert_at},
            ensure_ascii=False,
        )
    )


def command_bulk_update_source(args: argparse.Namespace) -> None:
    nb = load_notebook(args.path)
    instructions = read_bulk_instructions([Path(p) for p in args.update_files])
    cell_lookup = {cell.get("id"): cell for cell in nb.cells if cell.get("id")}
    missing = [cell_id for cell_id, _, _ in instructions if cell_id not in cell_lookup]
    if missing:
        ids = ", ".join(missing)
        sys.exit(f"Cell IDs not found: {ids}")

    planned_updates: List[Tuple[nbformat.NotebookNode, str, str, str, Path]] = []
    for cell_id, new_content, source_file in instructions:
        cell = cell_lookup[cell_id]
        previous_source = stringify_source(cell.get("source", ""))
        planned_updates.append((cell, cell_id, new_content, previous_source, source_file))

    summary_payload = [
        {
            "id": cell_id,
            "file": str(source_file),
            "old_chars": len(previous_source),
            "new_chars": len(new_content),
        }
        for _, cell_id, new_content, previous_source, source_file in planned_updates
    ]

    if args.dry_run:
        print(
            json.dumps(
                {"action": "bulk-update-source", "updates": summary_payload},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    for cell, _, new_content, _, _ in planned_updates:
        cell["source"] = new_content

    write_notebook(nb, args.path)
    print(
        json.dumps(
            {
                "status": "bulk-updated",
                "updated": len(summary_payload),
                "details": summary_payload,
            },
            ensure_ascii=False,
        )
    )


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--path", required=True, type=Path, help="Path to the .ipynb file.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operate on Jupyter notebook cells by ID.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List notebook cells with selected fields.")
    add_common_arguments(list_parser)
    list_parser.add_argument("--fields", required=True, help="Comma-separated field names to display.")
    list_parser.add_argument(
        "--truncate",
        type=int,
        default=100,
        help="Character limit per field (use -1 for no limit).",
    )
    list_parser.add_argument(
        "--cell-type",
        choices=["markdown", "code"],
        help="Optional filter matching cell_type.",
    )
    list_parser.set_defaults(func=command_list)

    get_parser = subparsers.add_parser("get", help="Get fields for a specific cell ID.")
    add_common_arguments(get_parser)
    get_parser.add_argument("--id", required=True, help="Cell ID to read.")
    get_parser.add_argument("--fields", required=True, help="Comma-separated field names to display.")
    get_parser.add_argument(
        "--truncate",
        type=int,
        default=100,
        help="Character limit per field (use -1 for no limit).",
    )
    get_parser.set_defaults(func=command_get)

    update_parser = subparsers.add_parser("update", help="Update a field (source only) by cell ID.")
    add_common_arguments(update_parser)
    update_parser.add_argument("--id", required=True, help="Cell ID to update.")
    update_parser.add_argument("--field", required=True, help="Field to update (only 'source').")
    update_parser.add_argument("--content", help="Inline replacement content.")
    update_parser.add_argument("--content-file", help="Path to file with replacement content.")
    update_parser.add_argument("--dry-run", action="store_true", help="Preview without writing changes.")
    update_parser.set_defaults(func=command_update)

    delete_parser = subparsers.add_parser("delete", help="Delete a cell by ID.")
    add_common_arguments(delete_parser)
    delete_parser.add_argument("--id", required=True, help="Cell ID to delete.")
    delete_parser.add_argument("--dry-run", action="store_true", help="Preview deletion without writing.")
    delete_parser.add_argument(
        "--truncate",
        type=int,
        default=100,
        help="Character limit when previewing source (use -1 for no limit).",
    )
    delete_parser.set_defaults(func=command_delete)

    insert_parser = subparsers.add_parser("insert", help="Insert a new cell.")
    add_common_arguments(insert_parser)
    insert_parser.add_argument("--before-id", help="Insert before this cell ID (append when omitted).")
    insert_parser.add_argument(
        "--cell-type", required=True, choices=["markdown", "code"], help="cell_type for the new cell."
    )
    insert_parser.add_argument("--content", help="Inline cell content.")
    insert_parser.add_argument("--content-file", help="Path to file with cell content.")
    insert_parser.add_argument("--dry-run", action="store_true", help="Preview insertion without writing.")
    insert_parser.set_defaults(func=command_insert)

    bulk_parser = subparsers.add_parser(
        "bulk-update-source",
        help="Update multiple cell sources based on a content file with ID-prefixed lines.",
    )
    add_common_arguments(bulk_parser)
    bulk_parser.add_argument(
        "--update-file",
        dest="update_files",
        action="append",
        required=True,
        help="Path to an instruction file (first line = cell ID, rest = replacement source). Repeat flag for multiple files.",
    )
    bulk_parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    bulk_parser.set_defaults(func=command_bulk_update_source)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
