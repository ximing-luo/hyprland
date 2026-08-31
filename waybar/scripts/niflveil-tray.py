#!/usr/bin/python
"""Show minimized NiflVeil windows as a small icon tray."""

import fcntl
import json
import os
import signal
import subprocess
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gio", "2.0")
gi.require_version("GioUnix", "2.0")
gi.require_version("GLibUnix", "2.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import Gdk, Gio, GioUnix, GLib, GLibUnix, Gtk, GtkLayerShell


CACHE = Path("/tmp/minimize-state/windows.json")
NIFL = "/usr/local/bin/niflveil"


def normalize(text):
    return "".join(char for char in text.lower() if char.isalnum())


def load_apps():
    apps = []
    desktop_dirs = [Path.home() / ".local/share/applications", Path("/usr/share/applications")]

    for desktop_dir in desktop_dirs:
        for desktop_file in desktop_dir.glob("*.desktop"):
            try:
                app = GioUnix.DesktopAppInfo.new_from_filename(str(desktop_file))
            except (GLib.Error, TypeError):
                continue
            if app is None:
                continue

            apps.append({
                "app": app,
                "id": normalize(desktop_file.stem),
                "name": normalize(app.get_name() or ""),
                "wmclass": normalize(app.get_string("StartupWMClass") or ""),
            })

    return apps


def find_app(window, apps):
    window_class = normalize(window.get("class", ""))
    window_title = window.get("original_title", "")

    if window_class == "python3" and "有道词典" in window_title:
        window_class = "youdaodict"

    for app in apps:
        if app["wmclass"] and app["wmclass"] == window_class:
            return app["app"]

    for app in apps:
        if app["id"] == window_class or app["name"] == window_class:
            return app["app"]

    for app in apps:
        if window_class and (window_class in app["id"] or app["id"] in window_class):
            return app["app"]

    return None


def make_icon(app):
    if app is None or app.get_icon() is None:
        icon = Gio.ThemedIcon.new("application-x-executable")
    else:
        icon = app.get_icon()

    image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG)
    image.set_pixel_size(18)
    return image


def restore_window(button, address, window):
    subprocess.Popen([NIFL, "restore", address])
    window.destroy()


def close_window(*args):
    Gtk.main_quit()
    return False


def main():
    runtime_dir = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
    lock_path = runtime_dir / "niflveil-tray.lock"
    lock_file = lock_path.open("a+")

    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_file.seek(0)
        old_pid = lock_file.read().strip()
        if old_pid:
            os.kill(int(old_pid), signal.SIGTERM)
        return

    lock_file.seek(0)
    lock_file.truncate()
    lock_file.write(str(os.getpid()))
    lock_file.flush()

    windows = json.loads(CACHE.read_text()) if CACHE.exists() else []
    if not windows:
        subprocess.Popen(["notify-send", "niflveil", "没有已最小化的窗口"])
        return

    Gtk.init()
    display = Gdk.Display.get_default()
    screen = Gdk.Screen.get_default()
    cursor = json.loads(subprocess.check_output(["hyprctl", "cursorpos", "-j"], text=True))
    monitors = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"], text=True))
    monitor_index = next(index for index, item in enumerate(monitors) if item["focused"])
    hypr_monitor = monitors[monitor_index]
    monitor = display.get_monitor(monitor_index)
    geometry = monitor.get_geometry()

    panel_width = 136
    panel_width_scaled = round(panel_width * hypr_monitor["scale"])
    cursor_x = cursor["x"] - hypr_monitor["x"]
    left_margin = cursor_x - panel_width_scaled // 2 + round(30 * hypr_monitor["scale"])
    left_margin = max(6, min(left_margin, hypr_monitor["width"] - panel_width_scaled - 6))

    window = Gtk.Window()
    window.set_name("niflveil-tray")
    window.set_size_request(panel_width, -1)
    window.set_decorated(False)
    window.set_resizable(False)
    window.connect("destroy", close_window)
    window.connect("focus-out-event", close_window)
    window.connect("key-press-event", lambda widget, event: close_window() if event.keyval == Gdk.KEY_Escape else False)

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.set_namespace(window, "niflveil-tray")
    GtkLayerShell.set_layer(window, GtkLayerShell.Layer.OVERLAY)
    GtkLayerShell.set_monitor(window, monitor)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.TOP, True)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.LEFT, True)
    GtkLayerShell.set_margin(window, GtkLayerShell.Edge.TOP, 8)
    GtkLayerShell.set_margin(window, GtkLayerShell.Edge.LEFT, left_margin)
    GtkLayerShell.set_keyboard_mode(window, GtkLayerShell.KeyboardMode.ON_DEMAND)

    grid = Gtk.Grid()
    grid.set_row_spacing(4)
    grid.set_column_spacing(4)
    grid.set_margin_top(6)
    grid.set_margin_bottom(6)
    grid.set_margin_start(6)
    grid.set_margin_end(6)
    apps = load_apps()

    for index, hidden_window in enumerate(windows):
        app = find_app(hidden_window, apps)
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_image(make_icon(app))

        app_name = app.get_name() if app is not None else hidden_window.get("class", "窗口")
        title = hidden_window.get("original_title", "")
        button.set_tooltip_text(f"{app_name} - {title}")
        button.connect("clicked", restore_window, hidden_window["address"], window)
        grid.attach(button, index % 4, index // 4, 1, 1)

    style = Gtk.CssProvider()
    style.load_from_data(b"""
        window#niflveil-tray {
            background-color: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(11, 152, 228, 0.70);
            border-radius: 10px;
        }
        window#niflveil-tray button {
            min-width: 18px;
            min-height: 18px;
            padding: 5px;
            border: none;
            outline: none;
            border-radius: 6px;
            background: transparent;
            box-shadow: none;
        }
        window#niflveil-tray button:hover {
            background-color: transparent;
            box-shadow: inset 0 0 0 1px #e77d8f;
        }
        tooltip {
            font-size: 14px;
        }
    """)
    Gtk.StyleContext.add_provider_for_screen(screen, style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    window.add(grid)
    window.show_all()
    window.present()
    GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, close_window)
    Gtk.main()


if __name__ == "__main__":
    main()
