from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from fbpro98_play import InvalidPlayFileError, PlayFile, PlayerHeader


TESTS_DIR = Path(__file__).resolve().parent
FIXTURE_DIR = TESTS_DIR / "data"


@dataclass(frozen=True, slots=True)
class FixtureExpectation:
    fixture_name: str
    stream_length: int
    play_category: int
    special_flag: int
    user_category: int
    player_offsets: tuple[int, ...]
    player_headers: tuple[tuple[int, int, int], ...]


VALID_FIXTURES = [
    FixtureExpectation(
        fixture_name="AFGZoutX.ply",
        stream_length=441,
        play_category=0x9B,
        special_flag=0x00,
        user_category=0xB3,
        player_offsets=(25, 73, 97, 121, 157, 185, 209, 261, 301, 353, 389),
        player_headers=(
            (1, 2, 32),
            (1, 1, 18),
            (1, 0, 17),
            (2, 0, 16),
            (1, 0, 16),
            (2, 0, 17),
            (3, 0, 128),
            (4, 0, 128),
            (2, 0, 128),
            (1, 0, 66),
            (1, 0, 128),
        ),
    ),
    FixtureExpectation(
        fixture_name="AF-KO.ply",
        stream_length=491,
        play_category=0x01,
        special_flag=0x02,
        user_category=0x01,
        player_offsets=(25, 75, 115, 155, 199, 239, 283, 331, 371, 411, 451),
        player_headers=(
            (1, 4, 2048),
            (1, 0, 1025),
            (5, 0, 128),
            (1, 0, 65),
            (4, 0, 128),
            (3, 0, 512),
            (3, 0, 128),
            (3, 0, 1024),
            (6, 0, 128),
            (2, 0, 1025),
            (2, 0, 512),
        ),
    ),
    FixtureExpectation(
        fixture_name="JJ10drw3.ply",
        stream_length=389,
        play_category=0x89,
        special_flag=0x00,
        user_category=0x89,
        player_offsets=(25, 49, 85, 121, 157, 193, 229, 261, 293, 325, 357),
        player_headers=(
            (1, 2, 32),
            (1, 1, 18),
            (2, 0, 17),
            (1, 0, 16),
            (2, 0, 16),
            (1, 0, 17),
            (1, 0, 129),
            (3, 0, 128),
            (1, 0, 128),
            (2, 0, 129),
            (2, 0, 128),
        ),
    ),
    FixtureExpectation(
        fixture_name="JJ43rlZB.ply",
        stream_length=379,
        play_category=0x88,
        special_flag=0x00,
        user_category=0x84,
        player_offsets=(25, 59, 87, 115, 143, 177, 215, 249, 277, 311, 345),
        player_headers=(
            (3, 0, 512),
            (2, 0, 257),
            (1, 0, 257),
            (2, 0, 258),
            (2, 0, 512),
            (1, 0, 512),
            (2, 0, 1025),
            (1, 0, 258),
            (1, 0, 1024),
            (1, 0, 1025),
            (2, 0, 1024),
        ),
    ),
    FixtureExpectation(
        fixture_name="JJ7XWagR.ply",
        stream_length=517,
        play_category=0xA3,
        special_flag=0x00,
        user_category=0x97,
        player_offsets=(25, 97, 121, 149, 177, 205, 241, 275, 333, 387, 469),
        player_headers=(
            (1, 2, 32),
            (1, 1, 18),
            (2, 0, 17),
            (1, 0, 16),
            (2, 0, 16),
            (1, 0, 17),
            (2, 0, 128),
            (1, 0, 128),
            (4, 0, 128),
            (3, 0, 128),
            (1, 0, 129),
        ),
    ),
    FixtureExpectation(
        fixture_name="KCC33rmA.ply",
        stream_length=461,
        play_category=0x82,
        special_flag=0x00,
        user_category=0x88,
        player_offsets=(25, 49, 97, 149, 197, 233, 261, 299, 335, 377, 419),
        player_headers=(
            (2, 0, 258),
            (2, 1, 512),
            (1, 0, 258),
            (3, 0, 512),
            (1, 0, 512),
            (1, 0, 257),
            (2, 0, 1025),
            (1, 0, 1025),
            (2, 0, 1024),
            (3, 0, 1024),
            (1, 0, 1024),
        ),
    ),
    FixtureExpectation(
        fixture_name="MN22PLz.ply",
        stream_length=599,
        play_category=0x92,
        special_flag=0x00,
        user_category=0xA2,
        player_offsets=(25, 87, 135, 191, 239, 301, 357, 413, 461, 499, 555),
        player_headers=(
            (1, 0, 258),
            (1, 0, 1024),
            (1, 0, 1025),
            (6, 0, 1024),
            (2, 0, 258),
            (5, 0, 1024),
            (2, 0, 512),
            (3, 0, 1024),
            (1, 0, 512),
            (4, 0, 1024),
            (2, 0, 1024),
        ),
    ),
    FixtureExpectation(
        fixture_name="NY26RM00.ply",
        stream_length=473,
        play_category=0x89,
        special_flag=0x00,
        user_category=0x89,
        player_offsets=(25, 73, 109, 133, 157, 193, 229, 271, 331, 367, 415),
        player_headers=(
            (1, 2, 32),
            (1, 1, 18),
            (1, 0, 17),
            (2, 0, 16),
            (1, 0, 16),
            (2, 0, 17),
            (4, 0, 128),
            (1, 0, 129),
            (2, 0, 129),
            (1, 0, 65),
            (1, 0, 66),
        ),
    ),
    FixtureExpectation(
        fixture_name="SF1YemTy.ply",
        stream_length=381,
        play_category=0xB3,
        special_flag=0x00,
        user_category=0x87,
        player_offsets=(25, 59, 83, 107, 135, 163, 187, 233, 267, 301, 347),
        player_headers=(
            (1, 2, 32),
            (1, 1, 18),
            (1, 0, 17),
            (1, 0, 16),
            (2, 0, 16),
            (2, 0, 17),
            (6, 0, 128),
            (5, 0, 128),
            (1, 0, 129),
            (3, 0, 128),
            (4, 0, 128),
        ),
    ),
]


@pytest.mark.parametrize("expected", VALID_FIXTURES, ids=lambda expected: expected.fixture_name)
def test_play_file_reads_real_fixture_structure(expected: FixtureExpectation) -> None:
    file_path = FIXTURE_DIR / expected.fixture_name

    play_file = PlayFile(file_path)

    assert play_file.file_path == file_path
    assert play_file.chunk_id == PlayFile.ChunkId.P95
    assert play_file.stream_length == expected.stream_length
    assert play_file.play_category == expected.play_category
    assert play_file.special_flag == expected.special_flag
    assert play_file.user_category == expected.user_category
    assert play_file.player_offsets == expected.player_offsets
    assert play_file.player_headers == tuple(
        PlayerHeader(
            offset=offset,
            rank=rank,
            player_type=player_type,
            position=position,
        )
        for offset, (rank, player_type, position) in zip(
            expected.player_offsets,
            expected.player_headers,
            strict=True,
        )
    )


@pytest.mark.parametrize("expected", VALID_FIXTURES, ids=lambda expected: expected.fixture_name)
def test_real_fixture_parser_invariants(expected: FixtureExpectation) -> None:
    file_path = FIXTURE_DIR / expected.fixture_name
    file_bytes = file_path.read_bytes()
    play_file = PlayFile(file_path)

    assert len(file_bytes) == 8 + play_file.stream_length
    assert len(play_file.player_offsets) == 11
    assert play_file.player_offsets[0] == 25
    assert tuple(sorted(play_file.player_offsets)) == play_file.player_offsets
    assert all(offset > 0 for offset in play_file.player_offsets)
    assert all(
        8 + header.offset + 4 <= len(file_bytes)
        for header in play_file.player_headers
    )


def test_play_file_rejects_known_invalid_fixture() -> None:
    file_path = FIXTURE_DIR / "PS7Xmids.ply"

    with pytest.raises(InvalidPlayFileError, match="File too small to contain P95 header"):
        PlayFile(file_path)

