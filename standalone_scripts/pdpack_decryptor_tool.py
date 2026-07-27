"""
standalone_scripts/pdpack_decryptor_tool.py
==============================================
Standalone diagnostic tool: opens a .pdpack file (or a pv_ids_manager
cache file: .pvdb/.frag/.index) and displays its decoded contents either
as an interactive tree view or as plain JSON.

*** Why it was rewritten ***
The original version imported the encryption classes DIRECTLY from the
monolithic `Editor.py` (`from Editor import CustomEncryptionV1...`) and
from a separate `encryption_v4.py` file—two independent copies of the
same logic that already exist, have been fixed, and thoroughly tested in
`core/encryption.py` since Phase 1 of this migration (including the V3
bug fix that previously made those files impossible to open).

Keeping a third copy would eventually cause this tool to fall out of sync
with the actual encryption logic—exactly the type of problem that was
resolved multiple times during the migration. It now imports directly
from `core.encryption` / `core.pv_ids_manager`, so any future fixes made
there will automatically apply here without maintaining another copy.

`ttkbootstrap` was also removed (it is no longer a project dependency)
and replaced with the standard `tkinter.ttk`.

The rest of the project has already migrated to PySide6, but this tool
intentionally remains on Tkinter because it is a standalone diagnostic
utility contained in a single file, allowing it to run without requiring
PySide6 to be installed.

*** Dead code from the original that was NOT ported ***
- The standalone module-level functions
  `populate_tree` / `show_as_tree` / `show_as_text` /
  `display_decrypted_result`: they were never called from anywhere.
  `DecryptorApp.open_file()` uses its own class methods
  (`show_json` / `show_as_text`) instead.
- `DecryptorApp.clear_output` / `append_text`: these referenced
  `self.output_text`, which was never created in `__init__`
  (only `self.tree` and `self.text_widget` exist). They would have raised
  `AttributeError` if called—but nothing ever called them.

*** Format detection ***
The `detect_encryptor` logic lives in `core/diagnostic_decoder.py`
instead of this file on purpose. This keeps it as pure, testable logic
that does not require tkinter to be installed. This file simply imports
it and builds the UI around it.

Usage:
    python standalone_scripts/pdpack_decryptor_tool.py
"""
from __future__ import annotations

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.diagnostic_decoder import detect_encryptor


class DecryptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MikuMikuDB Decryptor Tool")
        self.root.geometry("800x600")

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True)

        self.btn_open = ttk.Button(frame, text="Open File...", command=self.open_file)
        self.btn_open.pack(pady=5)

        self.status_label = ttk.Label(frame, text="")
        self.status_label.pack(pady=2)

        self.display_container = ttk.Frame(frame)
        self.display_container.pack(fill="both", expand=True, pady=5)

        self.tree: ttk.Treeview | None = None
        self.text_widget: scrolledtext.ScrolledText | None = None

    def clear_display(self):
        for w in self.display_container.winfo_children():
            w.destroy()
        self.tree = None
        self.text_widget = None

    def insert_json(self, parent, key, value):
        """Recursively insert dict/list objects into the Treeview with their data type and value."""
        if isinstance(value, dict):
            node = self.tree.insert(parent, "end", text=key, values=("dict", ""))
            for k, v in value.items():
                self.insert_json(node, k, v)
        elif isinstance(value, list):
            node = self.tree.insert(parent, "end", text=f"{key} [list]", values=("list", ""))
            for i, v in enumerate(value):
                self.insert_json(node, f"[{i}]", v)
        else:
            self.tree.insert(parent, "end", text=key, values=(type(value).__name__, str(value)))

    def show_json(self, data):
        self.clear_display()

        self.tree = ttk.Treeview(self.display_container, columns=("type", "value"), show="tree headings")
        self.tree.heading("#0", text="Key")
        self.tree.heading("type", text="Type")
        self.tree.heading("value", text="Value")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(self.display_container, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        self.insert_json("", "root", data)
        root_item = self.tree.get_children()[0]
        self.tree.item(root_item, open=True)

    def show_as_text(self, data):
        self.clear_display()

        self.text_widget = scrolledtext.ScrolledText(self.display_container, wrap="none", font=("Consolas", 11))
        self.text_widget.pack(fill="both", expand=True)

        pretty = json.dumps(data, indent=4, ensure_ascii=False)
        self.text_widget.insert("end", pretty)

    def open_file(self):
        file = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("All Files", "*.*"),
                ("MikuMikuDB Pack", "*.pdpack"),
                ("PV Database (pv_ids_manager cache)", "*.pvdb;*.frag;*.index;*.json"),
            ]
        )
        if not file:
            return

        try:
            with open(file, "rb") as f:
                blob = f.read()
        except Exception as e:
            self.clear_display()
            messagebox.showerror("Error", f"Failed to read the file:\n{e}")
            return

        version_label, handler = detect_encryptor(blob, filename=file)

        if not handler:
            self.clear_display()
            messagebox.showerror("Error", "Unable to detect the encryption system or file format.")
            self.status_label.configure(text="")
            return

        try:
            data = handler.decrypt_data(blob)
        except Exception as e:
            self.clear_display()
            messagebox.showerror("Error", f"Failed to decode the file ({version_label}):\n{e}")
            self.status_label.configure(text="")
            return

        self.status_label.configure(text=f"File: {os.path.basename(file)}  |  Detected format: {version_label}")

        answer = messagebox.askyesnocancel(
            "Choose Display Mode",
            "How would you like to display the result?\n\n"
            "Yes = Tree View (exploration mode)\n"
            "No = Plain Text (JSON)\n"
            "Cancel = Do not display",
        )
        if answer is None:
            return
        if answer:
            self.show_json(data)
        else:
            self.show_as_text(data)


if __name__ == "__main__":
    root = tk.Tk()
    app = DecryptorApp(root)
    root.mainloop()
