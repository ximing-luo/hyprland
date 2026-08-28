#!/usr/bin/env python3
import json
import subprocess


DEFAULT_GAPS_OUT = 10
HIDDEN_GAPS_OUT = 3


def has_compact_gap():
    result = subprocess.run(
        ["hyprctl", "getoption", "general:gaps_out", "-j"],
        check=True,
        capture_output=True,
        text=True,
    )
    gap_values = json.loads(result.stdout).get("css", "").split()
    return bool(gap_values) and all(
        int(value) == HIDDEN_GAPS_OUT for value in gap_values
    )


def set_outer_gap(gap):
    subprocess.run(
        ["hyprctl", "eval", f"hl.config({{ general = {{ gaps_out = {gap} }} }})"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    was_hidden = has_compact_gap()

    # SIGUSR1 toggles Waybar. Only update the gap if Waybar received the signal.
    subprocess.run(["pkill", "-SIGUSR1", "waybar"], check=True)
    set_outer_gap(DEFAULT_GAPS_OUT if was_hidden else HIDDEN_GAPS_OUT)


if __name__ == "__main__":
    main()
