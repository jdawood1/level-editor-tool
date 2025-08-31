# Level Editor Tool (Python CLI) — Exporter & Telemetry

[![CI](https://github.com/jdawood1/level-editor-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/jdawood1/level-editor-tool/actions)

Developer-focused CLI prototype that demonstrates **workflow tooling, data exporters, and telemetry** — the kinds of skills relevant to engine/tools work.

---

## Highlights
- Define tiles/objects, build levels, and export to JSON
- Validates schema via Pydantic (v2)
- CLI subcommands: `new-level`, `add-object`, `export`, `stats`
- Telemetry: writes CSV of operations (timestamp, action, duration)
- Unit tests (pytest) + lint/format (black/ruff)
- GitHub Actions CI (lint + tests)

---

## Run in 30 seconds

```bash
# create venv + install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# create a level
python -m editor.cli new-level --name demo --width 20 --height 12

# add a few objects
python -m editor.cli add-object --level data/demo.json --type wall --x 3 --y 5
python -m editor.cli add-object --level data/demo.json --type coin --x 7 --y 2
python -m editor.cli add-object --level data/demo.json --type enemy --x 10 --y 6

# see stats + export
python -m editor.cli stats --level data/demo.json
python -m editor.cli export --level data/demo.json --out build/demo_level.json
```

**Outputs**
- `data/demo.json` → editable level
- `build/demo_level.json` → exported version
- `build/telemetry.csv` → logged CLI actions

---

## Repo Structure

```
level-editor-tool/
  editor/
    cli.py        # CLI entrypoint (Click)
    core.py       # core logic
    models.py     # Pydantic models (Level, LevelObject)
    telemetry.py  # telemetry logger
  tests/
    test_core.py
    test_models.py
  data/           # working levels (demo.json committed as example)
  build/          # exports + telemetry logs
  requirements.txt
  pyproject.toml
  README.md
```

---

## Roadmap
- [ ] `remove-object` CLI command
- [ ] Tkinter GUI wrapper
- [ ] Richer validation errors (duplicate objects, invalid coords)
- [ ] Schema versioning + migrations

---

## License
MIT © 2025 John Dawood
