# 字体、缩放与间距复现

本文记录当前 Arch Linux 桌面的实际字体匹配、组件字号和主要间距，用于在 Ubuntu 24.04 上尽量还原相同观感。

## 当前字体匹配

配置中出现的字体名称不一定就是最终使用的字体。Fontconfig 在当前 Arch Linux 上的实际匹配结果如下：

| 配置名称 | 当前实际字体 | 当前字体文件 |
| --- | --- | --- |
| `Sans`、`Sans Serif` | Noto Sans | `/usr/share/fonts/noto/NotoSans-Regular.ttf` |
| `Sans:lang=zh-cn` | 文泉驿正黑 | `/usr/share/fonts/wenquanyi/wqy-zenhei/wqy-zenhei.ttc` |
| `JetBrainsMono Nerd Font` | JetBrainsMono Nerd Font | `/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf` |
| `monospace` | Noto Sans Mono | `/usr/share/fonts/noto/NotoSansMono-Regular.ttf` |
| `monospace:lang=zh-cn` | Noto Sans Mono CJK | `/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc` |

`Sans` 是字体别名，不是固定字体。Ubuntu 如果把它解析为 Ubuntu Sans 或其他字体，字宽、行高和控件留白都会发生轻微变化。

## 各组件字体

| 组件 | 配置 | 字号或字重 |
| --- | --- | --- |
| GTK 3 | `Sans` | 9.5 |
| Waybar | `JetBrainsMono Nerd Font` | Bold 16px，部分模块为 12px 或 13px |
| Mako | `JetBrainsMono Nerd Font` | 11 |
| Hyprland 界面字体 | `JetBrains Mono Nerd Font` | 17 |
| Kitty | `JetBrains Mono Regular` | 最终字号 12 |
| Fcitx5 候选框 | `Sans` | 11 |
| Fcitx5 皮肤候选项 | `Sans` | 12 |
| Fcitx5 皮肤菜单 | `Sans` | 11 |
| Rofi | 未显式指定 | 由系统 Pango 默认字体决定 |

当前系统只安装了 JetBrains Mono 的 Nerd Font 版本。Kitty 中的 `JetBrains Mono Regular`、`JetBrains Mono Bold` 和 `JetBrains Mono Italic` 没有匹配到同名字体，Fontconfig 测试会回退到 Noto Sans Mono。因此，在 Ubuntu 上安装普通 JetBrains Mono 后，Kitty 的观感反而可能与当前 Arch 不同。

## 缩放和 DPI

Hyprland 当前显示参数：

```text
分辨率：1920x1080@144
缩放：1.25
Qt Wayland DPI：120
Xft DPI：120
```

120 DPI 等于基础 96 DPI 乘以 1.25。分数缩放会让 5px、7px、10px 等尺寸落在非整数物理像素上。GTK、Pango、Cairo、FreeType 和应用版本不同，可能产生约 1px 的取整差异。

## 主要间距

### Waybar

```text
高度：16px
顶部外边距：5px
底部外边距：-5px
左右外边距：10px
模块全局间距：0
```

各模块还使用了约 5–12px 的独立 margin 和 padding；工作区按钮主要使用左侧 5px、右侧 11px 的间距。

### Kitty

```text
窗口内边距：7px
最终字号：12
```

`kitty-theme.conf` 先设置字号 16，随后 `kitty.conf` 设置字号 12，因此最终以 12 为准。

### Mako

```text
外边距：20px
内边距：15px
通知宽度：300px
边框：2px
圆角：10px
```

### Rofi

```text
全局 spacing：2px
窗口 padding：5px
列表和输入框：1–2px 的额外间距
```

### Fcitx5

```text
候选项间距：3px
内容边距：12px
文字左右边距：12px
文字上下边距：6px
Wayland 分数缩放：启用
皮肤自身 DPI 缩放：禁用
```

## Ubuntu 24.04 字体安装

先安装当前 Arch 用到的 Noto 和中文回退字体：

```bash
sudo apt update
sudo apt install -y fontconfig fonts-noto-core fonts-noto-cjk fonts-wqy-zenhei
```

再按照 README 安装 JetBrains Mono Nerd Font，最后刷新字体缓存：

```bash
fc-cache -f
```

## 导入后验证

在 Ubuntu 上执行：

```bash
fc-match "Sans"
fc-match "Sans:lang=zh-cn"
fc-match "JetBrainsMono Nerd Font"
fc-match "monospace"
fc-match "monospace:lang=zh-cn"
```

若要尽量复现当前 Arch，结果应分别接近：

```text
NotoSans-Regular.ttf
wqy-zenhei.ttc
JetBrainsMonoNerdFont-Regular.ttf
NotoSansMono-Regular.ttf
NotoSansCJK-Regular.ttc
```

如果匹配结果不同，应先解决字体安装或 Fontconfig 回退差异，再调整 Waybar、Mako、Rofi 的 padding。字体字面高度和字宽不同，通常比 1px 的间距差异更影响整体观感。

## 后续统一建议

若仍有明显差异，可以依次处理：

1. 将 Kitty 改为目标系统确实存在的 `JetBrainsMono Nerd Font Mono`。
2. 给 Rofi 显式指定字体，避免跟随发行版默认字体。
3. 将 GTK 和 Fcitx5 中的 `Sans` 改为明确字体名称。
4. 最后再逐项调整 Waybar、Mako 和 Rofi 的 margin、padding。

不要一开始就修改全部间距。先保证字体文件、字体回退、显示缩放和 DPI 一致，才能判断剩余差异是否真的来自布局参数。
