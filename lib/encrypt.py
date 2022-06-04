#!/usr/bin/env python3

from lib.utils import Utils
from lib.otp import OneTimePad
from os.path import dirname, join, exists
from json import loads
from time import time, strftime, gmtime
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gio


class Encrypt(Gtk.Box):

    def __init__(self, window):
        super().__init__()

        self.win = window

        # Open stored preferences
        self.config = loads(
            open(join(Utils.CONFIG_DIR, "otp.json"), "r").read()
        )

        # Set up grid
        spacing = 20
        grid = Gtk.Grid(
            row_homogeneous=True,
            row_spacing=spacing,
            column_spacing=spacing
        )

        # File label, button, and entry box
        file_label = Gtk.Label(halign=Gtk.Align.START)
        file_label.set_markup("<b>Choose the file to encrypt</b>")
        file_button = Gtk.Button(label="Choose File")
        file_button.connect("clicked", self.on_file_clicked)
        self.file = Gtk.Entry()

        # Save location label, button, and entry box
        dir_label = Gtk.Label(halign=Gtk.Align.START)
        dir_label.set_markup("<b>Save Location</b>")
        dir_button = Gtk.Button(label="Choose Directory")
        dir_button.connect("clicked", self.on_dir_clicked)
        self.dir = Gtk.Entry(text=self.config["save"])

        # Encrypt file names option
        self.enc_toggle = Gtk.CheckButton(label="Encrypt file names")
        self.enc_toggle.set_active(True)

        # Delete file upon encryption option
        self.del_toggle = Gtk.CheckButton(label="Delete file upon encryption")
        self.del_toggle.set_active(False)

        # Reset button
        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.win.reset)

        # Encrypt button
        encrypt_button = Gtk.Button(
            label="Encrypt", hexpand=True, vexpand=True
        )
        encrypt_button.connect("clicked", self.on_encrypt_clicked)

        # Attach widgets to grid
        widgets = [
            [file_label, file_button],
            [self.file],
            [dir_label, dir_button],
            [self.dir],
            [self.enc_toggle],
            [self.del_toggle],
            [Gtk.Box()],
            [reset_button],
            [encrypt_button]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.append(grid)

    def on_file_clicked(self, widget):
        """
        Open a dialog for user to select file
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the file to encrypt",
            transient_for=self.win,
            modal=True,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(
            Gio.File.new_for_path(self.config["dflt"])
        )
        dialog.connect("response", self._select_file)
        dialog.show()

    def _select_file(self, dialog, response):
        """
        Set file when chosen in dialog
        """
        if response == Gtk.ResponseType.OK:
            filename = Gio.File.get_path(dialog.get_file())
            self.file.set_text(filename)
            if self.dir.get_text() == "":
                self.dir.set_text(dirname(filename))
        dialog.destroy()

    def on_dir_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the save location",
            transient_for=self.win,
            modal=True,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK,
        )
        if exists(self.file.get_text()):
            dialog.set_current_folder(
                Gio.File.new_for_path(dirname(self.file.get_text()))
            )
        elif self.config["save"] != "":
            dialog.set_current_folder(
                Gio.File.new_for_path(self.config["save"])
            )
        else:
            dialog.set_current_folder(
                Gio.File.new_for_path(self.config["dflt"])
            )
        dialog.connect("response", self._select_dir)
        dialog.show()

    def _select_dir(self, dialog, response):
        """
        Set file when chosen in dialog
        """
        if response == Gtk.ResponseType.OK:
            self.dir.set_text(Gio.File.get_path(dialog.get_file()))
        dialog.destroy()

    def _encrypt_file(self):
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
        e, k = OneTimePad.encrypt_file(
            file,
            dir,
            self.config["keys"],
            Utils.DATA_DIR,
            enc_toggle,
            del_toggle
        )
        elapsed = time() - start
        elapsed = strftime("%H:%M:%S", gmtime(elapsed))
        e = Utils.lnbr(Utils.bn(e))
        k = Utils.lnbr(Utils.bn(k))
        enc_msg = f"<b>Encrypted</b>\n{e}"
        key_msg = f"<b>Key</b>\n{k}"
        time_msg = f"<b>Time</b>\n{elapsed}"
        msg = f"{enc_msg}\n{key_msg}\n{time_msg}"
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE
        )
        dialog.add_buttons(
            "_OK", Gtk.ResponseType.OK,
            "_Quit", Gtk.ResponseType.CLOSE,
        )
        dialog.set_markup("<big><b>Encryption successful</b></big>")
        label = Gtk.Label(label=msg, use_markup=True)
        dialog.get_message_area().append(label)
        dialog.set_titlebar(Gtk.HeaderBar(show_title_buttons=False))
        dialog.connect("response", self._confirm)
        dialog.show()

    def on_encrypt_clicked(self, widget):
        """
        Encrypt the user-selected file and save to the user-selected
        directory
        """
        config = loads(open(join(Utils.CONFIG_DIR, "otp.json"), "r").read())
        if not config["dbug"]:
            dialog = Gtk.MessageDialog(
                transient_for=self.win,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK
            )
            dialog.set_titlebar(Gtk.HeaderBar(show_title_buttons=False))
            dialog.connect("response", self._confirm)
            try:
                self._encrypt_file()
            except FileNotFoundError:
                dialog.set_markup("File not found")
                dialog.show()
            except Exception:
                dialog.set_markup("Unknown error")
                dialog.show()
        else:
            self._encrypt_file()

    def _confirm(self, dialog, response):
        """
        Close upon confirming
        """
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
            self.win.reset()
        elif response == Gtk.ResponseType.CLOSE:
            self.win.quit()
