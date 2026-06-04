#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    deps: tuple[str, ...] = ()
    dev_deps: tuple[str, ...] = ()
    imports: tuple[str, ...] = ()
    system_tools: tuple[str, ...] = ()
    extends: tuple[str, ...] = ()
    note: str = ""


PROFILES: dict[str, Profile] = {
    "document-ingest-light": Profile(
        deps=(
            "pypdf>=5.0.0",
            "pymupdf>=1.24.0",
            "pdfplumber>=0.11.0",
            "python-docx>=1.1.0",
        ),
        imports=("pypdf", "fitz", "pdfplumber", "docx"),
        note="Text-based PDF and DOCX extraction.",
    ),
    "document-ingest-ocr": Profile(
        deps=("pdf2image>=1.17.0", "pillow>=11.0.0", "pytesseract>=0.3.13"),
        imports=("pdf2image", "PIL", "pytesseract"),
        system_tools=("pdftotext", "pdfinfo", "tesseract"),
        extends=("document-ingest-light",),
        note="OCR fallback for scanned documents. Also check OCR language packs.",
    ),
    "document-ingest-docling": Profile(
        deps=("docling",),
        imports=("docling",),
        note="Advanced document understanding. Heavy transitive dependency profile.",
    ),
    "tables-reports": Profile(
        deps=(
            "pandas>=2.2.0",
            "openpyxl>=3.1.0",
            "lxml>=5.0.0",
            "rapidfuzz>=3.10.0",
        ),
        imports=("pandas", "openpyxl", "lxml", "rapidfuzz"),
        note="Tabular cleanup, matching, report generation, and Excel output.",
    ),
    "cli": Profile(
        deps=("typer>=0.15.0", "rich>=13.0.0"),
        imports=("typer", "rich"),
        note="Local script CLI arguments and rich terminal output.",
    ),
    "dev": Profile(
        dev_deps=("pytest>=8.3.0", "ruff>=0.8.0", "ipykernel>=6.29.0"),
        imports=("pytest",),
        note="Tests, linting, and notebook kernels.",
    ),
}


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def ordered_profiles(names: list[str]) -> list[str]:
    ordered: list[str] = []
    visiting: set[str] = set()

    def visit(name: str) -> None:
        if name not in PROFILES:
            raise SystemExit(f"Unknown profile: {name}")
        if name in ordered:
            return
        if name in visiting:
            raise SystemExit(f"Circular profile dependency involving: {name}")
        visiting.add(name)
        for parent in PROFILES[name].extends:
            visit(parent)
        visiting.remove(name)
        ordered.append(name)

    for name in names:
        visit(name)
    return ordered


def collect(names: list[str]) -> Profile:
    normal: list[str] = []
    dev: list[str] = []
    imports: list[str] = []
    system_tools: list[str] = []
    notes: list[str] = []
    for name in ordered_profiles(names):
        profile = PROFILES[name]
        normal.extend(profile.deps)
        dev.extend(profile.dev_deps)
        imports.extend(profile.imports)
        system_tools.extend(profile.system_tools)
        if profile.note:
            notes.append(f"{name}: {profile.note}")
    return Profile(
        deps=tuple(dedupe(normal)),
        dev_deps=tuple(dedupe(dev)),
        imports=tuple(dedupe(imports)),
        system_tools=tuple(dedupe(system_tools)),
        note="\n".join(notes),
    )


def require_pyproject(dry_run: bool) -> None:
    if Path("pyproject.toml").exists():
        return
    message = (
        "No pyproject.toml found in the current directory. "
        "Run from the target workspace root, or initialize the workspace first."
    )
    if dry_run:
        print(f"warning: {message}", file=sys.stderr)
        return
    raise SystemExit(message)


def require_uv(dry_run: bool) -> None:
    if shutil.which("uv"):
        return
    message = "uv was not found on PATH."
    if dry_run:
        print(f"warning: {message}", file=sys.stderr)
        return
    raise SystemExit(message)


def uv_commands(profile: Profile) -> list[list[str]]:
    commands: list[list[str]] = []
    if profile.deps:
        commands.append(["uv", "add", *profile.deps])
    if profile.dev_deps:
        commands.append(["uv", "add", "--dev", *profile.dev_deps])
    return commands


def command_line(command: list[str]) -> str:
    return shlex.join(command)


def list_profiles(_args: argparse.Namespace) -> int:
    for name in sorted(PROFILES):
        profile = PROFILES[name]
        print(name)
        if profile.extends:
            print(f"  extends: {', '.join(profile.extends)}")
        if profile.deps:
            print(f"  deps: {', '.join(profile.deps)}")
        if profile.dev_deps:
            print(f"  dev deps: {', '.join(profile.dev_deps)}")
        if profile.imports:
            print(f"  imports: {', '.join(profile.imports)}")
        if profile.system_tools:
            print(f"  system tools: {', '.join(profile.system_tools)}")
        if profile.note:
            print(f"  note: {profile.note}")
    return 0


def show_profile(args: argparse.Namespace) -> int:
    profile = collect(args.profiles)
    print("Resolved profiles:", ", ".join(ordered_profiles(args.profiles)))
    if profile.note:
        print(profile.note)
    print()
    for command in uv_commands(profile):
        print(command_line(command))
    if profile.system_tools:
        print("system tools:", ", ".join(profile.system_tools))
    if profile.imports:
        print("imports:", ", ".join(profile.imports))
    return 0


def install_profile(args: argparse.Namespace) -> int:
    profile = collect(args.profiles)
    require_pyproject(args.dry_run)
    require_uv(args.dry_run)

    for command in uv_commands(profile):
        if args.dry_run:
            print(command_line(command))
        else:
            subprocess.check_call(command)

    if profile.system_tools:
        missing = [tool for tool in profile.system_tools if shutil.which(tool) is None]
        if missing:
            print(
                "missing system tools: " + ", ".join(missing),
                file=sys.stderr,
            )
    return 0


def check_imports(args: argparse.Namespace) -> int:
    profile = collect(args.profiles)
    require_pyproject(False)
    require_uv(False)

    if profile.system_tools:
        missing_tools = [tool for tool in profile.system_tools if shutil.which(tool) is None]
        if missing_tools:
            print("missing system tools: " + ", ".join(missing_tools), file=sys.stderr)

    code = (
        "import importlib\n"
        f"mods = {list(profile.imports)!r}\n"
        "for mod in mods:\n"
        "    importlib.import_module(mod)\n"
        "print('imports ok:', ', '.join(mods))\n"
    )
    subprocess.check_call(["uv", "run", "python", "-c", code])
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage repo-local uv dependency profiles for reusable skills."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available profiles.")
    list_parser.set_defaults(func=list_profiles)

    show_parser = subparsers.add_parser("show", help="Show resolved profile commands.")
    show_parser.add_argument("profiles", nargs="+", choices=sorted(PROFILES))
    show_parser.set_defaults(func=show_profile)

    install_parser = subparsers.add_parser("install", help="Install profiles with uv add.")
    install_parser.add_argument("profiles", nargs="+", choices=sorted(PROFILES))
    install_parser.add_argument("--dry-run", action="store_true", help="Print commands only.")
    install_parser.set_defaults(func=install_profile)

    check_parser = subparsers.add_parser("check", help="Verify profile imports with uv run.")
    check_parser.add_argument("profiles", nargs="+", choices=sorted(PROFILES))
    check_parser.set_defaults(func=check_imports)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
