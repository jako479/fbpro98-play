from __future__ import annotations

from enum import Enum
from pathlib import Path
from struct import Struct


PLY_HEADER = Struct("<4si")
PLY_METADATA = Struct("<BBB")
PLY_METADATA_OFFSET = PLY_HEADER.size + 22


class InvalidPlyError(Exception):
    pass


class PlyFile:
    class ChunkId(str, Enum):
        P95 = "P95:"

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        buffer = self.file_path.read_bytes()
        if len(buffer) < PLY_HEADER.size:
            raise InvalidPlyError(
                f"File too small to contain P95 header in {self.file_path}"
            )

        chunk_id_bytes, self.stream_length = PLY_HEADER.unpack_from(buffer, 0)
        self.chunk_id = chunk_id_bytes.decode("ascii")
        if self.chunk_id != self.ChunkId.P95:
            raise InvalidPlyError(
                f"Invalid header '{self.chunk_id}' at 0x0 in {self.file_path}"
            )

        if len(buffer) < PLY_METADATA_OFFSET + PLY_METADATA.size:
            raise InvalidPlyError(
                f"File too small to contain play metadata in {self.file_path}"
            )

        (
            self.play_category,
            self.special_flag,
            self.user_category,
        ) = PLY_METADATA.unpack_from(buffer, PLY_METADATA_OFFSET)


__all__ = [
    "InvalidPlyError",
    "PlyFile",
]
