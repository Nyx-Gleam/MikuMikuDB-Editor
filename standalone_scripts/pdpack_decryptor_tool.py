"""
standalone_scripts/pdpack_decryptor_tool.py
==============================================
Herramienta de diagnóstico standalone: abre un .pdpack (o un archivo de
caché de pv_ids_manager: .pvdb/.frag/.index) y muestra su contenido
decodificado como árbol explorable o como JSON plano.

*** Por qué se reescribió ***
La versión original importaba las clases de encriptación DIRECTO del
`Editor.py` monolítico (`from Editor import CustomEncryptionV1...`) y de
un `encryption_v4.py` suelto -- dos copias separadas de la misma lógica
que ya viven, corregidas y probadas, en `core/encryption.py` desde la
Fase 1 de esta migración (incluye el fix del bug de V3 que hacía
imposible abrir esos archivos). Mantener una tercera copia aparte
hubiera significado que esta herramienta se desincronizara de la lógica
real tarde o temprano -- exactamente el tipo de problema que
resolvimos varias veces durante la migración. Ahora importa directo de
`core.encryption` / `core.pv_ids_manager`, así que cualquier fix futuro
ahí se refleja aquí automáticamente, sin mantener una copia aparte.

También se quitó `ttkbootstrap` (ya no es una dependencia del proyecto)
-- usa `tkinter.ttk` normal. El resto del proyecto ya migró a PySide6,
pero esta herramienta se deja en Tkinter a propósito: es un diagnóstico
standalone de un solo archivo, y así no depende de tener PySide6
instalado para usarla.

*** Código muerto del original que NO se portó ***
- Las funciones sueltas `populate_tree`/`show_as_tree`/`show_as_text`/
  `display_decrypted_result` a nivel de módulo: nunca se llamaban desde
  ningún lado -- `DecryptorApp.open_file()` usa sus propios métodos
  (`show_json`/`show_as_text` de la clase), no estas funciones.
- `DecryptorApp.clear_output`/`append_text`: referencian
  `self.output_text`, que nunca se crea en `__init__` (solo se crean
  `self.tree`/`self.text_widget`). Habrían lanzado `AttributeError` si
  algo las hubiera llamado -- nada las llama.

*** Detección de formato ***
La lógica de `detect_encryptor` vive en `core/diagnostic_decoder.py` (no
aquí) a propósito: así es lógica pura, testeable sin necesitar tkinter
instalado. Este archivo solo la importa y construye la UI alrededor.

Uso:
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

        self.btn_open = ttk.Button(frame, text="Abrir archivo…", command=self.open_file)
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
        """Inserta recursivamente dict/list en el Treeview con tipo de dato y valor."""
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
            title="Seleccionar archivo",
            filetypes=[
                ("Todos", "*.*"),
                ("MikuMikuDB Pack", "*.pdpack"),
                ("PV Database (caché de pv_ids_manager)", "*.pvdb;*.frag;*.index;*.json"),
            ]
        )
        if not file:
            return

        try:
            with open(file, "rb") as f:
                blob = f.read()
        except Exception as e:
            self.clear_display()
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            return

        version_label, handler = detect_encryptor(blob, filename=file)

        if not handler:
            self.clear_display()
            messagebox.showerror("Error", "No se pudo detectar el sistema de encriptación/formato de este archivo.")
            self.status_label.configure(text="")
            return

        try:
            data = handler.decrypt_data(blob)
        except Exception as e:
            self.clear_display()
            messagebox.showerror("Error", f"No se pudo decodificar el archivo ({version_label}):\n{e}")
            self.status_label.configure(text="")
            return

        self.status_label.configure(text=f"Archivo: {os.path.basename(file)}  |  Formato detectado: {version_label}")

        answer = messagebox.askyesnocancel(
            "Elegir modo de vista",
            "¿Cómo quieres mostrar el resultado?\n\n"
            "Sí = Árbol (modo exploración)\n"
            "No = Texto plano (JSON)\n"
            "Cancelar = No mostrar",
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
