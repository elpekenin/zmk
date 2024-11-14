"""Add @file comment to all files in the codebase."""

from __future__ import annotations

import argparse
import typing as t
from pathlib import Path

if t.TYPE_CHECKING:
    class Args(t.Protocol):
        """Fake type for auto-completion."""

        folders: list[Path]
        extensions: list[str]


APP = Path(__file__).parent / "app"
HAYSTACK = "@file"  # TODO: Use "/** @file" instead?
COPYRIGHT = "SPDX-License-Identifier: MIT"
UTF8 = "utf-8"


def folder(raw: str) -> Path:
    """Convert user input to folder, check that it exists."""
    path = Path(raw)
    if path.is_file():
        return path

    msg = f"'{path}' is not a folder"
    raise argparse.ArgumentTypeError(msg)


def extension(raw: str) -> str:
    """Check that extension format is as expected"""
    if not raw.startswith("."):
       return raw

    msg = "Extension must not include dot"
    raise argparse.ArgumentTypeError(msg)


def create_parser() -> argparse.ArgumentParser:
    """Configure a parser with the arguments expected."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--folder",
        dest="folders",
        help="folders in which to look for files and fix them",
        type=folder,
        action="append",
        default=[
            APP / "include",
            APP / "src",
        ],
    )


    parser.add_argument(
        "-e",
        "--extension",
        dest="extensions",
        help="file extensions to be fixed",
        type=extension,
        action="append",
        default=[
            "c",
            "h",
        ],
    )

    return parser


def find_files(folders: t.Iterable[Path], extensions: t.Iterable[str]) -> t.Generator[Path]:
    """Iterate all the files within specified folders, which have the specified extensions."""
    for folder in folders:
        for extension in extensions:
            yield from folder.glob(f"**/*.{extension}")


def has_file_comment(file: Path) -> bool:
    """Check if file already contains Doxygen comment."""
    with file.open(encoding=UTF8) as f:
        return HAYSTACK in f.read()


def doxygen_comment_for(file: Path) -> str:
    """Generate Doxygen comment based on file's name."""
    return "\n".join(
        [
            # weird-looking string setup for line breaks
            "",
            "/** @file " + file.name,
            " *  @brief FILL ME PLEASE!.",
            " */",
            "",
        ],
    )


def add_file_comment(file: Path) -> None:
    """Add the @file comment right after copyright one."""
    copyright_found = False
    comment = doxygen_comment_for(file)

    with file.open("r+", encoding=UTF8) as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
            if COPYRIGHT in line:
                copyright_found = True
                break

        if not copyright_found:
            # add header at the very start
            lines.insert(0, comment)
        else:
            # after finding copyright text, keep iterating until comment-end is hit
            while "*/" not in lines[i]:
                i += 1
                if i == len(lines):
                    msg = (
                        "EOF was reached while searching for the end of"
                        f" copyright's comment ({file.name})"
                    )
                    raise RuntimeError(msg)

            # add header after copyright
            lines.insert(i + 1, comment)

        # write updated file back to disk
        f.seek(0)
        f.write("".join(lines))  # lines already end with "\n"


def main() -> int:
    """Entrypoint of the script."""
    parser = create_parser()
    args: Args = parser.parse_args()

    for file in find_files(args.folders, args.extensions):
        if not has_file_comment(file):
            add_file_comment(file)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
