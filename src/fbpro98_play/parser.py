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


@dataclass(frozen=True, slots=True)
class PlayerHeader:
    offset: int
    rank: int
    player_type: int
    position: int


class PlayFile:
    class ChunkId(str, Enum):
        P95 = "P95:"

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        buffer = self.file_path.read_bytes()
        if len(buffer) < PLY_HEADER.size:
            raise InvalidPlayFileError(
                f"File too small to contain P95 header in {self.file_path}"
            )

        chunk_id_bytes, self.stream_length = PLY_HEADER.unpack_from(buffer, 0)
        self.chunk_id = chunk_id_bytes.decode("ascii")
        if self.chunk_id != self.ChunkId.P95:
            raise InvalidPlayFileError(
                f"Invalid header '{self.chunk_id}' at 0x0 in {self.file_path}"
            )

        if len(buffer) != PLY_HEADER.size + self.stream_length:
            raise InvalidPlayFileError(
                f"File size {len(buffer)} does not match P95 chunk size "
                f"{PLY_HEADER.size + self.stream_length} in {self.file_path}"
            )

        if len(buffer) < PLY_METADATA_OFFSET + PLY_METADATA.size:
            raise InvalidPlayFileError(
                f"File too small to contain play metadata in {self.file_path}"
            )

        self.player_offsets = PLY_PLAYER_OFFSETS.unpack_from(buffer, PLY_PLAYER_OFFSETS_OFFSET)

        (
            self.play_category,
            self.special_flag,
            self.user_category,
        ) = PLY_METADATA.unpack_from(buffer, PLY_METADATA_OFFSET)

        self.player_headers = tuple(
            self._read_player_header(buffer, offset) for offset in self.player_offsets
        )

    def _read_player_header(self, buffer: bytes, offset: int) -> PlayerHeader:
        absolute_offset = PLY_PLAYER_DATA_BASE + offset
        if len(buffer) < absolute_offset + PLY_PLAYER_HEADER.size:
            raise InvalidPlayFileError(
                f"File too small to contain player header at 0x{absolute_offset:02X} "
                f"in {self.file_path}"
            )

        rank, player_type, position = PLY_PLAYER_HEADER.unpack_from(buffer, absolute_offset)
        return PlayerHeader(
            offset=offset,
            rank=rank,
            player_type=player_type,
            position=position,
        )


__all__ = [
    "InvalidPlayFileError",
    "PlayerHeader",
    "PlayFile",
]
