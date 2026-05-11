#!/usr/bin/env python3
"""
GTA RP Macro Tool
─────────────────
Send mode    : G triggers a configurable key sequence
Receive mode : F8 toggles Y-spam on/off
ESC          : Quit at any time
"""

import sys
import time
import threading
import shutil

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode, Controller
except ImportError:
    print("[ERROR] pynput not found.")
    print("        Run: pip install pynput")
    input("Press Enter to exit...")
    sys.exit(1)

# ── Shared state ──────────────────────────────────────────────────────────────
controller = Controller()
_spam_active = False
_spam_thread = None
_lock = threading.Lock()

# ── Box drawing ───────────────────────────────────────────────────────────────
def term_width():
    return shutil.get_terminal_size((80, 24)).columns

def box(lines, title=""):
    W     = term_width() - 2
    inner = W - 2

    def pad(s):
        return s + " " * max(0, inner - len(s))

    top_title = f"─── {title} " if title else ""
    top_fill  = "─" * max(0, inner - len(top_title))
    print(f"╭{top_title}{top_fill}╮")
    for line in lines:
        print(f"│ {pad(line)} │")
    print(f"╰{'─' * inner}╯")

def divider(label=""):
    W     = term_width() - 2
    inner = W - 2
    if label:
        fill = "─" * max(0, inner - len(label) - 3)
        print(f"├── {label} {fill}┤")
    else:
        print(f"├{'─' * inner}┤")

# ── Helpers ───────────────────────────────────────────────────────────────────
def tap(key, hold=0.05):
    try:
        controller.press(key)
        time.sleep(hold)
        controller.release(key)
    except Exception as e:
        print(f"  [WARN] tap() failed: {e}")

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"  {ts}  {msg}")

def parse_delay(raw: str) -> float:
    """
    Accept formats:  500ms  |  0.5s  |  0.5  (bare number = seconds)
    Returns seconds as a float.
    """
    raw = raw.strip().lower()
    try:
        if raw.endswith("ms"):
            return float(raw[:-2]) / 1000.0
        if raw.endswith("s"):
            return float(raw[:-1])
        return float(raw)
    except ValueError:
        return None

def parse_key(raw: str):
    """Return a pynput KeyCode or Key from a string like 'e', 'enter', 'space'."""
    raw = raw.strip().lower()
    # Check named keys first
    named = {
        "enter": Key.enter, "space": Key.space, "tab": Key.tab,
        "backspace": Key.backspace, "esc": Key.esc, "escape": Key.esc,
        "shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt,
        "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
        "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
        "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
        "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
    }
    if raw in named:
        return named[raw]
    if len(raw) == 1:
        return KeyCode.from_char(raw)
    return None

def chain_summary(steps: list) -> list:
    """Return lines describing the current chain for display."""
    lines = [f"  Trigger  :  G  (fixed)", ""]
    for i, (key_raw, delay) in enumerate(steps, 1):
        delay_str = f"{int(delay * 1000)} ms" if delay < 1 else f"{delay:.2f} s"
        lines.append(f"  Step {i:<4}:  press {key_raw!r:<12} then wait {delay_str}")
    return lines

# ── Send mode setup ───────────────────────────────────────────────────────────
def configure_steps() -> list:
    """
    Interactively build the step chain.
    Returns list of (key_raw, delay_seconds) tuples.
    """
    steps = []

    box([
        "  Build your key sequence.",
        "  G is always the trigger — define what happens after.",
        "",
        "  For each step enter a key, then a delay.",
        "  Delay format:  500ms  |  0.5s  |  0.5 (bare number = seconds)",
        "",
        "  Type 'done' as the key when you have enough steps.",
    ], title="Send Mode — Setup")
    print()

    while True:
        step_num = len(steps) + 1

        # ── key ──
        while True:
            try:
                raw_key = input(f"  Step {step_num} — key (or 'done'): ").strip()
            except (EOFError, KeyboardInterrupt):
                sys.exit(0)

            if raw_key.lower() == "done":
                if not steps:
                    print("  [!] Add at least one step first.")
                    continue
                return steps

            k = parse_key(raw_key)
            if k is None:
                print(f"  [!] Unrecognised key '{raw_key}'. Try: e, 1, enter, space …")
                continue
            break

        # ── delay ──
        while True:
            try:
                raw_delay = input(f"  Step {step_num} — delay after '{raw_key}' (e.g. 100ms): ").strip()
            except (EOFError, KeyboardInterrupt):
                sys.exit(0)

            d = parse_delay(raw_delay)
            if d is None or d < 0:
                print("  [!] Invalid delay. Examples: 100ms  0.5s  0.3")
                continue
            break

        steps.append((raw_key, d))
        print()

        # preview current chain
        box(chain_summary(steps), title=f"Chain so far — {len(steps)} step(s)")
        print()

# ── Send mode runner ──────────────────────────────────────────────────────────
def run_send_mode():
    steps = configure_steps()

    # Build resolved (pynput key, delay) pairs once
    resolved = [(parse_key(raw), delay) for raw, delay in steps]

    print()
    box(
        chain_summary(steps) + ["", "  Running — press G in-game.  ESC to quit."],
        title="Send Mode — Active"
    )
    print()

    executing = threading.Lock()

    def execute_chain():
        with executing:
            for key, delay in resolved:
                tap(key, hold=0.05)
                time.sleep(delay)
            log("chain executed")

    def on_press(key):
        try:
            if key == KeyCode.from_char('g'):
                t = threading.Thread(target=execute_chain, daemon=True)
                t.start()
        except Exception as e:
            log(f"ERROR: {e}")

    def on_release(key):
        if key == Key.esc:
            log("ESC — stopping.")
            return False

    try:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        log(f"FATAL: {e}")

# ── Receive mode ──────────────────────────────────────────────────────────────
def _y_spam_loop():
    while True:
        with _lock:
            if not _spam_active:
                break
        tap(KeyCode.from_char('y'), hold=0.03)
        time.sleep(0.05)

def run_receive_mode():
    global _spam_active, _spam_thread
    box([
        "  Mode    :  Receive",
        "  Toggle  :  F8  →  start / stop Y-spam",
        "  Exit    :  ESC",
    ], title="Receive Mode")
    print()

    def on_press(key):
        global _spam_active, _spam_thread
        try:
            if key == Key.f8:
                with _lock:
                    if not _spam_active:
                        _spam_active = True
                        _spam_thread = threading.Thread(target=_y_spam_loop, daemon=True)
                        _spam_thread.start()
                        log("Y-spam  ON")
                    else:
                        _spam_active = False
                        log("Y-spam  OFF")
        except Exception as e:
            log(f"ERROR: {e}")

    def on_release(key):
        global _spam_active
        if key == Key.esc:
            with _lock:
                _spam_active = False
            log("ESC — stopping.")
            return False

    try:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        log(f"FATAL: {e}")

    if _spam_thread and _spam_thread.is_alive():
        _spam_thread.join(timeout=1.0)

# ── Main menu ─────────────────────────────────────────────────────────────────
def main():
    print()
    box([
        "",
        "  GTA RP Macro Tool",
        "",
        "  ❶  Send mode",
        "     G triggers a configurable key sequence",
        "",
        "  ❷  Receive mode",
        "     F8 toggles Y-spam on / off",
        "",
    ], title="GTA RP Macro Tool")
    print()

    while True:
        try:
            choice = input("  Select mode [1/2]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Cancelled.")
            sys.exit(0)

        if choice == "1":
            print()
            run_send_mode()
            break
        elif choice == "2":
            print()
            run_receive_mode()
            break
        else:
            print("  [!] Enter 1 or 2.")

    print()
    box(["  Session ended."], title="Done")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Ctrl+C — bye.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  [FATAL] {e}")
        input("  Press Enter to exit...")
        sys.exit(1)
