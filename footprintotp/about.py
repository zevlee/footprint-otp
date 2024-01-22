from os.path import join
from platform import system
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk
from . import __appdir__, __appname__, __id__, __version__

class About(Gtk.AboutDialog):
    """
    About dialog window

    :param parent: Parent window
    :type parent: Gtk.Window
    """
    def __init__(self, parent):
        """
        Constructor
        """
        super().__init__(
            modal=True,
            transient_for=parent,
            program_name=__appname__,
            version=__version__,
            copyright="Copyright (c) 2021-2024 Zev Lee",
            license_type=Gtk.License.MIT_X11,
            website="https://github.com/zevlee/footprint-otp",
            website_label="Homepage"
        )

        # Set up header
        header = Gtk.HeaderBar()

        # Set decoration layout
        if system() == "Darwin":
            header.set_decoration_layout("close,minimize,maximize:")
        else:
            header.set_decoration_layout(":minimize,maximize,close")

        # Add header
        self.set_titlebar(header)

        # Set up logo
        filename = join(__appdir__, f"{__id__}.svg")
        logo = Gtk.Image.new_from_file(filename)

        # Add logo
        self.set_logo(logo.get_paintable())
