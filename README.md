# Galactic Defenders

Galactic Defenders is a fullscreen Pygame arcade shooter. Download a packaged desktop build from the [latest releases](https://github.com/aadhimaganti-sys/galacticdefenders/releases/latest), or run it from source below.

## Run from source

Requires Python 3.11 or newer.

```bash
python -m venv .venv
```

Activate the environment, then install dependencies and start the game:

```bash
python -m pip install -r requirements.txt
python main.py
```

On Linux, activate with `source .venv/bin/activate`. On Windows PowerShell, use `.venv\Scripts\Activate.ps1`. On macOS, use `source .venv/bin/activate`.

## Controls

- Move: `W`, `A`, `S`, `D` or the arrow keys
- Fire: `Space` or `Enter`
- Toggle auto-pilot during play: `P`
- Return to the menu: `Esc`

## Desktop downloads

The `main` branch automatically builds and publishes archives for Linux x86_64, Windows x86_64, macOS Apple silicon, and macOS Intel. Extract the archive, then launch `GalacticDefenders.exe` on Windows or run `./GalacticDefenders` from the extracted folder on Linux and macOS. If macOS blocks the unsigned build, allow it in **System Settings → Privacy & Security**.