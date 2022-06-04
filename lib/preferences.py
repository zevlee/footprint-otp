#!/usr/bin/env python3

from lib.utils import Utils
from os.path import join, exists, expanduser
from platform import system
from json import loads, dumps
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk, Gio


class Preferences(Gtk.Window):

    def __init__(self, parent):
        super().__init__(
            modal=True,
            transient_for=parent,
            resizable=False,
            title="Preferences"
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

        # Set up grid
        spacing = 20
        grid = Gtk.Grid(
            row_homogeneous=True,
            column_homogeneous=True,
            margin_start=spacing,
            margin_end=spacing,
            margin_top=spacing,
            margin_bottom=spacing,
            row_spacing=spacing,
            column_spacing=spacing
        )

        # Open stored preferences
        self.config = loads(
            open(join(Utils.CONFIG_DIR, "otp.json"), "r").read()
        )

        # Default mode label and combo box
        mode_label = Gtk.Label(halign=Gtk.Align.START)
        mode_label.set_markup("<b>Default Mode</b>")
        self.mode = Gtk.ComboBoxText()
        self.mode.set_entry_text_column(0)
        modes = ["standard", "simple"]
        for mode in modes:
            self.mode.append_text(mode)
        self.mode.set_active(modes.index(self.config["mode"]))

        # Default directory label, button, and entry box
        dflt_label = Gtk.Label(halign=Gtk.Align.START)
        dflt_label.set_markup("<b>Default Directory</b>")
        dflt_button = Gtk.Button(label="Choose Directory")
        dflt_button.connect("clicked", self.on_dflt_clicked)
        self.dflt = Gtk.Entry()
        self.dflt.set_text(self.config["dflt"])

        # Keys location label, button, and entry box
        keys_label = Gtk.Label(halign=Gtk.Align.START)
        keys_label.set_markup("<b>Keys Location</b>")
        keys_button = Gtk.Button(label="Choose Directory")
        keys_button.connect("clicked", self.on_keys_clicked)
        self.keys = Gtk.Entry()
        self.keys.set_text(self.config["keys"])

        # Default save directory label, button, and entry box
        save_dir_label = Gtk.Label(halign=Gtk.Align.START)
        save_dir_label.set_markup("<b>Default Save Location</b>")
        save_dir_button = Gtk.Button(label="Choose Directory")
        save_dir_button.connect("clicked", self.on_enc_clicked)
        self.save = Gtk.Entry()
        self.save.set_text(self.config["save"])

        # Default save directory note
        note = Gtk.Label(halign=Gtk.Align.START)
        note.set_markup(Utils.lnbr(
            "<small>If the save location is left blank, files are saved to the"
            " same location as the selected file by default.</small>"
        ))

        # Advanced label
        advanced_label = Gtk.Label(halign=Gtk.Align.START)
        advanced_label.set_markup("<b>Advanced</b>")

        # Debug mode check box
        self.dbug = Gtk.CheckButton(label="Debug Mode")
        self.dbug.set_active(self.config["dbug"])

        # Default settings button
        default_button = Gtk.Button(label="Default Settings")
        default_button.connect("clicked", self.on_default_clicked)

        # Cancel and save buttons
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_clicked)

        # Attach widgets to grid
        widgets = [
            [dflt_label, dflt_button],
            [self.dflt],
            [keys_label, keys_button],
            [self.keys],
            [save_dir_label, save_dir_button],
            [self.save],
            [note],
            [advanced_label],
            [self.dbug],
            [default_button],
            [cancel_button, save_button]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.set_child(grid)

    def on_dflt_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the default directory",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(
            Gio.File.new_for_path(self.config["dflt"])
        )
        dialog.set_keep_above(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dflt = dialog.get_filename()
            self.dflt.set_text(dflt)
        dialog.destroy()

    def on_keys_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose where to save key files",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(
            Gio.File.new_for_path(self.config["keys"])
        )
        dialog.set_keep_above(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            key = dialog.get_filename()
            self.keys.set_text(key)
        dialog.destroy()

    def on_enc_clicked(self, widget):
        """
        Open a dialog for user to select directory
        """
        dialog = Gtk.FileChooserDialog(
            title="Choose the default location to save files",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(
            Gio.File.new_for_path(self.config["save"])
        )
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
        self.keys.set_text(join(Utils.DATA_DIR, "keys"))
        self.save.set_text("")
        self.dbug.set_active(False)

    def on_cancel_clicked(self, widget):
        """
        Close without saving
        """
        self.destroy()

    def _save_prefs(self):
        """
        Save preferences then close
        """
        if not exists(self.dflt.get_text()):
            raise FileNotFoundError
        if not exists(self.keys.get_text()):
            raise FileNotFoundError
        if not exists(self.save.get_text()) and self.save.get_text() != "":
            raise FileNotFoundError
        with open(join(Utils.CONFIG_DIR, "otp.json"), "w") as c:
            config = {
                "mode": self.mode.get_active_text(),
                "dflt": self.dflt.get_text(),
                "keys": self.keys.get_text(),
                "save": self.save.get_text(),
                "dbug": self.dbug.get_active()
            }
            c.write(dumps(config))
            c.close()
        self.destroy()

    def on_save_clicked(self, widget):
        """
        When clicked, call `_save_prefs`
        """
        config = loads(open(join(Utils.CONFIG_DIR, "otp.json"), "r").read())
        if not config["dbug"]:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK
            )
            dialog.set_titlebar(Gtk.HeaderBar(show_title_buttons=False))
            dialog.connect("response", self._confirm)
            try:
                self._save_prefs()
            except FileNotFoundError:
                dialog.set_markup("Directory not found")
                dialog.show()
        else:
            self._save_prefs()

    def _confirm(self, dialog, response):
        """
        Close upon confirming
        """
        dialog.destroy()
