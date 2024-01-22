from os import mkdir
from os.path import join, exists
from platform import system
from json import loads, dumps
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gdk, Gio, GLib, Adw
from . import *
from .window import Window


class Application(Adw.Application):
    """
    Application
    """
    def __init__(self):
        """
        Constructor
        """
        super().__init__(
            application_id=ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Set application name
        GLib.set_application_name(APPNAME)

        # Set program name
        GLib.set_prgname(ID)

    def do_startup(self):
        """
        Start up application
        """
        Gtk.Application.do_startup(self)

        # Restore any missing files and folders
        if not exists(CONF):
            mkdir(CONF)
        if not exists(DATA):
            mkdir(DATA)
        if not exists(join(DATA, "keys")):
            mkdir(join(DATA, "keys"))
        if not exists(join(CONF, "settings.json")):
            with open(join(CONF, "settings.json"), "w") as d:
                d.write(dumps(DEFAULT))
                d.close()
        if not exists(join(DATA, "otp.log")):
            open(join(DATA, "otp.log"), "w").close()
        
        # Validate config file
        validate_config("settings.json")

        # Set color scheme
        config = loads(open(join(CONF, "settings.json"), "r").read())
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
                join(APPDIR, "usr", "share", "icons")
            )

    def do_activate(self):
        """
        Activate application
        """
        win = Window(self)
        win.show()
