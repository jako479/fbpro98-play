"""Parse FbPro98 .ply play files into PlayFile objects.

Decodes the P95 block: header, 11 player offsets, play metadata
(play_category / special_category / user_category), and per-player headers.
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path

from fbpro98_play.model import PlayerHeader, PlayFile
from fbpro98_play.schema import (
    ID_P95,
    PLY_HEADER,
    PLY_METADATA,
    PLY_METADATA_OFFSET,
    PLY_PLAYER_DATA_BASE,
    PLY_PLAYER_HEADER,
    PLY_PLAYER_OFFSETS,
    PLY_PLAYER_OFFSETS_OFFSET,
)

StrPath = str | PathLike[str]


class InvalidPlayFileError(Exception):
    """Raised when a `.ply` file is structurally invalid."""


def read_play(path: StrPath) -> PlayFile:
    """Read and parse a `.ply` play file."""
    file_path = Path(path)
    return parse_play(file_path.read_bytes(), file_path)


def parse_play(buffer: bytes, path: StrPath = "<buffer>") -> PlayFile:
    """Parse a `.ply` play from raw bytes."""
    file_path = Path(path)

    if len(buffer) < PLY_HEADER.size:
        raise InvalidPlayFileError(f"File too small to contain P95 header in {file_path}")

    block_id, stream_length = PLY_HEADER.unpack_from(buffer, 0)
    if block_id != ID_P95:
        block_id_str = block_id.decode("ASCII", errors="replace")
        raise InvalidPlayFileError(f"Invalid header '{block_id_str}' at 0x0 in {file_path}")

    if len(buffer) != PLY_HEADER.size + stream_length:
        raise InvalidPlayFileError(
            f"File size {len(buffer)} does not match P95 block size {PLY_HEADER.size + stream_length} in {file_path}"
        )

    if len(buffer) < PLY_METADATA_OFFSET + PLY_METADATA.size:
        raise InvalidPlayFileError(f"File too small to contain play metadata in {file_path}")

    player_offsets = PLY_PLAYER_OFFSETS.unpack_from(buffer, PLY_PLAYER_OFFSETS_OFFSET)

    play_category, special_category, user_category = PLY_METADATA.unpack_from(
        buffer,
        PLY_METADATA_OFFSET,
    )

    player_headers = tuple(_parse_player_header(buffer, offset, file_path) for offset in player_offsets)

    return PlayFile(
        file_path,
        stream_length,
        play_category,
        special_category,
        user_category,
        player_offsets,
        player_headers,
    )


def _parse_player_header(buffer: bytes, offset: int, path: Path) -> PlayerHeader:
    absolute_offset = PLY_PLAYER_DATA_BASE + offset
    if len(buffer) < absolute_offset + PLY_PLAYER_HEADER.size:
        raise InvalidPlayFileError(f"File too small to contain player header at 0x{absolute_offset:02X} in {path}")

    rank, player_type, position = PLY_PLAYER_HEADER.unpack_from(buffer, absolute_offset)
    return PlayerHeader(
        offset=offset,
        rank=rank,
        player_type=player_type,
        position=position,
    )
