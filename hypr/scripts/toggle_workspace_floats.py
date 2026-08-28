#!/usr/bin/env python3
"""Toggle floating windows into a per-workspace special workspace."""

from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]+$")


def hyprctl_json(command: str) -> Any:
    result = subprocess.run(
        ["hyprctl", command, "-j"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def notify_error(message: str) -> None:
    print(f"toggle_workspace_floats: {message}", file=sys.stderr)
    subprocess.run(
        ["hyprctl", "notify", "-1", "4000", "rgb(ff5555)", f"Float stash: {message}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def client_address(client: dict[str, Any]) -> str | None:
    address = client.get("address")
    if isinstance(address, str) and ADDRESS_RE.fullmatch(address):
        return address
    return None


def run_batch(commands: list[str]) -> None:
    if not commands:
        return
    subprocess.run(
        ["hyprctl", "--batch", "; ".join(f"dispatch {command}" for command in commands)],
        check=True,
        capture_output=True,
        text=True,
    )


def focus_rank(client: dict[str, Any]) -> int:
    rank = client.get("focusHistoryID")
    return rank if isinstance(rank, int) and rank >= 0 else sys.maxsize


def toggle_workspace_floats() -> None:
    workspace = hyprctl_json("activeworkspace")
    workspace_id = workspace.get("id")
    if not isinstance(workspace_id, int) or workspace_id <= 0:
        raise RuntimeError("当前活动工作区不是普通数字工作区")

    clients = hyprctl_json("clients")
    if not isinstance(clients, list):
        raise RuntimeError("无法读取 Hyprland 窗口列表")

    stash_name = f"special:floatstash-{workspace_id}"
    visible_floats: list[dict[str, Any]] = []
    stashed_floats: list[dict[str, Any]] = []

    for client in clients:
        if not isinstance(client, dict) or client_address(client) is None:
            continue

        client_workspace = client.get("workspace")
        if not isinstance(client_workspace, dict):
            continue

        if client_workspace.get("name") == stash_name:
            stashed_floats.append(client)
            continue

        if (
            client_workspace.get("id") == workspace_id
            and client.get("mapped") is True
            and client.get("floating") is True
            and client.get("pinned") is not True
        ):
            visible_floats.append(client)

    # Visible floating windows always take precedence. This lets newly opened
    # floating windows join an already hidden stash before the next restore.
    if visible_floats:
        commands = [
            f"hl.dsp.window.move({{ window='address:{client_address(client)}', workspace='{stash_name}', follow=false }})"
            for client in visible_floats
        ]
        run_batch(commands)
        return

    if not stashed_floats:
        return

    most_recent = min(stashed_floats, key=focus_rank)
    focus_address = client_address(most_recent)
    commands = [
        f"hl.dsp.window.move({{ window='address:{client_address(client)}', workspace='{workspace_id}', follow=false }})"
        for client in stashed_floats
    ]
    if focus_address is not None:
        commands.append(f"hl.dsp.focus({{ window='address:{focus_address}' }})")
    run_batch(commands)


def main() -> int:
    runtime_dir = Path(os.environ.get("XDG_RUNTIME_DIR", f"/tmp/hyprland-{os.getuid()}"))
    runtime_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = runtime_dir / "toggle-workspace-floats.lock"

    try:
        with lock_path.open("w") as lock_file:
            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return 0
            toggle_workspace_floats()
    except (json.JSONDecodeError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        notify_error(str(error))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
