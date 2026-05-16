# fbpro98-play — Architecture

Library that parses FbPro '98 `.ply` play files into a typed, file-native model.

For system-level context (how this fits with `pnfl-playpool` and `pnfl-playcatalog`), see [pnfl-docs/Design/play-architecture.md](../pnfl-docs/Design/play-architecture.md).

## Module layout

```
src/fbpro98_play/
├── __init__.py    # public API re-exports
├── model.py       # PlayFile, PlayerHeader, category constants
└── reader.py      # parse_play, read_play, InvalidPlayFileError
```

`specs/ply.hexpat` documents the on-disk byte layout.

## What this package does

- Parses `.ply` files into `PlayFile` records
- Exposes file-native classification:
  - `play_category` (raw integer from the file)
  - `special_category` (raw integer)
  - `user_category` (raw integer)
  - Properties: `is_offensive`, `is_defensive`, `is_special_teams`
- Validates structural correctness of `.ply` bytes

## What this package assumes

- Input files come from FbPro '98 or another producer that follows the `.ply` format

## What this package enforces

Raise `InvalidPlayFileError` for:
- File too small to contain a header
- Invalid block magic
- Stream length / offset table not internally consistent
- Player record prefix corruption

## What this package does NOT do

- PNFL-specific classification or folder layout (lives in `pnfl-playpool`)
- Build collections / lookup tables (lives in `pnfl-playpool`)
- Workbook export (lives in `pnfl-playcatalog`)

## Testing

- `tests/` — parsing real `.ply` fixtures, structural error paths

Fixtures are real game-produced `.ply` files; that is the authoritative ground truth for any wire-format question.
