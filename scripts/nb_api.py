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
from typing import Any, Dict, List, Optional, Sequence

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
    if args.truncate == -1 and "output" in fields:
        exit("Listing all output cells without truncating is not allowed")
    for cell in nb.cells:
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
    cell = create_cell(args.type, content)
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
                    "type": cell["cell_type"],
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
            {"status": "inserted", "new_id": cell["id"], "type": cell["cell_type"], "position": insert_at},
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
    insert_parser.add_argument("--type", required=True, choices=["markdown", "code"], help="Cell type to create.")
    insert_parser.add_argument("--content", help="Inline cell content.")
    insert_parser.add_argument("--content-file", help="Path to file with cell content.")
    insert_parser.add_argument("--dry-run", action="store_true", help="Preview insertion without writing.")
    insert_parser.set_defaults(func=command_insert)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
