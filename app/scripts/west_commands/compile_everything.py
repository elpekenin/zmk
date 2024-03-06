# Copyright (c) 2024 The ZMK Contributors
# SPDX-License-Identifier: MIT
"""(Try) Compile every keyboard configuration."""

import argparse
import subprocess
import sys
import yaml
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional

from west.commands import WestCommand

ZMK_YML = ".zmk.yml"

class CompileEverything(WestCommand):
    def __init__(self):
        super().__init__(
            name="compile_everything",
            help="(try) compile every keyboard configuration",
            description="(Try) compile every keyboard configuration.",
        )

    def do_add_parser(self, parser_adder):
        """Define custom flags/options.
        """
        parser = parser_adder.add_parser(
            self.name,
            help=self.help,
            description=self.description,
        )

        parser.add_argument(
            "--verbose",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="Whether to print compiler's stderr on fails. Default: True",
        )

        parser.add_argument(
            "--failfast",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="Whether the command stops after a compilation fails. Default: False",
        )

        parser.add_argument(
            "--list",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="List available outputs, eg: to parallelize their build on GHA. Default: False",
        )

        return parser

    def _get_yamls(self, dir: Path) -> Iterable[dict]:
        """Read ZMK's metadata files in the given directory.
        """
        for yaml_file in dir.glob(f"*{ZMK_YML}"):
            with yaml_file.open("r") as f:
                yield yaml.safe_load(f)

    def _gather_targets_impl(self, dir: Path, boards: list[str], exposes: dict[str, str], requires: dict[str, str]):
        """Actual implementation for gathering targets from a leaf folder.
        """

        # base case, nothing to do with files
        if not dir.is_dir():
            return
        
        # make sure we iterate our children (if any)
        for child in dir.iterdir():
            self._gather_targets_impl(child, boards, exposes, requires)

        # actual logic for this folder
        for metadata in self._get_yamls(dir):
            _id = metadata.get("id")

            ids = metadata.get("siblings", [_id])
            if ids is None:
                raise ValueError(metadata)

            # assuming multi -require/-expose is not a thing

            # interconnects
            _exposes = metadata.get("exposes")
            if _exposes is not None:
                exposes[_id] = _exposes[0]
                continue

            # shields
            _requires = metadata.get("requires")
            if _requires is not None:
                for id_ in ids:  # could be split
                    requires[id_] = _requires[0]

                continue

            # at this point, yaml for a regular keyboard
            for id_ in ids:
                boards.append((id_, None))

    def _gather_targets(self, boards_dir: Path) -> list[tuple[str, Optional[str]]]:
        """Collect valid targets by iterating over zmk/app/boards

        Returns dict of targets: board, Optional[shield]
        """

        boards, exposes, requires = [], {}, {}
        for child in boards_dir.iterdir():
            if (
                not child.is_dir()  # overlay files at the root of the folder
                or child.name == "interconnects"  # nothing to grab
            ):
                continue

            self._gather_targets_impl(child, boards, exposes, requires)

        # parse targets from exposes/requires
        for shield, req in requires.items():
            for connect, exp in exposes.items():
                if exp == req:
                    boards.append((connect, shield))
                    break

        return boards

    def _compile(self, zmk_app_dir: Path, board: str, shield: Optional[str] = None) -> bool:
        """Try and compile a board, printing some information on the process.

        Return: Whether the command ran successfully
        """

        command = f"west build -p -b {board}"

        if shield is not None:
            command += f" -- -DSHIELD={shield}"

        out = subprocess.run(
            command,
            capture_output=True,
            shell=True,
            cwd=zmk_app_dir,
        )

        if out.returncode == 0:
            self.inf(f"{command}: ok")
        else:
            self.err(f"{command}: fail")

            self.failed = True

            if self.verbose:
                self.err(out.stderr)

            if self.failfast:
                sys.exit(0)

    def do_run(self, args, unknown_args):
        """Command's entrypoint. Collect and (try) compile all boards in the repo.
        """

        self.verbose = args.verbose
        self.failfast = args.failfast

        # walk backwards: .py / west_commands / script / app
        this_file = Path(__file__)
        zmk_app_dir = this_file.parent.parent.parent
        boards_dir = zmk_app_dir / "boards"

        targets = self._gather_targets(boards_dir)

        if args.list:
            import json

            targets = [
                {
                    "board": board,
                    "shield": shield
                }
                for board, shield in targets
            ]

            print(json.dumps(targets))

            sys.exit(0)

        self.failed = False
        for board, shield in targets:
            self._compile(zmk_app_dir, board, shield)

        sys.exit(1 if self.failed else 0)
