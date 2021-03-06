#!/usr/bin/env python3

from lib.utils import Utils
from lib.otp import OneTimePad
from os.path import dirname, join, exists
from json import loads
from time import time, strftime, gmtime
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gio


class Decrypt(Gtk.Box):

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
        file_label.set_markup("<b>Choose the file to decrypt</b>")
        file_button = Gtk.Button(label="Choose File")
        file_button.connect("clicked", self.on_file_clicked)
        self.file = Gtk.Entry()

        # Key label, button, and entry box
        key_label = Gtk.Label(halign=Gtk.Align.START)
        key_label.set_markup("<b>Choose the key file</b>")
        key_button = Gtk.Button(label="Choose Key File")
        key_button.connect("clicked", self.on_key_clicked)
        self.key = Gtk.Entry()

        # Save location label, button, and entry box
        dir_label = Gtk.Label(halign=Gtk.Align.START)
        dir_label.set_markup("<b>Save Location</b>")
        dir_button = Gtk.Button(label="Choose Directory")
        dir_button.connect("clicked", self.on_dir_clicked)
        self.dir = Gtk.Entry(text=self.config["save"])

        # Delete files option
        self.del_toggle = Gtk.CheckButton(label="Delete files upon decryption")
        self.del_toggle.set_active(True)

        # Reset button
        reset_button = Gtk.Button(label="Reset")
        reset_button.connect("clicked", self.win.reset)

        # Decrypt button
        decrypt_button = Gtk.Button(
            label="Decrypt", hexpand=True, vexpand=True
        )
        decrypt_button.connect("clicked", self.on_decrypt_clicked)

        # Attach widgets to grid
        widgets = [
            [file_label, file_button],
            [self.file],
            [key_label, key_button],
            [self.key],
            [dir_label, dir_button],
            [self.dir],
            [self.del_toggle],
            [reset_button],
            [decrypt_button]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.append(grid)

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
        self.filter(dialog, "e")
        dialog.connect("response", self._select_file)
        dialog.show()

    def _select_file(self, dialog, response):
        """
        Set file when chosen in dialog
        """
        if response == Gtk.ResponseType.OK:
            filename = Gio.File.get_path(dialog.get_file())
            self.file.set_text(filename)
            # Attempt to find key file
            log = open(join(Utils.DATA_DIR, "otp.log"), "r").readlines()
            bn_log = [Utils.bn(line[:-1]) for line in log]
            try:
                key_ind = bn_log.index(Utils.bn(filename)) + 1
                if exists(join(self.config["keys"], bn_log[key_ind])):
                    self.key.set_text(
                        join(self.config["keys"], bn_log[key_ind])
                    )
                elif exists(log[key_ind][:-1]):
                    self.key.set_text(exists(log[key_ind][:-1]))
            except ValueError:
                pass
            # Set save location to same as chosen file
            if self.dir.get_text() == "":
                self.dir.set_text(dirname(filename))
        dialog.destroy()

    def on_key_clicked(self, widget):
        """
        Open a dialog for user to select key
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the key file",
            transient_for=self.win,
            modal=True,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(
            Gio.File.new_for_path(self.config["keys"])
        )
        self.filter(dialog, "k")
        dialog.connect("response", self._select_key)
        dialog.show()

    def _select_key(self, dialog, response):
        """
        Set key file when chosen in dialog
        """
        if response == Gtk.ResponseType.OK:
            self.key.set_text(Gio.File.get_path(dialog.get_file()))
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

    def _decrypt_file(self):
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
        d = OneTimePad.decrypt_file(
            file,
            key,
            dir,
            Utils.DATA_DIR,
            del_toggle
        )
        elapsed = time() - start
        elapsed = strftime("%H:%M:%S", gmtime(elapsed))
        d = Utils.lnbr(Utils.bn(d))
        dec_msg = f"<b>Decrypted</b>\n{d}"
        time_msg = f"<b>Time</b>\n{elapsed}"
        msg = f"{dec_msg}\n{time_msg}"
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
        dialog.set_markup("<big><b>Decryption successful</b></big>")
        label = Gtk.Label(label=msg, use_markup=True)
        dialog.get_message_area().append(label)
        dialog.set_titlebar(Gtk.HeaderBar(show_title_buttons=False))
        dialog.connect("response", self._confirm)
        dialog.show()

    def on_decrypt_clicked(self, widget):
        """
        Decrypt the user-selected file and save to the user-selected
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
                self._decrypt_file()
            except FileNotFoundError:
                dialog.set_markup("File not found")
                dialog.show()
            except Exception:
                dialog.set_markup("Invalid file combination")
                dialog.show()
        else:
            self._decrypt_file()

    def _confirm(self, dialog, response):
        """
        Close upon confirming
        """
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
            self.win.reset()
        elif response == Gtk.ResponseType.CLOSE:
            self.win.quit()
