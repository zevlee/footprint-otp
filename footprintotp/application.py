#!/usr/bin/env python3

from .window import Window
from . import __appdir__, __appname__, __conf__, __data__, __id__, DEFAULT, Utils
from os import mkdir
from os.path import join, exists
from platform import system
from json import loads, dumps
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gdk, Gio, GLib, Adw


class Application(Adw.Application):
    """
    Application
    """
    def __init__(self):
        """
        Constructor
        """
        super().__init__(
            application_id=__id__,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Set application name
        GLib.set_application_name(__appname__)

        # Set program name
        GLib.set_prgname(__id__)

    def do_startup(self):
        """
        Start up application
        """
        Gtk.Application.do_startup(self)

        # Restore any missing files and folders
        if not exists(__conf__):
            mkdir(__conf__)
        if not exists(__data__):
            mkdir(__data__)
        if not exists(join(__data__, "keys")):
            mkdir(join(__data__, "keys"))
        if not exists(join(__conf__, "settings.json")):
            with open(join(__conf__, "settings.json"), "w") as d:
                d.write(dumps(DEFAULT))
                d.close()
        if not exists(join(__data__, "otp.log")):
            open(join(__data__, "otp.log"), "w").close()
        
        # Validate config file
        Utils.validate_config("settings.json")

        # Set color scheme
        config = loads(open(join(__conf__, "settings.json"), "r").read())
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
                join(__appdir__, "usr", "share", "icons")
            )

    def do_activate(self):
        """
        Activate application
        """
        win = Window(self)
        win.show()
