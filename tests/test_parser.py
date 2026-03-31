from __future__ import annotations

from pathlib import Path
from struct import Struct

import pytest

from fbpro98_play import InvalidPlyError, PlyFile


PLY_HEADER = Struct("<4si")


def write_ply_file(
    file_path: Path,
    *,
    chunk_id: bytes = b"P95:",
    stream_length: int = 25,
    play_category: int = 0x82,
    special_flag: int = 0x00,
    user_category: int = 0x02,
) -> None:
    file_path.write_bytes(
        PLY_HEADER.pack(chunk_id, stream_length)
        + bytes(22)
        + bytes([play_category, special_flag, user_category])
    )


def test_ply_file_reads_basic_metadata(tmp_path: Path) -> None:
    file_path = tmp_path / "test.ply"
    write_ply_file(
        file_path,
        stream_length=1234,
        play_category=0xAA,
        special_flag=0x10,
        user_category=0xBB,
    )

    play_file = PlyFile(file_path)

    assert play_file.file_path == file_path
    assert play_file.chunk_id == PlyFile.ChunkId.P95
    assert play_file.stream_length == 1234
    assert play_file.play_category == 0xAA
    assert play_file.special_flag == 0x10
    assert play_file.user_category == 0xBB


def test_ply_file_rejects_invalid_header(tmp_path: Path) -> None:
    file_path = tmp_path / "bad_header.ply"
    write_ply_file(file_path, chunk_id=b"BAD:")

    with pytest.raises(InvalidPlyError, match="Invalid header"):
        PlyFile(file_path)


def test_ply_file_rejects_truncated_metadata(tmp_path: Path) -> None:
    file_path = tmp_path / "truncated.ply"
    file_path.write_bytes(PLY_HEADER.pack(b"P95:", 25) + bytes(22))

    with pytest.raises(InvalidPlyError, match="File too small to contain play metadata"):
        PlyFile(file_path)
