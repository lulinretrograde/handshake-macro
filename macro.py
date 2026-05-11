#!/usr/bin/env python3
"""
GTA RP Macro Tool
─────────────────
Send mode    : Press G in-game → script auto-presses 1 then 2
Receive mode : Press F8 to toggle Y-spam on/off
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
def box(lines, title=""):
    """Render a rounded box around a list of strings."""
    W = shutil.get_terminal_size((80, 24)).columns - 2
    inner = W - 2  # space between the side borders

    def pad(s):
        # strip ANSI for length calculation isn't needed here, plain text only
        visible = len(s)
        return s + " " * max(0, inner - visible)

    top_title = f"─── {title} " if title else ""
    top_fill  = "─" * max(0, inner - len(top_title))
    print(f"╭{top_title}{top_fill}╮")
    for line in lines:
        print(f"│ {pad(line)} │")
    print(f"╰{'─' * inner}╯")


def section(label, W=None):
    if W is None:
        W = shutil.get_terminal_size((80, 24)).columns - 2
    inner = W - 2
    fill = "─" * max(0, inner - len(label) - 2)
    print(f"├─ {label} {fill}┤")


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


# ── Send mode ─────────────────────────────────────────────────────────────────
def run_send_mode():
    box([
        "Mode     :  Send",
        "Trigger  :  G  →  presses 1, then 2",
        "Exit     :  ESC",
    ], title="Send Mode")
    print()

    def on_press(key):
        try:
            if key == KeyCode.from_char('g'):
                time.sleep(0.08)
                tap(KeyCode.from_char('1'))
                time.sleep(0.06)
                tap(KeyCode.from_char('2'))
                log("G → pressed 1, 2")
        except Exception as e:
            log(f"ERROR: {e}")

    def on_release(key):
        if key == Key.esc:
            log("ESC pressed — stopping.")
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
        "Mode     :  Receive",
        "Toggle   :  F8  →  start / stop Y-spam",
        "Exit     :  ESC",
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
            log("ESC pressed — stopping.")
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
        "     Press G in-game → script presses 1 then 2",
        "",
        "  ❷  Receive mode",
        "     Press F8 to toggle Y-spam on / off",
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
    box(["Session ended."], title="Done")
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
