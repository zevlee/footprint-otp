#!/usr/bin/env python3

from lib.window import Window
from lib.utils import Utils
from os import mkdir
from os.path import join, exists
from platform import system
from json import loads, dumps
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gdk, Gio, GLib, Adw


class Application(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=Utils.ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Set application name
        GLib.set_application_name(Utils.NAME)

        # Set program name
        GLib.set_prgname(Utils.ID)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # Restore any missing files and folders
        if not exists(Utils.CONFIG_DIR):
            mkdir(Utils.CONFIG_DIR)
        if not exists(Utils.DATA_DIR):
            mkdir(Utils.DATA_DIR)
        if not exists(join(Utils.DATA_DIR, "keys")):
            mkdir(join(Utils.DATA_DIR, "keys"))
        if not exists(join(Utils.CONFIG_DIR, "otp.json")):
            with open(join(Utils.CONFIG_DIR, "otp.json"), "w") as d:
                d.write(dumps(Utils.DEFAULT))
                d.close()
        if not exists(join(Utils.DATA_DIR, "otp.log")):
            open(join(Utils.DATA_DIR, "otp.log"), "w").close()

        # Set color scheme
        config = loads(open(join(Utils.CONFIG_DIR, "otp.json"), "r").read())
        appearance = config["appr"]
        if appearance:
            self.get_style_manager().set_color_scheme(
                Adw.ColorScheme.FORCE_DARK
            )
        else:
            self.get_style_manager().set_color_scheme(
                Adw.ColorScheme.FORCE_LIGHT
            )

        # Set up icons for linux
        if system() == "Linux":
            icon_theme = Gtk.IconTheme.get_for_display(
                Gdk.Display.get_default()
            )
            icon_theme.add_search_path(
                join(Utils.APP_DIR, "usr", "share", "icons")
            )

    def do_activate(self):
        win = Window(self)
        win.show()
