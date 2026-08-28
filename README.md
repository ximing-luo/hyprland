# Hyprland 桌面配置

这是用于迁移到 Ubuntu 24.04 的 Hyprland 桌面配置仓库。仓库只跟踪实际使用的桌面配置，不包含 `~/.config` 中其他应用的缓存、账号状态和机器生成数据。

## 包含内容

- `hypr/`：Hyprland 0.55+ Lua 配置和窗口管理脚本
- `waybar/`：当前使用的配置、样式和 GPU 脚本
- `mako/`：通知样式
- `rofi/`：程序启动器
- `kitty/`：终端配置
- `waypaper/`：壁纸管理器配置
- `assets/fcitx5/Hyprland-Blue/`：Fcitx5 自定义皮肤资源
- `fcitx5/conf/classicui.conf`：Fcitx5 候选框样式和皮肤选择
- `fish/`：Fish 代理配置和 Fastfetch 快捷函数
- `lf/`：终端文件管理器配置
- `networkmanager-dmenu/`：Rofi 网络菜单
- `Thunar/`：在当前目录打开 Kitty 的自定义动作
- `gtk-3.0/`：GTK 字体设置

Waybar 只保留当前实际使用的以下文件：

```text
waybar/Waybar-3.0/config
waybar/Waybar-3.0/style.css
waybar/scripts/gpu-smart.sh
```

## Ubuntu 24.04 兼容性

本仓库的 `hypr/hyprland.lua` 使用 Hyprland 0.55 引入的 Lua 配置格式，因此需要 **Hyprland 0.55 或更高版本**。

Ubuntu 24.04 官方仓库没有与本配置兼容的 Hyprland，但 Constantin Piber 维护的第三方 PPA 为 Noble 提供 Hyprland 及其配套依赖。2026-08-28 直接读取 PPA 软件包索引时，Noble/amd64 的稳定版为 `0.56.2-1ppa1`，可以使用本仓库的 Lua 配置。

该 PPA 不是 Ubuntu 官方仓库，启用前应自行评估第三方仓库风险。相关资料：

- [Hyprland 官方安装说明](https://wiki.hypr.land/Getting-Started/Installation/)
- [Hyprland PPA](https://launchpad.net/~cppiber/+archive/ubuntu/hyprland)
- [PPA 打包源码](https://github.com/cpiber/hyprland-ppa)
- [Hyprland GitHub Releases](https://github.com/hyprwm/Hyprland/releases)

先确认版本：

```bash
Hyprland --version
```

版本低于 0.55 时不要导入 `hyprland.lua`。

## Ubuntu 24.04 安装桌面组件

### 1. 安装 Ubuntu 仓库组件

这条命令只安装 Ubuntu 24.04 仓库中可直接获得的外围组件，不包含 Hyprland 本体和后面单独安装的程序：

```bash
sudo apt update && sudo apt install -y software-properties-common && sudo add-apt-repository -y universe && sudo apt update && sudo apt install -y waybar mako-notifier rofi kitty fish lf thunar fcitx5 fcitx5-chinese-addons network-manager network-manager-gnome network-manager-config-connectivity-ubuntu blueman grim slurp wl-clipboard brightnessctl playerctl pavucontrol pipewire wireplumber jq libnotify-bin htop filelight python3 python3-pip python3-gi gir1.2-nm-1.0 pipx git curl build-essential flatpak fontconfig libwayland-dev wayland-protocols liblz4-dev
```

不同 Ubuntu 软件源中，Mako 的包名可能是 `mako-notifier`；如果提示找不到，先执行：

```bash
apt search '^mako'
```

### 2. Hyprland 本体

添加维护者提供的 PPA，并安装 Hyprland、权限代理、屏幕共享 Portal、UWSM 和 PPA 版本的 Waybar：

```bash
sudo add-apt-repository -y ppa:cppiber/hyprland
sudo apt update
apt-cache policy hyprland
sudo apt install -y hyprland hyprpolkitagent xdg-desktop-portal-hyprland uwsm waybar
```

`apt-cache policy hyprland` 必须显示候选版本来自 `ppa.launchpadcontent.net/cppiber/hyprland`。截至上述检查日期，预期版本为 `0.56.2-1ppa1`；以后应以目标机器实际显示的候选版本为准。

安装后必须确认：

```bash
Hyprland --version
```

版本低于 0.55 时不要导入 `hypr/hyprland.lua`。

### 3. Awww

Awww 是 Waypaper 当前配置使用的壁纸后端。Ubuntu 24.04 没有对应的官方软件包，需要先通过 [rustup](https://rustup.rs/) 安装最新稳定版 Rust，再从上游源码构建：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
git clone https://codeberg.org/LGFae/awww.git ~/.local/src/awww
cd ~/.local/src/awww
cargo build --release
install -Dm755 target/release/awww ~/.local/bin/awww
install -Dm755 target/release/awww-daemon ~/.local/bin/awww-daemon
```

确认 `~/.local/bin` 已加入 `PATH`，然后检查：

```bash
awww-daemon --help
```

### 4. Waypaper

Waypaper 官方支持通过 `pipx` 安装：

```bash
pipx ensurepath
pipx install waypaper
```

重新登录后确认：

```bash
waypaper --help
```

### 5. NetworkManager Dmenu

上游没有提供 Ubuntu 安装包，官方方式是把脚本复制到 `PATH`：

```bash
git clone https://github.com/firecat53/networkmanager-dmenu.git ~/.local/src/networkmanager-dmenu
install -Dm755 ~/.local/src/networkmanager-dmenu/networkmanager_dmenu ~/.local/bin/networkmanager_dmenu
```

本仓库已经提供 `~/.config/networkmanager-dmenu/config.ini`，不需要让程序覆盖生成。

### 6. Mission Center

使用 Flathub 安装：

```bash
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --user -y flathub io.missioncenter.MissionCenter
mkdir -p ~/.local/bin
ln -sf ~/.local/share/flatpak/exports/bin/io.missioncenter.MissionCenter ~/.local/bin/missioncenter
```

如果 Flatpak 导出目录没有生成该文件，可以把 Hyprland 中的 `missioncenter` 命令改成：

```text
flatpak run io.missioncenter.MissionCenter
```

### 7. JetBrains Mono Nerd Font

Waybar 和 Mako 依赖 Nerd Font 图标，普通 JetBrains Mono 不够。安装到当前用户：

```bash
mkdir -p ~/.local/share/fonts/JetBrainsMonoNerdFont
curl -fL https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.tar.xz -o /tmp/JetBrainsMono.tar.xz
tar -xf /tmp/JetBrainsMono.tar.xz -C ~/.local/share/fonts/JetBrainsMonoNerdFont
fc-cache -f
```

确认字体名称：

```bash
fc-match "JetBrainsMono Nerd Font"
```

### 8. Snipaste

Snipaste 官方为 Linux 提供 AppImage。请从 [Snipaste 官方下载页](https://www.snipaste.com/download.html) 下载 Linux x86_64 AppImage，然后安装为配置使用的命令名：

```bash
install -Dm755 ~/Downloads/Snipaste*.AppImage ~/.local/bin/Snipaste
```

AppImage 的实际文件名可能变化，执行前应先用 `ls ~/Downloads/Snipaste*.AppImage` 确认。

### 9. NiflVeil

NiflVeil 是当前机器上的自定义程序，不属于 Ubuntu、Flatpak 或公开上游软件包。目前没有可用的源码仓库，因此无法给出可复现的 Ubuntu 安装命令。

在源码重新发布并提供安装方式前，其他用户应注释以下功能：

- Hyprland 的 `Alt+Escape`、`Alt+R` 绑定
- Waybar 的 `custom/niflveil` 模块

### 10. 其他可选程序

这些程序不是桌面基础组件，需要使用者按需安装；缺少时对应自启动项或快捷键不可用：

```text
v2rayN
youdao-dict
```

全部安装完后检查命令：

```bash
command -v Hyprland waybar mako rofi kitty fish lf thunar awww-daemon waypaper networkmanager_dmenu Snipaste missioncenter
```

## 字体和主题

界面使用 `JetBrainsMono Nerd Font` 和 Nerd Font 图标。普通 JetBrains Mono 不包含 Waybar 所需的全部图标，请按上面的步骤安装 Nerd Font 版本。

当前系统的实际字体回退、各组件字号、DPI 和间距记录见 [`FONTS.md`](FONTS.md)。迁移后观感不一致时，应先按照该文档核对 Fontconfig 匹配结果。

Rofi 使用的主题已经包含在仓库中：

```text
~/.config/rofi/themes/glue_pro_blue.rasi
```

## 导入配置

该仓库本身就是 `~/.config`。在新机器上，先备份已有配置，再克隆到临时目录并逐项复制：

```bash
git clone <你的 GitHub 仓库地址> ~/dotfiles
cp -a ~/.config ~/.config.backup
cp -a ~/dotfiles/. ~/.config/
```

Fcitx5 的皮肤资源不属于 `~/.config`，需要再复制到用户数据目录：

```bash
mkdir -p ~/.local/share/fcitx5/themes
cp -a ~/.config/assets/fcitx5/Hyprland-Blue ~/.local/share/fcitx5/themes/
fcitx5 -r -d
```

仓库中的 `fcitx5/conf/classicui.conf` 已将亮色和暗色皮肤都设置为 `Hyprland-Blue`。仓库不包含个人词库、输入历史或 Rime 生成数据。

不要在一个已有大量应用配置的 `~/.config` 中直接执行强制覆盖或删除命令。仓库中的 `.gitignore` 只控制 Git 跟踪范围，不会删除本机其他配置。

导入后赋予脚本执行权限：

```bash
chmod +x ~/.config/hypr/scripts/*.py
chmod +x ~/.config/waybar/scripts/gpu-smart.sh
```

将 Fish 设为登录 Shell 是可选操作：

```bash
chsh -s /usr/bin/fish
```

重新登录后生效。

## 导入前必须调整的机器差异

### 显示器和硬件

- `hypr/hyprland.lua` 固定了 `1920x1080@144` 和 `1.25` 缩放。
- Waybar 不固定电池、背光设备和温度区域，由 Waybar 自动选择可用设备。
- 目标机器使用 NVIDIA 显卡；GPU 模块调用 `nvidia-smi`，Hyprland 配置也保留了 NVIDIA 驱动环境变量。
- 导入前需要在 Ubuntu 上正确安装 NVIDIA 驱动，并确认 `nvidia-smi` 可以正常运行。

### 壁纸

壁纸图片没有包含在仓库中。上传版本的 `waypaper/config.ini` 使用通用目录：

```text
~/Pictures/Wallpapers
```

导入后需要自己创建目录、放入壁纸，并在 Waypaper 中选择当前壁纸：

```bash
mkdir -p ~/Pictures/Wallpapers
waypaper
```

默认不预设具体壁纸，也不绑定 `eDP-1` 等机器特定显示器。多显示器用户应在 Waypaper 中为自己的显示器选择壁纸并保存配置。

### 自定义脚本和程序

Hyprland 配置按命令名调用以下可选程序：

```text
hyprpolkitagent
v2rayN
Snipaste
niflveil
```

这些程序需要位于 `PATH` 中。未安装时，相应自启动项或快捷键不可用。`Alt+R` 还引用未包含在仓库中的 `~/.local/bin/niflveil-restore`。

LF 配置还引用若干 `~/.local/bin/` 自用脚本，目标机器缺少它们时，相应 LF 快捷键不可用。

### Fish 代理

Fish 配置保留了使用 `127.0.0.1:10808` 的 `en`/`dis` 代理函数，但默认不会自动启用。使用其他代理端口时请自行修改。

## 验证

导入后先做静态检查：

```bash
luac -p ~/.config/hypr/hyprland.lua
Hyprland --verify-config -c ~/.config/hypr/hyprland.lua
fish -n ~/.config/fish/config.fish
```

在已运行的 Hyprland 会话中重新加载并检查错误：

```bash
hyprctl reload
hyprctl configerrors
```

最后实际测试 Waybar、Rofi、Mako、壁纸、截图、网络菜单、音量和亮度快捷键。
