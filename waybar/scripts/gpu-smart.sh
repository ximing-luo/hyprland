#!/bin/bash
# 智能 GPU 信息脚本 - 修复版

CACHE_FILE="/tmp/waybar-gpu-cache"
STATE_FILE="/tmp/waybar-gpu-state"
CACHE_AGE=2

# 获取当前显示状态
get_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo "0" > "$STATE_FILE"
        echo "0"
    fi
}

# 切换状态
toggle_state() {
    current_state=$(get_state)
    if [ "$current_state" = "0" ]; then
        echo "1" > "$STATE_FILE"
    else
        echo "0" > "$STATE_FILE"
    fi
}

# 直接获取并解析 GPU 信息
get_parsed_gpu_info() {
    # 直接调用 nvidia-smi，避免中间脚本问题
    read usage mem_used mem_total temp power <<< $(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits | tr ',' ' ')
    
    mem_percentage=$((mem_used * 100 / mem_total))
    
    # 计算显存 GB，确保 bc 可用
    if command -v bc >/dev/null 2>&1; then
        mem_gb=$(echo "scale=1; $mem_used/1024" | bc)
    else
        # 使用 awk 作为备选
        mem_gb=$(awk "BEGIN {printf \"%.1f\", $mem_used/1024}")
    fi
    
    # 确保 mem_gb 不为空
    if [ -z "$mem_gb" ]; then
        mem_gb="0.0"
    fi
    mem_gb=$(printf "%.1f" "$mem_gb")
    
    echo "$usage $mem_percentage $mem_gb $temp $power"
}

# 处理参数
case "$1" in
    "toggle")
        toggle_state
        state=$(get_state)
        read usage mem_percent mem_gb temp power <<< $(get_parsed_gpu_info)
        
        if [ "$state" = "1" ]; then
            echo "{\"text\": \"* ${usage}%  ${mem_gb}G\", \"tooltip\": \"GPU 详细信息:\\n使用率: ${usage}%\\n显存: ${mem_percent}% (${mem_gb}G)\\n温度: ${temp}℃\\n功率: ${power}W\"}"
        else
            echo "{\"text\": \"* ${usage}%  ${mem_percent}%\", \"tooltip\": \"GPU 详细信息:\\n使用率: ${usage}%\\n显存: ${mem_percent}% (${mem_gb}G)\\n温度: ${temp}℃\\n功率: ${power}W\"}"
        fi
        ;;
    *)
        state=$(get_state)
        read usage mem_percent mem_gb temp power <<< $(get_parsed_gpu_info)
        
        if [ "$state" = "1" ]; then
            echo "{\"text\": \"* ${usage}%  ${mem_gb}G\", \"tooltip\": \"GPU 详细信息:\\n使用率: ${usage}%\\n显存: ${mem_percent}% (${mem_gb}G)\\n温度: ${temp}℃\\n功率: ${power}W\"}"
        else
            echo "{\"text\": \"* ${usage}%  ${mem_percent}%\", \"tooltip\": \"GPU 详细信息:\\n使用率: ${usage}%\\n显存: ${mem_percent}% (${mem_gb}G)\\n温度: ${temp}℃\\n功率: ${power}W\"}"
        fi
        ;;
esac
