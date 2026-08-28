# 代理函数
function en
    set -gx http_proxy http://127.0.0.1:10808
    set -gx https_proxy http://127.0.0.1:10808
    # set -gx all_proxy socks5://127.0.0.1:10808
    # set -gx socks_proxy socks5://127.0.0.1:10808
    set_color green; echo "Proxy enabled"; set_color normal
end

function dis
    set -e -g http_proxy
    set -e -g https_proxy
    set -e -g all_proxy
    set -e -g socks_proxy
    set_color red; echo "Proxy disabled"; set_color normal
end

# en >/dev/null  # 按需取消注释以自动启用本机代理

