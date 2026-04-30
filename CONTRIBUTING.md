# Contributing to HAMIOS

Thank you for your interest in contributing!

## Getting started

```bash
git clone https://github.com/fvdijke/HAMIOS.git
cd HAMIOS
pip install pillow pystray   # runtime deps
pip install pyinstaller      # only for building the EXE
python HAMIOS.py             # run from source
```

## Code style

- Python 3.10+, single-file architecture (`HAMIOS.py`)
- `theme_manager.py` is the only separate module
- `_font()` for all tkinter fonts — never hardcode "Segoe UI" or similar
- `_FONT_SANS` / `_FONT_MONO` constants for canvas drawing
- `_fetch_with_retry()` for all HTTP calls; store results in `_cache_set()`
- Log meaningful events with `log.info()` / `log.warning()`
- All user-visible strings must have an entry in `_T` (built-in English)
  and a matching key in every `langs/lang_*.json`

## Pull requests

1. Fork the repo and create a feature branch: `git checkout -b feat/my-feature`
2. Keep commits focused; one logical change per commit
3. Run the syntax check before opening a PR:
   ```bash
   python -m py_compile HAMIOS.py
   python -m flake8 HAMIOS.py --max-line-length=110 --ignore=E501,W503
   ```
4. Update `HAMIOS.py` docstring changelog and version if needed
5. Open a PR against `main` with a clear description

## Adding a new language pack

Copy an existing `langs/lang_xx.json`, change `meta.code` and `meta.name`,
translate `strings` and `solar_tips`. HAMIOS auto-detects the file on startup.

## Reporting bugs / requesting features

Use [GitHub Issues](https://github.com/fvdijke/HAMIOS/issues).
Please include OS, screen resolution, and HAMIOS.log (if relevant).
