# fbpro98-play — Status

**Status: Complete**

Library for parsing Front Page Sports Football Pro '98 play (`.ply`) files into a typed, file-native model.

## Implemented

- Parses `.ply` files into `PlayFile` records, from a path or from raw bytes
- Exposes file-native classification: `play_category`, `special_category`, `user_category`, and resolved `category_name`
- Offense / defense / special-teams classification via `is_offensive`, `is_defensive`, `is_special_teams`
- Per-player headers (offset, rank, type, position) parsed from the player offset table
- Structural validation with `InvalidPlayFileError` for malformed files
- Public API surface re-exported from the package, with documented binary block schema

## Remaining

- Nothing outstanding for the current scope.
