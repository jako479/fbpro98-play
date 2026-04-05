from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from struct import Struct

PLY_HEADER = Struct("<4si")
PLY_PLAYER_OFFSETS = Struct("<11H")
PLY_METADATA = Struct("<BBB")
PLY_PLAYER_HEADER = Struct("<BBH")

PLY_PLAYER_OFFSETS_OFFSET = PLY_HEADER.size
PLY_METADATA_OFFSET = PLY_PLAYER_OFFSETS_OFFSET + PLY_PLAYER_OFFSETS.size
PLY_PLAYER_DATA_BASE = PLY_HEADER.size


class InvalidPlayFileError(Exception):
    pass


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
    offset: int
    rank: int
    player_type: int
    position: int


class PlayFile:
    class ChunkId(str, Enum):
        P95 = "P95:"

    def __init__(
        self,
        file_path: str | Path,
        chunk_id: str,
        stream_length: int,
        play_category: int,
        special_category: int,
        user_category: int,
        player_offsets: tuple[int, ...],
        player_headers: tuple[PlayerHeader, ...],
    ) -> None:
        self.file_path = Path(file_path)
        self.chunk_id = chunk_id
        self.stream_length = stream_length
        self.play_category = play_category
        self.special_category = special_category
        self.user_category = user_category
        self.player_offsets = player_offsets
        self.player_headers = player_headers

    @classmethod
    def from_file(cls, file_path: str | Path) -> PlayFile:
        """Read and parse a .ply file."""
        path = Path(file_path)
        return cls.from_buffer(path.read_bytes(), file_path)

    @classmethod
    def from_buffer(cls, buffer: bytes, file_path: str | Path = "<buffer>") -> PlayFile:
        """Parse a .ply from raw bytes. Separates I/O from parsing."""
        path = Path(file_path)

        if len(buffer) < PLY_HEADER.size:
            raise InvalidPlayFileError(f"File too small to contain P95 header in {path}")

        chunk_id_bytes, stream_length = PLY_HEADER.unpack_from(buffer, 0)
        chunk_id = chunk_id_bytes.decode("ascii")
        if chunk_id != cls.ChunkId.P95:
            raise InvalidPlayFileError(f"Invalid header '{chunk_id}' at 0x0 in {path}")

        if len(buffer) != PLY_HEADER.size + stream_length:
            raise InvalidPlayFileError(
                f"File size {len(buffer)} does not match P95 chunk size "
                f"{PLY_HEADER.size + stream_length} in {path}"
            )

        if len(buffer) < PLY_METADATA_OFFSET + PLY_METADATA.size:
            raise InvalidPlayFileError(f"File too small to contain play metadata in {path}")

        player_offsets = PLY_PLAYER_OFFSETS.unpack_from(buffer, PLY_PLAYER_OFFSETS_OFFSET)

        play_category, special_category, user_category = PLY_METADATA.unpack_from(
            buffer, PLY_METADATA_OFFSET,
        )

        player_headers = tuple(
            cls._parse_player_header(buffer, offset, path) for offset in player_offsets
        )

        return cls(
            file_path, chunk_id, stream_length, play_category,
            special_category, user_category, player_offsets, player_headers,
        )

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
        if self.is_special_teams:
            mapping = (
                SPECIAL_TEAMS_OFFENSIVE_CATEGORIES
                if self.is_offensive
                else SPECIAL_TEAMS_DEFENSIVE_CATEGORIES
            )
            return mapping.get(self.special_category)
        base = self.user_category & 0x3F
        if self.is_offensive:
            return OFFENSIVE_CATEGORIES.get(base)
        return DEFENSIVE_CATEGORIES.get(base)

    @staticmethod
    def _parse_player_header(
        buffer: bytes, offset: int, path: Path,
    ) -> PlayerHeader:
        absolute_offset = PLY_PLAYER_DATA_BASE + offset
        if len(buffer) < absolute_offset + PLY_PLAYER_HEADER.size:
            raise InvalidPlayFileError(
                f"File too small to contain player header at 0x{absolute_offset:02X} in {path}"
            )

        rank, player_type, position = PLY_PLAYER_HEADER.unpack_from(buffer, absolute_offset)
        return PlayerHeader(
            offset=offset,
            rank=rank,
            player_type=player_type,
            position=position,
        )
