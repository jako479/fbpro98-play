"""In-memory data model for FbPro98 .ply play files.

Defines the types the reader produces (PlayerHeader, PlayFile) and the
canonical category-code -> category-name lookup tables for offense, defense,
and special teams.
"""

from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from pathlib import Path

StrPath = str | PathLike[str]


OFFENSIVE_CATEGORIES = {
    0x01: "Run Right",
    0x03: "Pass Short Right",
    0x05: "Run Left",
    0x07: "Pass Short Left",
    0x09: "Run Middle",
    0x0B: "Pass Short Middle",
    0x0F: "Pass Razzle Dazzle",
    0x13: "Pass Medium Right",
    0x17: "Pass Medium Left",
    0x1B: "Pass Medium Middle",
    0x23: "Pass Long Right",
    0x31: "Goal Line Run",
    0x33: "Goal Line Pass",
    0xFF: "User Specific",
}

DEFENSIVE_CATEGORIES = {
    0x00: "Run Right",
    0x02: "Pass Short",
    0x04: "Run Left",
    0x08: "Run Middle",
    0x0C: "Run Dazzle",
    0x0E: "Pass Dazzle",
    0x12: "Pass Medium",
    0x22: "Pass Long",
    0x30: "Goal Line Run",
    0x32: "Goal Line Pass",
    0xFE: "User Specific",
}

SPECIAL_TEAMS_OFFENSIVE_CATEGORIES = {
    0x01: "Field Goal/PAT",
    0x02: "Kickoff",
    0x03: "Punt",
    0x04: "Onside Kick",
    0x05: "Fake FG Run",
    0x06: "Fake FG Pass",
    0x07: "Fake Punt Run",
    0x08: "Fake Punt Pass",
    0x09: "Free Kick",
    0x0A: "Squib Kick",
}

SPECIAL_TEAMS_DEFENSIVE_CATEGORIES = {
    0x01: "Field Goal/PAT Defense",
    0x02: "Kick Return",
    0x03: "Punt Return",
    0x04: "Onside Return",
    0x05: "Fake FG Run Defense",
    0x06: "Fake FG Pass Defense",
    0x07: "Fake Punt Run Defense",
    0x08: "Fake Punt Pass Defense",
    0x09: "Free Kick Return",
    0x0A: "Squib Return",
}


@dataclass(frozen=True, slots=True)
class PlayerHeader:
    """One player's header inside a .ply: file offset, depth-chart rank, type code, and position code."""

    offset: int
    rank: int
    player_type: int
    position: int


class PlayFile:
    """Parsed .ply file: stream length, category fields, and per-player headers."""

    def __init__(
        self,
        file_path: StrPath,
        stream_length: int,
        play_category: int,
        special_category: int,
        user_category: int,
        player_offsets: tuple[int, ...],
        player_headers: tuple[PlayerHeader, ...],
    ) -> None:
        self.file_path = Path(file_path)
        self.stream_length = stream_length
        self.play_category = play_category
        self.special_category = special_category
        self.user_category = user_category
        self.player_offsets = player_offsets
        self.player_headers = player_headers

    @property
    def is_offensive(self) -> bool:
        return self.play_category % 2 == 1

    @property
    def is_defensive(self) -> bool:
        return self.play_category % 2 == 0

    @property
    def is_special_teams(self) -> bool:
        return self.special_category != 0

    @property
    def category_name(self) -> str | None:
        """Resolve this play's human-readable category, picking the right lookup table.

        Special-teams plays (`special_category != 0`) map via the special-teams
        offensive or defensive table by `special_category`. Normal plays mask
        off the user-defined high bits (`user_category & 0x3F`) before looking
        up in the offense or defense table. Returns None for unrecognized codes.
        """
        if self.is_special_teams:
            mapping = SPECIAL_TEAMS_OFFENSIVE_CATEGORIES if self.is_offensive else SPECIAL_TEAMS_DEFENSIVE_CATEGORIES
            return mapping.get(self.special_category)
        base = self.user_category & 0x3F
        if self.is_offensive:
            return OFFENSIVE_CATEGORIES.get(base)
        return DEFENSIVE_CATEGORIES.get(base)
