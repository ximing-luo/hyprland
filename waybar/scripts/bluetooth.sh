#!/usr/bin/env bash

# 获取当前连接的蓝牙设备名称
connected=$(bluetoothctl devices Connected)

if [ -z "$connected" ]; then
    jq -cn --arg text '<span size="11520">󰂯</span>' --arg tooltip "未连接蓝牙设备" '{text: $text, tooltip: $tooltip}'
    exit
fi

names=$(printf '%s\n' "$connected" | sed 's/^Device [^ ]* //' | paste -sd ',' | sed 's/,/, /g')
jq -cn --arg text "<span size=\"11520\">󰂯</span>   $names" --arg tooltip "已连接：$names" '{text: $text, tooltip: $tooltip}'
