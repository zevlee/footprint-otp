#!/usr/bin/env python3

from lib.utils import Utils
from os import remove
from os.path import dirname, join, exists
from platform import system
from gi import require_versions
require_versions({"Gtk": "4.0", "Adw": "1"})
from gi.repository import Gtk


class FileLog(Gtk.Window):

    def __init__(self, parent):
        super().__init__(
            modal=True,
            transient_for=parent,
            resizable=False,
            title="File Log"
        )

        self.parent = parent

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
            column_homogeneous=True,
            margin_start=spacing,
            margin_end=spacing,
            margin_top=spacing,
            margin_bottom=spacing,
            row_spacing=spacing,
            column_spacing=spacing
        )

        # Scrolled window of files
        self.store = Gtk.ListStore(str, str, str, str)
        log_file = join(Utils.DATA_DIR, "otp.log")
        if not exists(log_file):
            open(log_file, "w").close()
            log = []
        else:
            log = open(log_file).readlines()
        for i in range(len(log) // 5):
            file = Utils.lnbr(Utils.bn(log[i * 5][:-1]), 32)
            enc = Utils.lnbr(Utils.bn(log[i * 5 + 1][:-1]), 32)
            key = Utils.lnbr(Utils.bn(log[i * 5 + 2][:-1]), 32)
            encd = Utils.lnbr(log[i * 5 + 3][:-1], 32)
            self.store.append([file, enc, key, encd])
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.connect("cursor-changed", self.on_selection)
        cols = ["File", "Encrypted", "Key", "Time"]
        for i in range(len(cols)):
            col = Gtk.TreeViewColumn(
                cols[i], Gtk.CellRendererText(), text=i
            )
            self.tree.append_column(col)
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(width=800, height=400)
        scroll.set_child(self.tree)

        # Delete button
        delete_button = Gtk.Button(label="Delete Entry")
        delete_button.connect("clicked", self.on_delete_clicked)

        # Select button
        select_button = Gtk.Button(label="Select")
        select_button.connect("clicked", self.on_select_clicked)

        self.name, self.file, self.key, self.time = None, None, None, None

        # Attach widgets to grid
        widgets = [
            [scroll],
            [delete_button, select_button]
        ]
        for i in range(len(widgets)):
            width = max(len(row) for row in widgets) // len(widgets[i])
            for j in range(len(widgets[i])):
                grid.attach(widgets[i][j], j * width, i, width, 1)

        # Add grid
        self.set_child(grid)

    def on_selection(self, widget):
        selection = self.tree.get_selection()
        model, treeiter = selection.get_selected()
        self.name, self.file, self.key, self.time = [
            item.replace("\n", "") for item in self.store[treeiter][:]
        ]

    def on_delete_clicked(self, widget):
        """
        Open dialog to confirm deletion of entry and key file
        """
        if self.file is not None:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.NONE
            )
            dialog.add_buttons(
                "_Cancel", Gtk.ResponseType.CANCEL,
                "_OK", Gtk.ResponseType.OK
            )
            dialog.set_markup("<big><b>Confirm deletion</b></big>")
            msg = f"Delete entry for <b>{self.name}</b>?"
            spacing = 20
            label = Gtk.Label(
                label=msg,
                use_markup=True,
                margin_start=spacing,
                margin_end=spacing
            )
            dialog.get_content_area().add(label)
            dialog.del_key = Gtk.CheckButton(
                label="Delete the associated key file",
                margin_start=spacing,
                margin_end=spacing
            )
            dialog.del_key.set_active(True)
            dialog.get_content_area().add(dialog.del_key)
            dialog.set_titlebar(Gtk.HeaderBar(show_title_buttons=False))
            dialog.connect("response", self._confirm)
            dialog.show()

    def on_select_clicked(self, widget):
        """
        Select files for decryption
        """
        if self.file is not None:
            log = open(join(Utils.DATA_DIR, "otp.log"), "r").readlines()
            bn_log = [Utils.bn(line[:-1]) for line in log]
            filename = log[bn_log.index(self.file)][:-1]
            key = log[bn_log.index(self.key)][:-1]
            self.parent.stack.set_visible_child_name("decrypt")
            self.parent.decrypt.file.set_text(filename)
            self.parent.decrypt.key.set_text(key)
            if self.parent.decrypt.dir.get_text() == "":
                self.parent.decrypt.dir.set_text(dirname(filename))
            self.destroy()

    def _confirm(self, dialog, response):
        """
        Close upon confirming
        """
        if response == Gtk.ResponseType.OK:
            old_log = open(
                join(Utils.DATA_DIR, "otp.log"), "r"
            ).readlines()
            bn_log = [Utils.bn(line[:-1]) for line in old_log]
            if dialog.del_key.get_active():
                remove(old_log[bn_log.index(self.key)])
            ind = bn_log.index(self.file) - 1
            rmv = []
            for i in range(5):
                rmv.append(ind + i)
            new_log = [j for i, j in enumerate(old_log) if i not in rmv]
            with open(join(Utils.DATA_DIR, "otp.log"), "w") as logfile:
                for line in new_log:
                    logfile.write(line)
                logfile.close()
            self.destroy()
        dialog.destroy()
