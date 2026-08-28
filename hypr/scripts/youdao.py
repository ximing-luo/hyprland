#!/usr/bin/env python3
"""Open Youdao Dict or toggle its window through the tray icon."""

import json
import subprocess


# 查找有道词典的托盘项
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
    capture_output=True,
    text=True,
)

items = []
if items_result.returncode == 0:
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
    if "Youdao Dict" not in id_result.stdout:
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

# 托盘中没有有道词典时启动程序
subprocess.Popen(
    ["/usr/bin/youdao-dict"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True,
)
