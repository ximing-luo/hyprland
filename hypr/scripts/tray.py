#!/usr/bin/env python3
"""Toggle supported app windows through their tray D-Bus items."""

import json
import subprocess
import sys


app = sys.argv[1]

if app == "ceru":
    item_id = "ceru-music_status_icon"
    app_name = "Ceru Music"

if app == "youdao":
    item_id = "Youdao Dict"
    app_name = "有道词典"


items_result = subprocess.run(
    [
        "busctl",
        "--user",
        "--json=short",
        "get-property",
        "org.kde.StatusNotifierWatcher",
        "/StatusNotifierWatcher",
        "org.kde.StatusNotifierWatcher",
        "RegisteredStatusNotifierItems",
    ],
    check=True,
    capture_output=True,
    text=True,
)

items = json.loads(items_result.stdout)["data"]

for item in items:
    service, path = item.split("/", 1)
    object_path = "/" + path
    id_result = subprocess.run(
        [
            "gdbus",
            "call",
            "--session",
            "--dest",
            service,
            "--object-path",
            object_path,
            "--method",
            "org.freedesktop.DBus.Properties.Get",
            "org.kde.StatusNotifierItem",
            "Id",
        ],
        capture_output=True,
        text=True,
    )
    if item_id not in id_result.stdout:
        continue

    subprocess.run(
        [
            "gdbus",
            "call",
            "--session",
            "--dest",
            service,
            "--object-path",
            object_path,
            "--method",
            "org.kde.StatusNotifierItem.Activate",
            "0",
            "0",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    raise SystemExit(0)

subprocess.run(["notify-send", app_name, "没有找到托盘图标"], check=False)
raise SystemExit(1)
