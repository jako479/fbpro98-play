# Front Page Sports Football Pro '98 `.ply` File Format (Little-Endian)

**Status:** Draft
**Owner:** FBPro98 Play Library
**Encoding:** Integers are little-endian; chunk IDs are ASCII.

---

## 1. Container Overview

A `.ply` currently appears to contain a single `P95` chunk.

Each file begins with a standard chunk header:

1. **ID** - 4 ASCII bytes
2. **size** - 4-byte little-endian integer

For observed `.ply` files:

- `ID` is always `"P95:"`
- `size` is the payload length after the 8-byte chunk header
- total file length is `8 + size`

---

## 2. Chunk: P95 - Play Definition

### 2.1 Header (8 bytes)

| Offset | Type    | Name | Description                                         |
| -----: | :------ | :--- | :-------------------------------------------------- |
| 0x0000 | char[4] | ID   | `"P95:"`                                            |
| 0x0004 | u32     | size | Payload size in bytes (everything after this field) |

**Notes**

- Total file length = `8 + size`.
- The current parser rejects any chunk ID other than `"P95:"`.

### 2.2 Player Offsets Table (fixed 22 bytes)

- Exactly 11 entries.
- Each entry is a `u16` little-endian value.
- Each offset points to one player record.
- Offsets are relative to the end of the 8-byte header (byte offset `0x08`).

| Field       | Value / Rule                                   |
| :---------- | :--------------------------------------------- |
| Count       | 11                                             |
| Entry type  | `u16` (little-endian)                          |
| Total size  | `11 * 2 = 22 bytes`                            |
| Offset base | End of `P95` header (byte offset `0x08`)       |
| First entry | Observed as `0x0019` in all sampled real files |

**Observed slot order from `fbpro_ply.hsl` comments**

1. QB
2. C
3. LT
4. LG
5. RG
6. RT
7. TE
8. RWR
9. LWR
10. LHB
11. RHB

### 2.3 Metadata (fixed 3 bytes)

These are the currently parsed metadata bytes after the 11-entry offsets table.

| Offset | Type | Name          | Description                              |
| -----: | :--- | :------------ | :--------------------------------------- |
| 0x001E | u8   | play_category | Category byte supplied by the game       |
| 0x001F | u8   | special_flag  | Special-teams flag                       |
| 0x0020 | u8   | user_category | User category byte stored in the file    |

**Observed notes**

- `special_flag` is usually `0x00` in sampled offensive/defensive plays.
- `special_flag = 0x02` was observed in the sampled kickoff file `AF-KO.ply`.
- No stock/custom flag has been identified in the currently parsed header region.

### 2.4 Player Records (variable length, partially understood)

Each of the 11 offsets points to a variable-length player record.

The current HSL model suggests this leading structure:

| Relative Offset | Type | Name     | Description |
| --------------: | :--- | :------- | :---------- |
| `+0x00`         | u8   | rank     | Depth / rank |
| `+0x01`         | u8   | type     | Player record type |
| `+0x02`         | u16  | position | Position code |
| `+0x04`         | ...  | data     | Variable logic-box data |

**Observed/inferred player type values from `fbpro_ply.hsl`**

- `0x01` = pre-snap player
- `0x02` = after-snap player
- `0x04` = kicking player

**Observed/inferred position codes from `fbpro_ply.hsl` comments**

- `0x20` = QB
- `0x12` = C
- `0x11` = T
- `0x10` = G
- `0x81` = TE
- `0x80` = WR
- `0x42` = HB

### 2.5 Logic Boxes (partial)

The HSL describes each player as containing one or more logic-box sequences:

- pre-snap logic boxes
- middle-of-play logic boxes
- end-of-play logic boxes

Each logic box is modeled as:

| Relative Offset | Type | Name         | Description |
| --------------: | :--- | :----------- | :---------- |
| `+0x00`         | u16  | numLogic     | Logic-box sequence number |
| `+0x02`         | u16  | x            | X coordinate / field value |
| `+0x04`         | u16  | y            | Y coordinate / field value |
| `+0x06`         | u16  | commandCount | Number of commands |
| `+0x08`         | ...  | commands     | Variable-length command array |

### 2.6 Commands (partial)

The HSL models each command as:

| Relative Offset | Type | Name | Description |
| --------------: | :--- | :--- | :---------- |
| `+0x00`         | u16  | type | Command type |
| `+0x02`         | u16  | x    | Command data / field value |
| `+0x04`         | u16  | y    | Command data / field value |

The exact command-type meanings are still being reverse engineered.

---

## 3. Reader Contract

- API:
  - `PlyFile(path)` returns a parsed file wrapper.
- Behavior:
  - Read the `P95` header.
  - Validate that `len(file) == 8 + size`.
  - Read the 11-entry player offsets table.
  - Validate that the file is large enough to contain the 3 known metadata bytes.
  - Read the first 4 bytes of each player record as a `PlayerHeader`.
  - Expose:
    - `chunk_id`
    - `stream_length`
    - `player_offsets`
    - `player_headers`
    - `play_category`
    - `special_flag`
    - `user_category`
- Errors:
  - Raise `InvalidPlyError` for structural issues such as bad chunk ID, size mismatch, truncated metadata, or truncated player headers.

---

## 4. Validation & Test Vectors

Current checked-in test fixtures cover:

- offensive plays
- defensive plays
- special-teams plays
- one known invalid zero-byte file

The current parser test set verifies:

- `ID == "P95:"`
- `len(file) == 8 + size` for all checked-in valid fixtures
- exact 11-player offset tables for all checked-in valid fixtures
- exact first-player-header tuples for all 11 players in all checked-in valid fixtures
- metadata bytes at offsets `0x1E..0x20`
- rejection of a zero-byte invalid file

---

## 5. Open Questions

- The full player-record layout is not yet specified.
- The boundaries between pre-snap, middle-of-play, and end-of-play logic sequences are not yet documented.
- Command type values are still largely unknown.
- No stock/custom play flag has been identified yet in the currently documented `.ply` structure.
