# fbpro98-play

`fbpro98-play` parses Front Page Sports Football Pro '98 `.ply` files.

Current scope:

- validate the `P95` header
- expose `play_category`
- expose `special_flag`
- expose `user_category`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Usage

```python
from fbpro98_play import PlyFile

play_file = PlyFile("some_play.ply")
print(play_file.play_category)
print(play_file.special_flag)
print(play_file.user_category)
```

## Testing

```bash
pytest
```

Current tests cover parser behavior for:

- valid `P95` metadata reads
- invalid headers
- truncated metadata
