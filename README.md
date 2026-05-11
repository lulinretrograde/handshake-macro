# gta-rp-macro

Keyboard macro tool for farming handshakes on GTA RP servers.

## Requirements

- Python 3.8+
- [pynput](https://pypi.org/project/pynput/)

```
pip install pynput
```

## Usage

```
python gta_macro.py
```

Select a mode at the prompt and switch to your game window. Press `ESC` at any time to stop.

## Modes

### ❶ Send
Initiates a handshake. When you press `G` (the interact key), the script automatically presses `1` then `2` to navigate through the prompt — no need to manually hit the menu options each time.

| Key | Action |
|-----|--------|
| `G` | Triggers the `1` → `2` sequence |
| `ESC` | Exit |

### ❷ Receive
Accepts incoming handshakes. Press `F8` to start spamming `Y` so every handshake request gets accepted automatically.

| Key | Action |
|-----|--------|
| `F8` | Toggle Y-spam on / off |
| `ESC` | Exit |

## Notes

- Runs in the background and reads global keypresses — works while the game window is focused
- Windows Defender or antivirus may flag `pynput` due to its keyboard hook; this is a false positive
- Tested on Windows 10 / 11 with Python 3.11
