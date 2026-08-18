#!/usr/bin/env python3
"""Render and validate a one-page RenderCV resume without stale artifacts.

The wrapper uses RenderCV's Python API for the old 2.2 engine and its quiet CLI
for 2.8. RenderCV 2.2 calls PyPI from ``welcome()`` on every render and the
request has no timeout; the old path therefore skips only that optional update
check. Both paths write to a fresh staging directory and validate the PDF
before publishing artifacts.

Usage (PowerShell):

    python render_resume.py C:\\path\\resume.yaml \\
      --output-dir C:\\path\\out --stem resume

By default it creates the PDF and PNG preview. Add ``--all`` when Markdown,
HTML, and Typst source files are also needed.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="RenderCV YAML input file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for published artifacts (default: input directory / output)",
    )
    parser.add_argument(
        "--stem",
        default=None,
        help="Published filename stem (default: YAML filename stem)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Also publish Markdown, HTML, and Typst source files",
    )
    parser.add_argument(
        "--allow-multi-page",
        action="store_true",
        help="Do not fail when the rendered PDF has more than one page",
    )
    return parser.parse_args()


def _count_pdf_pages(pdf_path: Path, fallback_count: int | None = None) -> int:
    data = pdf_path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise RuntimeError(f"Not a PDF file: {pdf_path}")
    try:
        from pypdf import PdfReader

        pages = len(PdfReader(str(pdf_path)).pages)
    except Exception:
        # Some PDF generators put page dictionaries in compressed object streams.
        # The regex is only a fallback for older runtimes without pypdf.
        pages = len(re.findall(rb"/Type\s*/Page\b", data))
    if pages < 1 and fallback_count:
        pages = fallback_count
    if pages < 1:
        raise RuntimeError(f"Could not determine PDF page count: {pdf_path}")
    return pages


def _pdfinfo_page_count(pdf_path: Path) -> int | None:
    """Use pdfinfo when available; return None when it is not installed."""
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        return None
    try:
        result = subprocess.run(
            [pdfinfo, str(pdf_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = re.search(r"^Pages:\s*(\d+)", result.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def _first_file(directory: Path, suffix: str) -> Path:
    candidates = sorted(directory.glob(f"*{suffix}"))
    if not candidates:
        raise RuntimeError(f"RenderCV did not produce a {suffix} file in {directory}")
    return candidates[0]


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    """Read PNG dimensions without requiring Pillow."""
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None
    if not header.startswith(b"\x89PNG\r\n\x1a\n") or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def _page_png_files(directory: Path) -> list[Path]:
    """Exclude copied photo/assets from RenderCV's page PNGs."""
    candidates = sorted(directory.glob("*.png"))
    page_files = []
    for path in candidates:
        dimensions = _png_dimensions(path)
        if dimensions and dimensions[0] >= 500 and dimensions[1] >= 700:
            page_files.append(path)
    return page_files or candidates


def _copy_one(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def _copy_pngs(png_files: Iterable[Path], output_dir: Path, stem: str) -> list[Path]:
    files = list(png_files)
    if not files:
        raise RuntimeError("RenderCV did not produce a PNG preview")
    published: list[Path] = []
    if len(files) == 1:
        published.append(_copy_one(files[0], output_dir / f"{stem}.png"))
    else:
        for index, source in enumerate(files, start=1):
            published.append(_copy_one(source, output_dir / f"{stem}_{index}.png"))
    return published


def _remove_previous_artifacts(output_dir: Path, stem: str) -> None:
    """Remove only previous artifacts for this stem; never delete the directory."""
    if not output_dir.exists():
        return
    patterns = [
        f"{stem}.pdf",
        f"{stem}.md",
        f"{stem}.html",
        f"{stem}.typ",
        f"{stem}.png",
        f"{stem}_*.png",
    ]
    for pattern in patterns:
        for path in output_dir.glob(pattern):
            if path.is_file():
                path.unlink()


def _render_with_rendercv_22(
    input_path: Path,
    staging_dir: Path,
    include_all: bool,
) -> Path:
    from rendercv.cli import printer, utilities

    # RenderCV 2.2's welcome() calls PyPI with no timeout. Do not change any
    # rendering behavior; only suppress this optional network check.
    printer.warn_if_new_version_is_available = lambda: False

    raw = utilities.data.read_a_yaml_file(input_path)
    rendercv_settings = raw.setdefault("rendercv_settings", {})
    settings = rendercv_settings.get("render_command")
    if not isinstance(settings, dict):
        settings = {}
        rendercv_settings["render_command"] = settings
    settings.update(
        {
            "output_folder_name": staging_dir.name,
            "typst_path": None,
            "pdf_path": None,
            "markdown_path": None,
            "html_path": None,
            "png_path": None,
            "dont_generate_markdown": not include_all,
            "dont_generate_html": not include_all,
            "dont_generate_png": False,
            "watch": False,
        }
    )

    original_cwd = Path.cwd()
    try:
        # RenderCV resolves template overrides relative to the YAML directory,
        # while output_folder_name is resolved relative to the working directory.
        os.chdir(input_path.parent)
        utilities.run_rendercv_with_printer(raw, input_path.parent, input_path)
    except Exception as exc:
        raise RuntimeError(
            "The installed RenderCV engine rejected this YAML. The project venv "
            "contains RenderCV 2.2, while the current master YAML uses the 2.8 "
            "schema; use the bundled 2.8 Python runtime or update the project venv."
        ) from exc
    finally:
        os.chdir(original_cwd)

    rendered_dir = input_path.parent / staging_dir.name
    if not rendered_dir.exists():
        raise RuntimeError(f"RenderCV did not create output directory: {rendered_dir}")
    return rendered_dir


def _render_with_rendercv_28(
    input_path: Path,
    staging_dir: Path,
    include_all: bool,
) -> Path:
    """Use the 2.8 CLI, whose internal API is intentionally different."""
    command = [
        sys.executable,
        "-X",
        "utf8",
        "-m",
        "rendercv",
        "render",
        input_path.name,
        "--output-folder",
        staging_dir.name,
        "--quiet",
    ]
    if not include_all:
        command.append("--dont-generate-markdown")

    try:
        result = subprocess.run(
            command,
            cwd=input_path.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("RenderCV exceeded the 180-second rendering timeout") from exc
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        if len(details) > 4000:
            details = details[-4000:]
        raise RuntimeError(f"RenderCV 2.8 failed (exit {result.returncode}): {details}")

    rendered_dir = input_path.parent / staging_dir.name
    if not rendered_dir.exists():
        raise RuntimeError(f"RenderCV did not create output directory: {rendered_dir}")
    return rendered_dir


def _render(input_path: Path, staging_dir: Path, include_all: bool) -> Path:
    try:
        import rendercv
    except ImportError as exc:  # pragma: no cover - depends on local runtime
        raise RuntimeError(
            "RenderCV is not installed in this Python runtime. "
            "Use the project .rendercv-venv or the bundled Codex Python."
        ) from exc

    version = str(getattr(rendercv, "__version__", "0"))
    # RenderCV 2.2 has the old synchronous API; 2.8 has the new CLI package.
    # Avoid importing the old API in 2.8, where those names no longer exist.
    if version.startswith("2.2"):
        return _render_with_rendercv_22(input_path, staging_dir, include_all)
    return _render_with_rendercv_28(input_path, staging_dir, include_all)


def main() -> int:
    args = _parse_args()
    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        raise SystemExit(f"Input YAML does not exist: {input_path}")
    try:
        input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Input YAML is not valid UTF-8: {input_path}") from exc

    output_dir = (args.output_dir or input_path.parent / "output").expanduser().resolve()
    stem = args.stem or input_path.stem
    if not stem or any(char in stem for char in "\\/:*?\"<>|"):
        raise SystemExit(f"Invalid output filename stem: {stem!r}")
    output_dir.mkdir(parents=True, exist_ok=True)
    _remove_previous_artifacts(output_dir, stem)

    staging_parent = input_path.parent
    staging_path = Path(tempfile.mkdtemp(prefix=".rendercv-staging-", dir=staging_parent))
    staging_dir = Path(staging_path.name)
    try:
        rendered_dir = _render(input_path, staging_dir, args.all)
        pdf_source = _first_file(rendered_dir, ".pdf")
        page_pngs = _page_png_files(rendered_dir)
        page_count = _count_pdf_pages(pdf_source, fallback_count=len(page_pngs))
        pdfinfo_pages = _pdfinfo_page_count(pdf_source)
        if pdfinfo_pages is not None and pdfinfo_pages != page_count:
            raise RuntimeError(
                f"PDF page-count disagreement: regex={page_count}, pdfinfo={pdfinfo_pages}"
            )
        if page_count != 1 and not args.allow_multi_page:
            raise RuntimeError(
                f"Resume rendered to {page_count} pages; fix content/layout or pass "
                "--allow-multi-page explicitly."
            )

        published = [_copy_one(pdf_source, output_dir / f"{stem}.pdf")]
        published.extend(_copy_pngs(page_pngs, output_dir, stem))

        if args.all:
            for suffix in (".md", ".html", ".typ"):
                source = _first_file(rendered_dir, suffix)
                published.append(_copy_one(source, output_dir / f"{stem}{suffix}"))

        print(f"RenderCV: {input_path.name}")
        print(f"Pages: {page_count}")
        print(f"Artifacts: {output_dir}")
        for path in published:
            print(f"- {path.name}")
        return 0
    finally:
        shutil.rmtree(staging_path, ignore_errors=True)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        try:
            raise SystemExit(main())
        except RuntimeError as exc:
            raise SystemExit(f"RenderCV validation failed: {exc}") from exc
