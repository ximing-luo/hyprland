# NiflVeil 最小化托盘

这套功能不是 freedesktop StatusNotifier 托盘。Waybar 的普通 `tray` 只能显示主动注册 D-Bus 托盘图标的应用，不能直接容纳普通 Hyprland 窗口。这里由 NiflVeil 负责隐藏和恢复窗口，再由 Waybar 与两个前端脚本提供入口。

## 组件关系

```text
Alt+Escape
    -> niflveil minimize
    -> 隐藏当前窗口并写入 /tmp/minimize-state/windows.json
    -> 通知 Waybar 刷新 custom/niflveil

Waybar custom/niflveil
    -> niflveil show 输出 Waybar JSON
    -> 点击图标运行 waybar/scripts/niflveil-tray.py
    -> GTK layer-shell 图标面板
    -> niflveil restore <窗口地址>

Alt+R
    -> hypr/scripts/niflveil-restore
    -> Rofi 文本菜单
    -> niflveil restore <窗口地址> 或 restore-all
```

NiflVeil 是状态和窗口操作的主体。`niflveil-tray.py` 只是 Waybar 点击后出现的 GTK 面板，`niflveil-restore` 是键盘使用的 Rofi 备用入口；两者读取同一份缓存，不会各自维护窗口状态。

## 仓库文件

- `hypr/hyprland.lua`：绑定 `Alt+Escape` 和 `Alt+R`。
- `hypr/scripts/niflveil-restore`：Rofi 恢复菜单，可恢复单个窗口或全部窗口。
- `waybar/Waybar-3.0/config`：声明 `custom/niflveil`，显示状态并设置点击命令。
- `waybar/Waybar-3.0/style.css`：Waybar 中 NiflVeil 模块的样式。
- `waybar/scripts/niflveil-tray.py`：点击 Waybar 后显示窗口图标面板。

## 依赖

必须先有可执行的 `niflveil` 命令。当前程序是本机自定义二进制，本仓库不提交该二进制，也没有可用的公开安装源；迁移到其他机器时需要另行安装，并确保下面的命令成功：

```bash
command -v niflveil
niflveil show
```

脚本还需要：

- Hyprland 和 Waybar
- Python 3、PyGObject、GTK 3、GTK Layer Shell 的 GI 绑定
- `rofi`、`jq`、`libnotify`/`notify-send`
- Nerd Font 图标字体

Arch Linux 可先检查相关软件包：

```bash
pacman -Q waybar rofi jq libnotify python-gobject gtk3 gtk-layer-shell
```

Ubuntu 上需要 GTK 3、PyGObject 和 GTK Layer Shell 对应的 GIR 包；具体包名以目标发行版的软件源为准。

## 安装位置

按仓库整体导入后，相关路径应为：

```text
~/.config/hypr/hyprland.lua
~/.config/hypr/scripts/niflveil-restore
~/.config/waybar/Waybar-3.0/config
~/.config/waybar/Waybar-3.0/style.css
~/.config/waybar/scripts/niflveil-tray.py
```

确保两个脚本可执行：

```bash
chmod +x ~/.config/hypr/scripts/niflveil-restore
chmod +x ~/.config/waybar/scripts/niflveil-tray.py
```

随后重载 Hyprland 并重启 Waybar，使绑定和模块配置生效。

## 使用

- `Alt+Escape`：把当前窗口交给 NiflVeil 最小化。
- 点击 Waybar 的 NiflVeil 图标：打开靠近鼠标位置的窗口图标面板；点击图标恢复对应窗口。
- `Alt+R`：打开 Rofi 列表；可以恢复一个窗口或选择“全部恢复”。
- `Esc`、点击面板外部或面板失去焦点：关闭 GTK 图标面板，不改变已最小化窗口。

## 验证与排错

先最小化一个普通窗口，再检查状态：

```bash
jq . /tmp/minimize-state/windows.json
niflveil show
```

如果 Waybar 没有出现图标，检查 `custom/niflveil` 的 `exec`、Waybar 日志以及 `niflveil show` 的 JSON 输出。若图标存在但点击没有面板，直接运行：

```bash
~/.config/waybar/scripts/niflveil-tray.py
```

若 Rofi 菜单没有内容，确认缓存文件存在且是 JSON 数组，并检查：

```bash
~/.config/hypr/scripts/niflveil-restore
```

缓存位于 `/tmp`，重启后消失属于正常现象。不要手工把窗口地址长期保存到配置中，它只对当前 Hyprland 会话有效。
