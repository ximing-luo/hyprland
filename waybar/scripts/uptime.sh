#!/usr/bin/env bash

# 将系统运行秒数格式化为紧凑的天、小时和分钟
read -r uptime_seconds _ < /proc/uptime
uptime_seconds=${uptime_seconds%.*}

days=$((uptime_seconds / 86400))
hours=$((uptime_seconds % 86400 / 3600))
minutes=$((uptime_seconds % 3600 / 60))
seconds=$((uptime_seconds % 60))

if ((days > 0)); then
    printf '{"text":"%dd %dh","tooltip":"%dd %dh %dm %ds"}\n' "$days" "$hours" "$days" "$hours" "$minutes" "$seconds"
elif ((hours > 0)); then
    printf '{"text":"%dh %dm","tooltip":"%dh %dm %ds"}\n' "$hours" "$minutes" "$hours" "$minutes" "$seconds"
elif ((minutes > 0)); then
    printf '{"text":"%dm","tooltip":"%dm %ds"}\n' "$minutes" "$minutes" "$seconds"
else
    printf '{"text":"%ds","tooltip":"%ds"}\n' "$seconds" "$seconds"
fi
