# gta-rp-macro

Keyboard macro tool for farming handshakes on GTA RP servers. Two modes — one for sending a fully configurable key sequence, one for spamming accept prompts.

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
Listens for `G` in the background. When detected, executes a key sequence you configure at startup.

At launch you define the chain step by step — each step is a key to press followed by a delay:

```
Step 1 — key (or 'done'): 1
Step 1 — delay after '1' (e.g. 100ms): 80ms

Step 2 — key (or 'done'): 2
Step 2 — delay after '2': 100ms

Step 3 — key (or 'done'): done
```

The chain preview updates after every step so you can see exactly what will run.

**Accepted keys:** any single character (`e`, `1`, `y` …), `enter`, `space`, `tab`, `backspace`, `shift`, `ctrl`, `alt`, arrow keys (`up` `down` `left` `right`), `f1`–`f12`

**Delay format:** `500ms` · `0.5s` · `0.5` (bare number = seconds)

| Key | Action |
|-----|--------|
| `G` | Triggers the configured sequence |
| `ESC` | Exit |

### ❷ Receive
Toggles a Y-spam loop on and off. Useful for rapidly accepting incoming handshake prompts.

| Key | Action |
|-----|--------|
| `F8` | Toggle Y-spam on / off |
| `ESC` | Exit |

## Notes

- Runs in the background and reads global keypresses — works while the game window is focused
- Windows Defender or antivirus may flag `pynput` due to its keyboard hook; this is a false positive
- Tested on Windows 10 / 11 with Python 3.11
