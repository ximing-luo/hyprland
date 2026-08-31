#!/usr/bin/env python3
"""Cycle visible workspaces while skipping internal float stashes."""

import json
import subprocess
import sys


active_result = subprocess.run(["hyprctl", "activeworkspace", "-j"], check=True, capture_output=True, text=True)
active = json.loads(active_result.stdout)
active_id = active["id"]
active_monitor = active["monitor"]

workspaces_result = subprocess.run(["hyprctl", "workspaces", "-j"], check=True, capture_output=True, text=True)
workspaces = json.loads(workspaces_result.stdout)

workspace_ids: list[int] = []
for workspace in workspaces:
    workspace_id = workspace.get("id")
    workspace_name = workspace.get("name")
    workspace_monitor = workspace.get("monitor")
    if not isinstance(workspace_id, int) or workspace_id <= 0:
        continue
    if not isinstance(workspace_name, str) or workspace_name.startswith("__floatstash_"):
        continue
    if workspace_monitor != active_monitor:
        continue
    workspace_ids.append(workspace_id)

workspace_ids.sort()
target_id = active_id

if sys.argv[1] == "next":
    for workspace_id in workspace_ids:
        if workspace_id > active_id:
            target_id = workspace_id
            break
    else:
        target_id = workspace_ids[0]

if sys.argv[1] == "prev":
    for workspace_id in reversed(workspace_ids):
        if workspace_id < active_id:
            target_id = workspace_id
            break
    else:
        target_id = workspace_ids[-1]

subprocess.run(["hyprctl", "dispatch", f"hl.dsp.focus({{ workspace={target_id} }})"], check=True)
