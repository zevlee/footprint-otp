#!/usr/bin/env python3

from lib.otp import encrypt_file, decrypt_file
from os import mkdir, remove
from os.path import dirname, join, basename, normpath, exists, expanduser
from platform import system
from json import loads, dumps
from textwrap import TextWrapper
from time import time, strftime, gmtime
from binascii import Error as BinasciiError
from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib
from gi.repository.GdkPixbuf import Pixbuf


class Fn:

    # config and data directories
    if system() == "Darwin":
        conf_dir = expanduser(
            "~/Library/Application Support/me.zevlee.FootprintOTP"
        )
        data_dir = conf_dir
    else:
        conf_dir = join(GLib.get_user_config_dir(), "Footprint OTP")
        data_dir = join(GLib.get_user_data_dir(), "Footprint OTP")
    # application version
    version = open(join(dirname(__file__), "..", "VERSION")).read()

    @staticmethod
    def bn(name):
        """
        Normalize a file path then find the base name
        """
        return basename(normpath(name))

    @staticmethod
    def lnbr(text, char=70):
        """
        Given a string `text` and integer `char`, return a string with
        line breaks every `char` characters
        """
        t = TextWrapper(width=char, break_on_hyphens=False)
        return t.fill(text)


class Header(Gtk.HeaderBar):

    def __init__(self, title, subtitle, version, application, window):
        Gtk.HeaderBar.__init__(self)
        self.title = title
        self.version = version
        self.app = application
        self.win = window
        self.set_title(self.title)
        self.set_subtitle(subtitle)
        self.set_show_close_button(True)

        # create menu
        action = Gio.SimpleAction.new("log", None)
        action.connect("activate", self.on_log)
        self.app.add_action(action)

        action = Gio.SimpleAction.new("prefs", None)
        action.connect("activate", self.on_prefs)
        self.app.add_action(action)

        action = Gio.SimpleAction.new("switch", None)
        action.connect("activate", self.on_switch)
        self.app.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.app.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.app.on_quit)
        self.app.add_action(action)

        builder = Gtk.Builder.new_from_file(
            join(dirname(__file__), "..", "gui", "menu.xml")
        )
        menu = builder.get_object("app-menu")
        menu_button = Gtk.MenuButton.new()
        menu_button.set_image(
            Gtk.Image.new_from_icon_name(
                "emblem-system-symbolic",
                Gtk.IconSize.LARGE_TOOLBAR
            )
        )
        menu_button.set_menu_model(menu)
        # window decoration layout
        if system() == "Darwin":
            self.set_decoration_layout("close,minimize,maximize:")
            self.pack_start(menu_button)
        else:
            self.set_decoration_layout(":minimize,maximize,close")
            self.pack_end(menu_button)

    def on_log(self, action, param):
        """
        Open file log dialog
        """
        win = FileLog()
        win.present()

    def on_prefs(self, action, param):
        """
        Open preferences dialog
        """
        prefs = Preferences()
        prefs.connect("destroy", self.win.reset)
        prefs.present()

    def on_switch(self, action, param):
        """
        Change application mode
        """
        if self.win.mode == "standard":
            win = SimpleAppWindow(
                self.app,
                self.win.stack.get_visible_child_name()
            )
        else:
            win = AppWindow(
                self.app,
                self.win.stack.get_visible_child_name()
            )
        win.present()
        self.win.destroy()

    def on_about(self, action, param):
        """
        Open about dialog
        """
        about = Gtk.AboutDialog(modal=True)
        about.set_position(Gtk.WindowPosition.CENTER)
        file = join(dirname(__file__), "..", "footprint-otp.svg")
        logo = Pixbuf.new_from_file(file)
        about.set_logo(logo)
        about.set_program_name(self.title)
        about.set_version(self.version)
        about.set_copyright("Copyright © 2021 Zev Lee")
        license = open(join(dirname(__file__), "..", "LICENSE")).read()
        about.set_license(license)
        about.set_wrap_license(True)
        about.set_website("https://gitlab.com/zevlee")
        about.set_website_label("Homepage")
        about.present()


class Preferences(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_icon_from_file(
            join(dirname(__file__), "..", "footprint-otp.svg")
        )
        self.set_title("Preferences")
        self.set_border_width(40)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_keep_above(True)

        # open stored preferences
        self.config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        self.add(grid)
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)

        mode_label = Gtk.Label(halign=Gtk.Align.START)
        mode_label.set_markup("<b>Default Mode</b>")
        grid.attach(mode_label, 0, 0, 1, 1)

        self.mode = Gtk.ComboBoxText()
        self.mode.set_entry_text_column(0)
        modes = ["standard", "simple"]
        for mode in modes:
            self.mode.append_text(mode)
        self.mode.set_active(modes.index(self.config["mode"]))
        grid.attach(self.mode, 1, 0, 1, 1)

        def_label = Gtk.Label(halign=Gtk.Align.START)
        def_label.set_markup("<b>Default Directory</b>")
        grid.attach(def_label, 0, 1, 1, 1)

        def_button = Gtk.Button(label="Choose Directory")
        def_button.connect("clicked", self.on_dflt_clicked)
        grid.attach(def_button, 1, 1, 1, 1)

        self.dflt = Gtk.Entry()
        self.dflt.set_text(self.config["dflt"])
        grid.attach(self.dflt, 0, 2, 2, 1)

        key_label = Gtk.Label(halign=Gtk.Align.START)
        key_label.set_markup("<b>Keys Location</b>")
        grid.attach(key_label, 0, 3, 1, 1)

        key_button = Gtk.Button(label="Choose Directory")
        key_button.connect("clicked", self.on_key_clicked)
        grid.attach(key_button, 1, 3, 1, 1)

        self.key = Gtk.Entry()
        self.key.set_text(self.config["keys"])
        grid.attach(self.key, 0, 4, 2, 1)

        enc_label = Gtk.Label(halign=Gtk.Align.START)
        enc_label.set_markup("<b>Default Save Location</b>")
        grid.attach(enc_label, 0, 5, 1, 1)

        enc_button = Gtk.Button(label="Choose Directory")
        enc_button.connect("clicked", self.on_enc_clicked)
        grid.attach(enc_button, 1, 5, 1, 1)

        self.save = Gtk.Entry()
        self.save.set_text(self.config["save"])
        grid.attach(self.save, 0, 6, 2, 1)

        note = Gtk.Label(halign=Gtk.Align.START)
        note.set_markup(Fn.lnbr(
            "<small>If the save location is left blank, files are saved to the"
            + " same location as the selected file by default.</small>"
        ))
        grid.attach(note, 0, 7, 2, 1)

        adv_label = Gtk.Label(halign=Gtk.Align.START)
        adv_label.set_markup("<b>Advanced</b>")
        grid.attach(adv_label, 0, 8, 2, 1)

        self.dbug = Gtk.CheckButton(label="Debug Mode")
        self.dbug.set_active(self.config["dbug"])
        grid.attach(self.dbug, 0, 9, 2, 1)

        default_button = Gtk.Button(label="Default Settings")
        default_button.connect("clicked", self.on_default_clicked)
        grid.attach(default_button, 0, 10, 2, 1)

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        grid.attach(cancel_button, 0, 11, 1, 1)

        select_button = Gtk.Button(label="Save")
        select_button.connect("clicked", self.on_save_clicked)
        grid.attach(select_button, 1, 11, 1, 1)

        self.show_all()

    def on_dflt_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the default directory",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(self.config["dflt"])
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.set_keep_above(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dflt = dialog.get_filename()
            self.dflt.set_text(dflt)
        dialog.destroy()

    def on_key_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose where to save key files",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(self.config["keys"])
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.set_keep_above(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            key = dialog.get_filename()
            self.key.set_text(key)
        dialog.destroy()

    def on_enc_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the default location to save files",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(self.config["save"])
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.set_keep_above(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            enc = dialog.get_filename()
            self.save.set_text(enc)
        dialog.destroy()

    def on_default_clicked(self, widget):
        """
        Reset options to default
        """
        self.mode.set_active(0)
        self.dflt.set_text(expanduser("~"))
        self.key.set_text(join(Fn.data_dir, "keys"))
        self.save.set_text("")
        self.dbug.set_active(False)

    def on_cancel_clicked(self, widget):
        """
        Close without saving
        """
        self.destroy()

    def save_prefs(self):
        """
        Save preferences then close
        """
        if not exists(self.dflt.get_text()):
            raise FileNotFoundError
        if not exists(self.key.get_text()):
            raise FileNotFoundError
        if not exists(self.save.get_text()) and self.save.get_text() != "":
            raise FileNotFoundError
        with open(join(Fn.conf_dir, "otp.json"), "w") as cfg:
            config = {
                "mode": self.mode.get_active_text(),
                "dflt": self.dflt.get_text(),
                "keys": self.key.get_text(),
                "save": self.save.get_text(),
                "dbug": self.dbug.get_active()
            }
            cfg.write(dumps(config))
            cfg.close()
        self.destroy()

    def on_save_clicked(self, widget):
        """
        When clicked, call `save_prefs`
        """
        config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())
        if not config["dbug"]:
            try:
                self.save_prefs()
            except FileNotFoundError:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Directory not found"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
        else:
            self.save_prefs()


class FileLog(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_icon_from_file(
            join(dirname(__file__), "..", "footprint-otp.svg")
        )
        self.set_title("File Log")
        self.set_border_width(40)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_keep_above(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        self.add(grid)
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)

        # list to store log data
        self.store = Gtk.ListStore(str, str, str, str)
        log_file = join(Fn.data_dir, "otp.log")
        if not exists(log_file):
            open(log_file, "w").close()
            log = []
        else:
            log = open(log_file).readlines()
        for i in range(len(log) // 5):
            file = Fn.lnbr(Fn.bn(log[i * 5][:-1]), 32)
            enc = Fn.lnbr(Fn.bn(log[i * 5 + 1][:-1]), 32)
            key = Fn.lnbr(Fn.bn(log[i * 5 + 2][:-1]), 32)
            encd = Fn.lnbr(log[i * 5 + 3][:-1], 32)
            self.store.append([file, enc, key, encd])
        # tree to display stored log data
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.connect("cursor-changed", self.on_selection)
        cols = ["File", "Encrypted", "Key", "Time"]
        for i in range(len(cols)):
            col = Gtk.TreeViewColumn(
                cols[i], Gtk.CellRendererText(), text=i
            )
            self.tree.append_column(col)
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(width=-1, height=400)
        scroll.add(self.tree)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        grid.attach(scroll, 0, 0, 4, 1)

        del_button = Gtk.Button(label="Delete Entry")
        del_button.connect("clicked", self.on_delete_entry)
        grid.attach(del_button, 3, 1, 1, 1)

        self.name, self.file, self.key, self.time = None, None, None, None

        self.show_all()

    def on_selection(self, widget):
        selection = self.tree.get_selection()
        model, treeiter = selection.get_selected()
        self.name, self.file, self.key, self.time = [
            item.replace("\n", "") for item in self.store[treeiter][:]
        ]

    def on_delete_entry(self, widget):
        if self.file is not None:
            confirm = Gtk.MessageDialog(
                transient_for=None,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.NONE,
                text="Confirm Deletion"
            )
            confirm.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
            confirm.format_secondary_markup(
                f"Delete entry for <b>{self.name}</b>?"
            )
            del_key = Gtk.CheckButton(
                label="Delete the associated key file"
            )
            del_key.set_halign(Gtk.Align.CENTER)
            del_key.set_active(True)
            confirm.get_content_area().add(del_key)
            confirm.show_all()
            confirm.set_position(Gtk.WindowPosition.CENTER)
            response = confirm.run()
            if response == Gtk.ResponseType.OK:
                old_log = open(join(Fn.data_dir, "otp.log"), "r").readlines()
                bn_log = [Fn.bn(line[:-1]) for line in old_log]
                if del_key.get_active():
                    remove(old_log[bn_log.index(self.key)][:-1])
                ind = bn_log.index(self.file) - 1
                rmv = []
                for i in range(5):
                    rmv.append(ind + i)
                new_log = [j for i, j in enumerate(old_log) if i not in rmv]
                with open(join(Fn.data_dir, "otp.log"), "w") as logfile:
                    for line in new_log:
                        logfile.write(line)
                    logfile.close()
                confirm.destroy()
                self.destroy()
            else:
                confirm.destroy()


class Encrypt(Gtk.Box):

    def __init__(self, app, win):
        Gtk.Box.__init__(self)

        self.app = app
        self.win = win

        self.config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())

        grid = Gtk.Grid()
        self.add(grid)
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)

        inst_label = Gtk.Label(halign=Gtk.Align.START)
        inst_label.set_markup("<b>Choose the file to encrypt</b>")
        grid.attach(inst_label, 0, 0, 4, 1)

        self.chooser = Gtk.FileChooserWidget()
        self.chooser.set_current_folder(self.config["dflt"])
        self.chooser.set_hexpand(True)
        self.chooser.set_vexpand(True)
        self.search = Gtk.SearchEntry()
        self.search.connect("search-changed", self.on_search_changed)
        self.chooser.set_extra_widget(self.search)
        self.all_filter = Gtk.FileFilter()
        self.all_filter.set_name("All files")
        self.all_filter.add_pattern("*")
        self.chooser.add_filter(self.all_filter)
        self.filter = Gtk.FileFilter()
        self.filter.set_name("Query")
        self.filter.add_pattern("*")
        self.chooser.add_filter(self.filter)
        grid.attach(self.chooser, 0, 1, 4, 1)

        dir_label = Gtk.Label(halign=Gtk.Align.START)
        dir_label.set_markup("<b>Save Location</b>")
        dir_box = Gtk.Box()
        dir_box.set_size_request(width=-1, height=60)
        dir_box.add(dir_label)
        grid.attach(dir_box, 0, 2, 1, 1)

        self.dir_button = Gtk.FileChooserButton(
            title="Choose the save location",
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        if self.config["save"] != "":
            self.dir_button.set_current_folder(self.config["save"])
        grid.attach(self.dir_button, 1, 2, 1, 1)

        self.enc_toggle = Gtk.CheckButton(label="Encrypt file names")
        self.enc_toggle.set_active(True)
        grid.attach(self.enc_toggle, 2, 2, 1, 1)

        self.del_toggle = Gtk.CheckButton(label="Delete file upon encryption")
        self.del_toggle.set_active(False)
        del_box = Gtk.Box()
        del_box.set_size_request(width=-1, height=60)
        del_box.add(self.del_toggle)
        grid.attach(del_box, 2, 3, 1, 1)

        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.win.reset)
        grid.attach(reset_button, 3, 2, 1, 1)

        encrypt_button = Gtk.Button(label="Encrypt")
        encrypt_button.connect("clicked", self.on_encrypt_clicked)
        grid.attach(encrypt_button, 3, 3, 1, 1)

        self.show_all()

    def on_search_changed(self, widget):
        query = self.search.get_text()
        if query != "":
            self.chooser.remove_filter(self.filter)
            self.chooser.remove_filter(self.all_filter)
            self.filter = Gtk.FileFilter()
            self.filter.set_name("Query")
            self.filter.add_pattern(f"*{query}*")
            self.chooser.add_filter(self.filter)
            self.chooser.add_filter(self.all_filter)
        else:
            self.chooser.remove_filter(self.filter)
            self.chooser.remove_filter(self.all_filter)
            self.chooser.add_filter(self.all_filter)
            self.chooser.add_filter(self.filter)

    def encrypt(self):
        file = self.chooser.get_filename()
        if self.dir_button.get_filename() is not None:
            dir = self.dir_button.get_filename()
        elif self.config["save"] != "":
            dir = self.config["save"]
        else:
            dir = dirname(file)
        enc_toggle = self.enc_toggle.get_active()
        del_toggle = self.del_toggle.get_active()
        start = time()
        e, k = encrypt_file(
            file,
            dir,
            self.config["keys"],
            Fn.data_dir,
            enc_toggle,
            del_toggle
        )
        elapsed = time() - start
        elapsed = strftime("%H:%M:%S", gmtime(elapsed))
        e = Fn.lnbr(Fn.bn(e))
        k = Fn.lnbr(Fn.bn(k))
        enc_msg = f"<b>Encrypted</b>\n{e}"
        key_msg = f"<b>Key</b>\n{k}"
        time_msg = f"<b>Time</b>\n{elapsed}"
        msg = f"{enc_msg}\n{key_msg}\n{time_msg}"
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="Encryption successful"
        )
        dialog.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
            Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE,
        )
        dialog.format_secondary_markup(msg)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.CLOSE:
            self.app.on_quit(None, None)
        dialog.destroy()

    def on_encrypt_clicked(self, widget):
        """
        Encrypt the user-selected file and save to the user-selected
        directory
        """
        config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())
        if not config["dbug"]:
            try:
                self.encrypt()
            except FileNotFoundError:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="File not found"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
            except TypeError:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="File not selected"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
            except IsADirectoryError:
                msg = f"{Fn.bn(self.chooser.get_filename())} is a directory"
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=msg
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
            except Exception:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Unknown error"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
        else:
            self.encrypt()


class Decrypt(Gtk.Box):

    def __init__(self, app, win):
        Gtk.Box.__init__(self)

        self.app = app
        self.win = win

        self.config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())

        grid = Gtk.Grid()
        self.add(grid)
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)

        inst_label = Gtk.Label(halign=Gtk.Align.START)
        inst_label.set_markup("<b>Choose the file to decrypt</b>")
        grid.attach(inst_label, 0, 0, 2, 1)

        self.chooser = Gtk.FileChooserWidget()
        self.chooser.set_current_folder(self.config["dflt"])
        self.chooser.set_hexpand(True)
        self.chooser.set_vexpand(True)
        self.chooser.connect("selection-changed", self.on_selection)
        self.search = Gtk.SearchEntry()
        self.search.connect("search-changed", self.on_search_changed)
        self.chooser.set_extra_widget(self.search)
        self.all_filter = Gtk.FileFilter()
        self.all_filter.set_name("OTP encrypted files (.otp)")
        self.all_filter.add_pattern("*.otp")
        self.chooser.add_filter(self.all_filter)
        self.filter = Gtk.FileFilter()
        self.filter.set_name("Query")
        self.filter.add_pattern("*")
        self.chooser.add_filter(self.filter)
        grid.attach(self.chooser, 0, 1, 4, 1)

        dir_label = Gtk.Label(halign=Gtk.Align.START)
        dir_label.set_markup("<b>Save Location</b>")
        dir_box = Gtk.Box()
        dir_box.set_size_request(width=-1, height=60)
        dir_box.add(dir_label)
        grid.attach(dir_box, 0, 2, 1, 1)

        self.dir_button = Gtk.FileChooserButton(
            title="Choose the save location",
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        if self.config["save"] != "":
            self.dir_button.set_current_folder(self.config["save"])
        grid.attach(self.dir_button, 1, 2, 1, 1)

        self.del_toggle = Gtk.CheckButton(
            label="Delete files upon decryption"
        )
        self.del_toggle.set_active(True)
        grid.attach(self.del_toggle, 2, 2, 1, 1)

        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.win.reset)
        grid.attach(reset_button, 3, 2, 1, 1)

        self.selected = Gtk.Label(halign=Gtk.Align.START)
        self.selected.set_markup("<b>File:</b>\n<b>Key:</b>")
        selected = Gtk.ScrolledWindow()
        selected.set_size_request(width=-1, height=60)
        selected.add(self.selected)
        grid.attach(selected, 0, 3, 3, 1)

        decrypt_button = Gtk.Button(label="Decrypt")
        decrypt_button.connect("clicked", self.on_decrypt_clicked)
        decrypt_button.connect("clicked", self.on_selection)
        grid.attach(decrypt_button, 3, 3, 1, 1)

        self.show_all()

    def on_selection(self, widget):
        try:
            self.file = self.chooser.get_filename()
            log = open(join(Fn.data_dir, "otp.log"), "r").readlines()
            bn_log = [Fn.bn(line[:-1]) for line in log]
            name_ind = bn_log.index(Fn.bn(self.file)) - 1
            name = log[name_ind][:-1]
            key_ind = bn_log.index(Fn.bn(self.file)) + 1
            self.key = log[key_ind][:-1]
            self.selected.set_markup(
                f"<b>File:</b> {Fn.bn(name)}\n<b>Key:</b>  {Fn.bn(self.key)}"
            )
        except (ValueError, TypeError):
            self.selected.set_markup("<b>File:</b>\n<b>Key:</b>")

    def on_search_changed(self, widget):
        query = self.search.get_text()
        if query != "":
            self.chooser.remove_filter(self.filter)
            self.chooser.remove_filter(self.all_filter)
            self.filter = Gtk.FileFilter()
            self.filter.set_name("Query")
            self.filter.add_pattern(f"*{query}*")
            self.chooser.add_filter(self.filter)
            self.chooser.add_filter(self.all_filter)
        else:
            self.chooser.remove_filter(self.filter)
            self.chooser.remove_filter(self.all_filter)
            self.chooser.add_filter(self.all_filter)
            self.chooser.add_filter(self.filter)

    def decrypt(self):
        file = self.file
        key = self.key

        # get directory
        if self.dir_button.get_filename() is not None:
            dir = self.dir_button.get_filename()
        elif self.config["save"] != "":
            dir = self.config["save"]
        else:
            dir = dirname(file)

        # check for key
        keys_dir = self.config["keys"]
        if exists(key):
            pass
        elif exists(join(dir, Fn.bn(key))):
            key = join(dir, Fn.bn(key))
        elif exists(join(keys_dir, Fn.bn(key))):
            key = join(keys_dir, Fn.bn(key))
        else:
            raise BinasciiError

        # get delete option status
        del_toggle = self.del_toggle.get_active()

        # decrypt
        start = time()
        d = decrypt_file(
            file,
            key,
            dir,
            Fn.data_dir,
            del_toggle
        )
        elapsed = time() - start
        elapsed = strftime("%H:%M:%S", gmtime(elapsed))
        d = Fn.lnbr(Fn.bn(d))
        dec_msg = f"<b>Decrypted</b>\n{d}"
        time_msg = f"<b>Time</b>\n{elapsed}"
        msg = f"{dec_msg}\n{time_msg}"
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="Decryption successful"
        )
        dialog.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
            Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE,
        )
        dialog.format_secondary_markup(msg)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.CLOSE:
            self.app.on_quit(None, None)
        dialog.destroy()
        self.file = None
        self.key = None

    def on_decrypt_clicked(self, widget):
        """
        Decrypt the user-selected file and save to the user-selected
        directory
        """
        config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())
        if not config["dbug"]:
            try:
                self.decrypt()
            except FileNotFoundError:
                error_text = "File not found"
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=error_text
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
            except (AttributeError, TypeError, BinasciiError):
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="File not found in log"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
            except Exception:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Unknown error"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
        else:
            self.decrypt()


class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, app, enc_dec="encrypt"):
        Gtk.Window.__init__(self, application=app)
        self.set_icon_from_file(
            join(dirname(__file__), "..", "footprint-otp.svg")
        )
        self.set_border_width(40)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.set_titlebar(
            Header(
                title="Footprint OTP",
                subtitle="One-Time Pad Encryption",
                version="Version " + Fn.version,
                application=app,
                window=self
            )
        )
        self.mode = "standard"
        self.enc_dec = enc_dec

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.add(vbox)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )

        self.encrypt = Encrypt(app, self)
        self.stack.add_titled(self.encrypt, "encrypt", "Encrypt")

        self.decrypt = Decrypt(app, self)
        self.stack.add_titled(self.decrypt, "decrypt", "Decrypt")

        self.stack.connect("notify::visible-child", self.dir_sync)

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.stack)

        vbox.pack_start(switcher, False, False, 0)
        vbox.pack_start(self.stack, True, True, 0)

        self.stack.set_visible_child_name(enc_dec)

        self.show_all()

    def reset(self, widget):
        """
        Reset options
        """
        config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())
        # reset encrypt options
        enc = self.encrypt
        enc.enc_toggle.set_active(True)
        enc.del_toggle.set_active(False)
        enc.dir_button.unselect_all()
        enc.chooser.unselect_all()
        enc.chooser.set_current_folder(config["dflt"])
        enc.search.set_text("")
        enc.config = config
        # reset decrypt options
        dec = self.decrypt
        dec.del_toggle.set_active(True)
        dec.dir_button.unselect_all()
        dec.chooser.unselect_all()
        dec.chooser.set_current_folder(config["dflt"])
        dec.search.set_text("")
        dec.selected.set_markup("<b>File:</b>\n<b>Key:</b>")
        dec.config = config

    def dir_sync(self, action, param):
        """
        Ensure that directory stays the same when switching between encrypt and
        decrypt modes
        """
        enc = self.encrypt
        dec = self.decrypt
        try:
            if self.stack.get_visible_child_name() == "encrypt":
                enc.chooser.set_current_folder(
                    dec.chooser.get_current_folder()
                )
            elif self.stack.get_visible_child_name() == "decrypt":
                dec.chooser.set_current_folder(
                    enc.chooser.get_current_folder()
                )
        except TypeError:
            pass


class SimpleEncrypt(Gtk.Box):

    def __init__(self, app, win):
        Gtk.Box.__init__(self)

        self.app = app
        self.win = win

        self.config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())

        grid = Gtk.Grid()
        self.add(grid)
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)

        file_label = Gtk.Label(halign=Gtk.Align.START)
        file_label.set_markup("<b>Choose the file to encrypt</b>")
        grid.attach(file_label, 0, 0, 1, 1)

        file_button = Gtk.Button(label="Choose File")
        file_button.connect("clicked", self.on_file_clicked)
        grid.attach(file_button, 1, 0, 1, 1)

        self.file = Gtk.Entry()
        grid.attach(self.file, 0, 1, 2, 1)

        dir_label = Gtk.Label(halign=Gtk.Align.START)
        dir_label.set_markup("<b>Save Location</b>")
        grid.attach(dir_label, 0, 2, 1, 1)

        dir_button = Gtk.Button(label="Choose Directory")
        dir_button.connect("clicked", self.on_dir_clicked)
        grid.attach(dir_button, 1, 2, 1, 1)

        self.dir = Gtk.Entry()
        grid.attach(self.dir, 0, 3, 2, 1)

        self.enc_toggle = Gtk.CheckButton(label="Encrypt file names")
        self.enc_toggle.set_active(True)
        grid.attach(self.enc_toggle, 0, 4, 2, 1)

        self.del_toggle = Gtk.CheckButton(
            label="Delete file upon encryption"
        )
        self.del_toggle.set_active(False)
        grid.attach(self.del_toggle, 0, 5, 2, 1)

        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.win.reset)
        grid.attach(reset_button, 0, 6, 2, 3)

        encrypt_button = Gtk.Button(label="Encrypt")
        encrypt_button.connect("clicked", self.on_encrypt_clicked)
        encrypt_button.set_hexpand(True)
        encrypt_button.set_vexpand(True)
        grid.attach(encrypt_button, 0, 9, 2, 6)

        self.show_all()

    def on_file_clicked(self, widget):
        """
        Open a dialog for user to select file
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the file to encrypt",
            parent=None,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(self.config["dflt"])
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file = dialog.get_filename()
            self.file.set_text(file)
        dialog.destroy()

    def on_dir_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the save location",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        if exists(self.file.get_text()):
            dialog.set_current_folder(dirname(self.file.get_text()))
        elif self.config["save"] != "":
            dialog.set_current_folder(self.config["save"])
        else:
            dialog.set_current_folder(self.config["dflt"])
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dir = dialog.get_filename()
            self.dir.set_text(dir)
        dialog.destroy()

    def encrypt(self):
        file = self.file.get_text()
        if self.dir.get_text() != "":
            dir = self.dir.get_text()
        elif self.config["save"] != "":
            dir = self.config["save"]
        else:
            dir = dirname(file)
        enc_toggle = self.enc_toggle.get_active()
        del_toggle = self.del_toggle.get_active()
        start = time()
        e, k = encrypt_file(
            file,
            dir,
            self.config["keys"],
            Fn.data_dir,
            enc_toggle,
            del_toggle
        )
        elapsed = time() - start
        elapsed = strftime("%H:%M:%S", gmtime(elapsed))
        e = Fn.lnbr(Fn.bn(e))
        k = Fn.lnbr(Fn.bn(k))
        enc_msg = f"<b>Encrypted</b>\n{e}"
        key_msg = f"<b>Key</b>\n{k}"
        time_msg = f"<b>Time</b>\n{elapsed}"
        msg = f"{enc_msg}\n{key_msg}\n{time_msg}"
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="Encryption successful"
        )
        dialog.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
            Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE,
        )
        dialog.format_secondary_markup(msg)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.CLOSE:
            self.app.on_quit(None, None)
        dialog.destroy()

    def on_encrypt_clicked(self, widget):
        """
        Encrypt the user-selected file and save to the user-selected
        directory
        """
        config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())
        if not config["dbug"]:
            try:
                self.encrypt()
            except FileNotFoundError:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="File not found"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
            except Exception:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Unknown error"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
        else:
            self.encrypt()


class SimpleDecrypt(Gtk.Box):

    def __init__(self, app, win):
        Gtk.Box.__init__(self)

        self.app = app
        self.win = win

        self.config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())

        grid = Gtk.Grid()
        self.add(grid)
        grid.set_row_spacing(20)
        grid.set_column_spacing(20)

        file_label = Gtk.Label(halign=Gtk.Align.START)
        file_label.set_markup("<b>Choose the file to decrypt</b>")
        grid.attach(file_label, 0, 0, 1, 1)

        file_button = Gtk.Button(label="Choose File")
        file_button.connect("clicked", self.on_file_clicked)
        grid.attach(file_button, 1, 0, 1, 1)

        self.file = Gtk.Entry()
        grid.attach(self.file, 0, 1, 2, 1)

        key_label = Gtk.Label(halign=Gtk.Align.START)
        key_label.set_markup("<b>Choose the key file</b>")
        grid.attach(key_label, 0, 2, 1, 1)

        key_button = Gtk.Button(label="Choose Key File")
        key_button.connect("clicked", self.on_key_clicked)
        grid.attach(key_button, 1, 2, 1, 1)

        self.key = Gtk.Entry()
        grid.attach(self.key, 0, 3, 2, 1)

        dir_label = Gtk.Label(halign=Gtk.Align.START)
        dir_label.set_markup("<b>Save Location</b>")
        grid.attach(dir_label, 0, 4, 1, 1)

        dir_button = Gtk.Button(label="Choose Directory")
        dir_button.connect("clicked", self.on_dir_clicked)
        grid.attach(dir_button, 1, 4, 1, 1)

        self.dir = Gtk.Entry()
        grid.attach(self.dir, 0, 5, 2, 1)

        self.del_toggle = Gtk.CheckButton(
            label="Delete files upon decryption"
        )
        self.del_toggle.set_active(True)
        grid.attach(self.del_toggle, 0, 6, 2, 1)

        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.win.reset)
        grid.attach(reset_button, 0, 7, 2, 3)

        decrypt_button = Gtk.Button(label="Decrypt")
        decrypt_button.connect("clicked", self.on_decrypt_clicked)
        decrypt_button.set_hexpand(True)
        decrypt_button.set_vexpand(True)
        grid.attach(decrypt_button, 0, 10, 2, 6)

        self.show_all()

    def filter(self, dialog, type):
        """
        Filter for the file selection dialog
        """
        if type == "e":
            filter_enc = Gtk.FileFilter()
            filter_enc.set_name("OTP encrypted files (.otp)")
            filter_enc.add_pattern("*.otp")
            dialog.add_filter(filter_enc)
        elif type == "k":
            filter_key = Gtk.FileFilter()
            filter_key.set_name("OTP keys (.key)")
            filter_key.add_pattern("*.key")
            dialog.add_filter(filter_key)
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)

    def on_file_clicked(self, widget):
        """
        Open a dialog for user to select file
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the file to decrypt",
            parent=None,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(self.config["dflt"])
        dialog.set_position(Gtk.WindowPosition.CENTER)
        self.filter(dialog, "e")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file = dialog.get_filename()
            self.file.set_text(file)
            # Attempt to find key file
            log = open(join(Fn.data_dir, "otp.log"), "r").readlines()
            bn_log = [Fn.bn(line[:-1]) for line in log]
            key_ind = bn_log.index(Fn.bn(file)) + 1
            if exists(join(self.config["keys"], bn_log[key_ind])):
                self.key.set_text(join(self.config["keys"], bn_log[key_ind]))
            elif exists(log[key_ind][:-1]):
                self.key.set_text(exists(log[key_ind][:-1]))
        dialog.destroy()

    def on_key_clicked(self, widget):
        """
        Open a dialog for user to select key
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the key file",
            parent=None,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(self.config["keys"])
        self.filter(dialog, "k")
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            key = dialog.get_filename()
            self.key.set_text(key)
        dialog.destroy()

    def on_dir_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the save location",
            parent=None,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        if exists(self.file.get_text()):
            dialog.set_current_folder(dirname(self.file.get_text()))
        elif self.config["save"] != "":
            dialog.set_current_folder(self.config["save"])
        else:
            dialog.set_current_folder(self.config["dflt"])
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dir = dialog.get_filename()
            self.dir.set_text(dir)
        dialog.destroy()

    def decrypt(self):
        file = self.file.get_text()
        key = self.key.get_text()
        if self.dir.get_text() != "":
            dir = self.dir.get_text()
        elif self.config["save"] != "":
            dir = self.config["save"]
        else:
            dir = dirname(file)
        del_toggle = self.del_toggle.get_active()
        start = time()
        d = decrypt_file(
            file,
            key,
            dir,
            Fn.data_dir,
            del_toggle
        )
        elapsed = time() - start
        elapsed = strftime("%H:%M:%S", gmtime(elapsed))
        d = Fn.lnbr(Fn.bn(d))
        dec_msg = f"<b>Decrypted</b>\n{d}"
        time_msg = f"<b>Time</b>\n{elapsed}"
        msg = f"{dec_msg}\n{time_msg}"
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="Decryption successful"
        )
        dialog.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
            Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE,
        )
        dialog.format_secondary_markup(msg)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.CLOSE:
            self.app.on_quit(None, None)
        dialog.destroy()

    def on_decrypt_clicked(self, widget):
        """
        Decrypt the user-selected file and save to the user-selected
        directory
        """
        config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())
        if not config["dbug"]:
            try:
                self.decrypt()
            except FileNotFoundError:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="File not found"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
            except Exception:
                dialog = Gtk.MessageDialog(
                    transient_for=None,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Invalid file combination"
                )
                dialog.set_position(Gtk.WindowPosition.CENTER)
                dialog.run()
                dialog.destroy()
        else:
            self.decrypt()


class SimpleAppWindow(Gtk.ApplicationWindow):

    def __init__(self, app, enc_dec="encrypt"):
        Gtk.Window.__init__(self, application=app)
        self.set_icon_from_file(
            join(dirname(__file__), "..", "footprint-otp.svg")
        )
        self.set_border_width(40)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.set_titlebar(
            Header(
                title="Footprint OTP",
                subtitle="One-Time Pad Encryption",
                version="Version " + Fn.version,
                application=app,
                window=self
            )
        )
        self.mode = "simple"
        self.enc_dec = enc_dec

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.add(vbox)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )

        self.encrypt = SimpleEncrypt(app, self)
        self.stack.add_titled(self.encrypt, "encrypt", "Encrypt")

        self.decrypt = SimpleDecrypt(app, self)
        self.stack.add_titled(self.decrypt, "decrypt", "Decrypt")

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.stack)

        vbox.pack_start(switcher, False, False, 0)
        vbox.pack_start(self.stack, True, True, 0)

        self.stack.set_visible_child_name(enc_dec)

        self.show_all()

    def reset(self, action):
        config = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())
        # reset encrypt options
        enc = self.encrypt
        enc.file.set_text("")
        enc.dir.set_text("")
        enc.enc_toggle.set_active(True)
        enc.del_toggle.set_active(False)
        enc.config = config
        # reset decrypt options
        dec = self.decrypt
        dec.file.set_text("")
        dec.key.set_text("")
        dec.dir.set_text("")
        dec.del_toggle.set_active(True)
        dec.config = config


class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id="me.zevlee.FootprintOTP",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        GLib.set_application_name("Footprint OTP")

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # ensure necessary folders exist
        if not exists(Fn.conf_dir):
            mkdir(Fn.conf_dir)
        if not exists(Fn.data_dir):
            mkdir(Fn.data_dir)
        if not exists(join(Fn.data_dir, "keys")):
            mkdir(join(Fn.data_dir, "keys"))
        if not exists(join(Fn.conf_dir, "otp.json")):
            with open(join(Fn.conf_dir, "otp.json"), "w") as default:
                dflt = {
                    "mode": "standard",
                    "dflt": expanduser("~"),
                    "keys": join(Fn.data_dir, "keys"),
                    "save": "",
                    "dbug": False
                }
                default.write(dumps(dflt))
                default.close()
        if not exists(join(Fn.data_dir, "otp.log")):
            open(join(Fn.data_dir, "otp.log"), "w").close()

    def do_activate(self):
        mode = loads(open(join(Fn.conf_dir, "otp.json"), "r").read())["mode"]
        if mode == "standard":
            win = AppWindow(self)
        else:
            win = SimpleAppWindow(self)
        win.present()

    def on_quit(self, action, param):
        self.quit()
