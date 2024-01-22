from os.path import join
from platform import system
from json import loads
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gio
from . import __conf__
from . import *
from .about import About
from .preferences import Preferences
from .file_log import FileLog
from .encrypt import Encrypt
from .decrypt import Decrypt


class Window(Gtk.ApplicationWindow):
    """
    Main window
    
    :param app: Application
    :type app: Gtk.Application
    """
    def __init__(self, app):
        """
        Constructor
        """
        super().__init__(
            application=app,
            resizable=True,
            title=APPNAME
        )

        # Add icon
        self.set_icon_name(ID)

        # Set up header
        header = Gtk.HeaderBar()

        # Build menu
        builder = Gtk.Builder.new_from_file(
            join(APPDIR, "gui", "menu.xml")
        )
        menu = builder.get_object("app-menu")
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu)

        # Add menu actions
        action = Gio.SimpleAction.new("prefs", None)
        action.connect("activate", self.on_prefs_clicked)
        app.add_action(action)
        action = Gio.SimpleAction.new("log", None)
        action.connect("activate", self.on_log_clicked)
        app.add_action(action)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about_clicked)
        app.add_action(action)

        # Set decoration layout
        if system() == "Darwin":
            header.set_decoration_layout("close,minimize,maximize:")
            header.pack_start(menu_button)
        else:
            header.set_decoration_layout(":minimize,maximize,close")
            header.pack_end(menu_button)

        # Add header
        self.set_titlebar(header)

        # Set up grid
        spacing = 20
        grid = Gtk.Grid(
            column_homogeneous=True,
            margin_start=spacing,
            margin_end=spacing,
            margin_top=spacing,
            margin_bottom=spacing,
            row_spacing=spacing,
            column_spacing=spacing
        )

        # Set up stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )
        self.encrypt = Encrypt(self)
        self.decrypt = Decrypt(self)
        self.stack.add_titled(self.encrypt, "encrypt", "Encrypt")
        self.stack.add_titled(self.decrypt, "decrypt", "Decrypt")

        # Set up stack switcher
        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.stack)

        # Attach widgets to grid
        widgets = [
            [switcher],
            [self.stack]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.set_child(grid)

    def on_prefs_clicked(self, action, param):
        """
        Open preferences window
        
        :param action: Action
        :type action: Gio.SimpleAction
        :param param: Parameter
        :type param: NoneType
        """
        prefs = Preferences(self)
        prefs.connect("destroy", self.reset)
        prefs.show()

    def on_log_clicked(self, action, param):
        """
        Open log window
        
        :param action: Action
        :type action: Gio.SimpleAction
        :param param: Parameter
        :type param: NoneType
        """
        win = FileLog(self)
        win.show()

    def on_about_clicked(self, action, param):
        """
        Open about dialog window
        
        :param action: Action
        :type action: Gio.SimpleAction
        :param param: Parameter
        :type param: NoneType
        """
        about = About(self)
        about.show()

    def reset(self, widget=None):
        """
        Reset options
        
        :param widget: Widget
        :type widget: Gtk.Widget
        """
        config = loads(open(join(__conf__, "settings.json"), "r").read())

        # Reset encrypt options
        self.encrypt.file.set_text("")
        self.encrypt.key.set_text("")
        self.encrypt.dir.set_text(config["save"])
        self.encrypt.del_toggle.set_active(False)
        self.encrypt.config = config

        # Reset decrypt options
        self.decrypt.file.set_text("")
        self.decrypt.key.set_text("")
        self.decrypt.dir.set_text(config["save"])
        self.decrypt.del_toggle.set_active(True)
        self.decrypt.config = config

    def quit(self):
        """
        Quit application
        """
        self.get_application().quit()
