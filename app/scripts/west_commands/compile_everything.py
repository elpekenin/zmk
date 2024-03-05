# Copyright (c) 2024 The ZMK Contributors
# SPDX-License-Identifier: MIT
"""(Try) Test all features."""

import subprocess
import sys
import yaml
from collections import defaultdict
from pathlib import Path

from west.commands import WestCommand

ZMK_YML = ".zmk.yml"

class CompileEverything(WestCommand):
    def __init__(self):
        super().__init__(
            name="compile_everything",
            help="(try) compile every possible configuration",
            description="(Try) compile every possible configuration.",
        )

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(
            self.name,
            help=self.help,
            description=self.description,
        )
        return parser

    def _gather_targets(self, boards_dir: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
        # map archs to boards >> arm: {kb1, kb2}
        boards = defaultdict(set)
        # map interconnect to boards >> pro_micro: {kb_3, kb_4}
        interconnects = defaultdict(set)

        for child in boards_dir.iterdir():
            if (
                not child.is_dir()  # overlay files at the root of the folder
                or child.name == "interconnects"  # nothing to grab
            ):
                continue

            if child.name == "shields":
                for shield in child.iterdir():
                    metadata_file = shield / f"{shield.name}{ZMK_YML}"
                    if not metadata_file.exists():
                        self.wrn(f"{shield.name} does not have a {ZMK_YML}", )
                        continue

                    # lets assume metadata.py was run already and the files
                    # have valid contents already. dont validate them
                    with metadata_file.open("r") as f:
                        metadata = yaml.safe_load(f)

                    # assuming we always have this attribute and it is
                    # always a 1-element list
                    interconnect = metadata["requires"][0]
                    interconnects[interconnect].add(shield.name)

            # at this stage, we should be on an arch folder
            else:
                arch = child.name
                for board_folder in child.iterdir():
                    for board in board_folder.glob(f"*{ZMK_YML}"):
                        boards[arch].add(board.name.rstrip(ZMK_YML))

        return boards, interconnects

    def _compile(self, zmk_app_dir: Path, command: str, display_name: str) -> bool:
        self.inf(f"Compiling {display_name}", end=" ")

        out = subprocess.run(
            command,
            capture_output=True,
            shell=True,
            cwd=zmk_app_dir,
        )

        if out.returncode == 0:
            self.inf("✓")
            return True
        else:
            self.inf("❌")
            self.err(out.stderr)
            return False

    def do_run(self, args, unknown_args):
        # walk backwards: .py / west_commands / script / app
        this_file = Path(__file__)
        zmk_app_dir = this_file.parent.parent.parent
        boards_dir = zmk_app_dir / "boards"

        boards, interconnects = self._gather_targets(boards_dir)

        failed = False
        for interconnect, shields in interconnects.items():
            # remove interconnects from target boards, they are not actual valid targets
            for _arch, boards_ in boards.items():
                boards_.discard(interconnect)

            # this code is broken right now, trying to compile "pro_micro" is not valid
            break
            for shield in shields:
                command = f"west build -p -b {interconnect} -- -DSHIELD={shield}"
                name = f"{interconnect}/{shield}"
                if not self._compile(zmk_app_dir, command, name):
                    failed = True

        for _arch, boards_ in boards.items():
            for board in boards_:
                command = f"west build -p -b {board}"
                name = board
                if not self._compile(zmk_app_dir, command, name):
                    failed = True

        sys.exit(1 if failed else 0)
