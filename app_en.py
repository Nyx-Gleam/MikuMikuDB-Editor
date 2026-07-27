#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Diva mod_pv_db.txt Generator GUI
Generates mod_pv_db.txt files for Project Diva song packs with GUI interface
"""

import os
import time
import glob
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    DND_FILES = None
    TkinterDnD = None

class CustomEncryption:
    """Custom encryption handler for .pdpack files"""
    
    def __init__(self, password="MikuMikuDB_NyxC_2025"):
        self.password = password.encode()
        self.salt = b'mikumiku_salt_v1'  # Fixed salt for consistency
    
    def _derive_key(self):
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_data(self, data):
        """Encrypt JSON data to encrypted bytes"""
        try:
            # Convert data to JSON string
            json_string = json.dumps(data, indent=2, ensure_ascii=False)
            json_bytes = json_string.encode('utf-8')
            
            # Create Fernet cipher
            key = self._derive_key()
            fernet = Fernet(key)
            
            # Encrypt the data
            encrypted_data = fernet.encrypt(json_bytes)
            
            # Add custom header for file identification
            header = b'PDPACK_ENCRYPTED_V1\n'
            return header + encrypted_data
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_bytes):
        """Decrypt encrypted bytes back to JSON data"""
        try:
            # Check for custom header
            if not encrypted_bytes.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                raise Exception("Invalid or corrupted encrypted file format")
            
            # Remove header
            encrypted_data = encrypted_bytes[len(b'PDPACK_ENCRYPTED_V1\n'):]
            
            # Create Fernet cipher
            key = self._derive_key()
            fernet = Fernet(key)
            
            # Decrypt the data
            decrypted_bytes = fernet.decrypt(encrypted_data)
            json_string = decrypted_bytes.decode('utf-8')
            
            # Parse JSON
            return json.loads(json_string)
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

class SongVariantDialog:
    def __init__(self, parent, variant_data=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configure Audio Variant")

        window_width = 540
        window_height = 520

        # Centrar en pantalla
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.name_var = tk.StringVar(value=variant_data.get('name', '') if variant_data else '')
        self.name_en_var = tk.StringVar(value=variant_data.get('name_en', '') if variant_data else '')
        self.name_reading_var = tk.StringVar(value=variant_data.get('name_reading', variant_data.get('name', '')) if variant_data else '')
        self.vocal_disp_var = tk.StringVar(value=variant_data.get('vocal_disp', '') if variant_data else '')
        self.vocal_disp_en_var = tk.StringVar(value=variant_data.get('vocal_disp_en', '') if variant_data else '')
        
        # ← NUEVO (suffix y performers)
        self.file_suffix_var = tk.StringVar(value=variant_data.get('file_suffix', '') if variant_data else '')
        self.performers = variant_data.get('performers', ['MIK']) if variant_data else ['MIK']
        
        # Personajes disponibles
        self.characters = {
            'MIK': 'Hatsune Miku',
            'RIN': 'Kagamine Rin',
            'LEN': 'Kagamine Len',
            'LUK': 'Megurine Luka',
            'KAI': 'KAITO',
            'MEI': 'MEIKO',
            'HAK': 'Yowane Haku',
            'NER': 'Akita Neru',
            'SAK': 'Sakine Meiko',
            'TET': 'Kasane Teto'
        }
        
        self.create_widgets()
        
    def is_hiragana(self, text):
        """Check if text contains only Hiragana characters (and common punctuation/spaces)"""
        # Hiragana range: U+3040-U+309F
        # Also allow common punctuation, spaces, and numbers
        hiragana_pattern = r'^[\u3040-\u309F\s\u3000ー・。、！？\d]+$'
        return bool(re.match(hiragana_pattern, text))
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Título
        ttk.Label(
            main_frame,
            text="Configure Audio Variant",
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # --- Campos básicos (fila 1..5)
        fields = [
            ("Variant name: *", self.name_var),
            ("English name: *", self.name_en_var),
            ("Variant reading (Hiragana): *", self.name_reading_var),   # ← Campo agregado con indicación
            ("Variant artist: *", self.vocal_disp_var),
            ("Artist in English: *", self.vocal_disp_en_var)
        ]

        for i, (label, var) in enumerate(fields, 1):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(main_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
            
            # Add validation callback for name_reading field
            if "reading" in label.lower():
                var.trace('w', self.validate_hiragana)

        # Add validation label for Hiragana
        self.hiragana_validation_label = ttk.Label(
            main_frame, 
            text="", 
            foreground="red",
            font=('Arial', 8)
        )
        self.hiragana_validation_label.grid(row=len(fields)+1, column=1, sticky=tk.W, padx=(10, 0))

        # --- Sección Performers (después de los campos básicos)
        row_performers = len(fields) + 2  # primera fila libre después del label de validación

        # Etiqueta
        ttk.Label(
            main_frame,
            text="Selected performers:"
        ).grid(row=row_performers, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))

        # Listbox donde se muestran los performers actuales
        self.performers_listbox = tk.Listbox(main_frame, height=4)
        self.performers_listbox.grid(
            row=row_performers+1, column=0, columnspan=2,
            sticky=(tk.W, tk.E), pady=(0, 5)
        )

        # Botones Add / Remove
        perf_btn_frame = ttk.Frame(main_frame)
        perf_btn_frame.grid(row=row_performers+2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        ttk.Button(
            perf_btn_frame,
            text="Add",
            command=self.add_variant_performer
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            perf_btn_frame,
            text="Remove",
            command=self.remove_variant_performer
        ).pack(side=tk.LEFT)

        # Combobox para elegir personaje
        ttk.Label(
            main_frame,
            text="Select character:"
        ).grid(row=row_performers+3, column=0, sticky=tk.W, pady=(0, 2))
        self.character_var = tk.StringVar(value='MIK')
        char_combo = ttk.Combobox(
            main_frame,
            textvariable=self.character_var,
            width=30,
            state="readonly"
        )
        char_combo['values'] = [f"{code} - {name}" for code, name in self.characters.items()]
        char_combo.grid(
            row=row_performers+3, column=1, sticky=(tk.W, tk.E),
            pady=(0, 2), padx=(10, 0)
        )

        # --- Campo para el sufijo de archivo (después de Performers)
        row_file = row_performers + 4
        ttk.Label(
            main_frame,
            text="File name suffix: *"
        ).grid(row=row_file, column=0, sticky=tk.W, pady=2)
        ttk.Entry(
            main_frame,
            textvariable=self.file_suffix_var,
            width=40
        ).grid(row=row_file, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # --- Nota sobre campos obligatorios
        ttk.Label(
            main_frame,
            text="* Required fields",
            font=('Arial', 8),
            foreground="gray"
        ).grid(row=row_file+1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # --- Botones Accept / Cancel
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row_file+2, column=0, columnspan=2, pady=(20, 0))
        ttk.Button(button_frame, text="Accept", command=self.accept).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)

        # Configurar expansiones
        main_frame.columnconfigure(1, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

        # Mostrar la lista inicial de performers
        self.update_variant_performers_display()
        
        # Initial validation
        self.validate_hiragana()

    def validate_hiragana(self, *args):
        """Validate that name_reading contains only Hiragana"""
        text = self.name_reading_var.get()
        if text and not self.is_hiragana(text):
            self.hiragana_validation_label.config(text="⚠ Please use only Hiragana characters")
        else:
            self.hiragana_validation_label.config(text="")

    def update_variant_performers_display(self):
        self.performers_listbox.delete(0, tk.END)
        for p in self.performers:
            name = self.characters.get(p, p)
            self.performers_listbox.insert(tk.END, f"{p} - {name}")

    def add_variant_performer(self):
        # Don't allow more than 6 performers
        if len(self.performers) >= 6:
            messagebox.showerror("Error", "Cannot add more than 6 performers to a variant")
            return

        selected = self.character_var.get().split(' - ')[0]
        if selected not in self.performers:
            self.performers.append(selected)
            self.update_variant_performers_display()

    def remove_variant_performer(self):
        # Don't allow less than 6 performers
        if len(self.performers) <= 1:
            messagebox.showerror("Error", "Variant must have at least 1 performer")
            return

        sel = self.performers_listbox.curselection()
        if sel:
            idx = sel[0]
            del self.performers[idx]
            self.update_variant_performers_display()
        
    def accept(self):
        # Validate that there is at least 1 performer
        if not self.performers or len(self.performers) < 1:
            messagebox.showerror("Error", "Variant must have at least 1 performer")
            return

        # Validate required fields
        required_fields = [
            (self.name_var.get().strip(), "Variant name"),
            (self.name_en_var.get().strip(), "English name"),
            (self.name_reading_var.get().strip(), "Variant reading"),
            (self.vocal_disp_var.get().strip(), "Variant artist"),
            (self.vocal_disp_en_var.get().strip(), "Artist in English"),
            (self.file_suffix_var.get().strip(), "File name suffix")
        ]

        missing_fields = []
        for value, field_name in required_fields:
            if not value:
                missing_fields.append(field_name)

        if missing_fields:
            messagebox.showerror(
                "Required Fields Missing", 
                f"Please fill in the following required fields:\n\n• " + "\n• ".join(missing_fields)
            )
            return

        # Validate that name_reading is written in Hiragana
        name_reading = self.name_reading_var.get().strip()
        if not self.is_hiragana(name_reading):
            messagebox.showerror(
                "Invalid Input", 
                "Variant reading must contain only Hiragana characters.\n\n",
                "Please use Hiragana (ひらがな) for the reading field."
            )
            return


        self.result = {
            'name': self.name_var.get().strip(),
            'name_en': self.name_en_var.get().strip(),
            'name_reading': name_reading,
            'vocal_disp': self.vocal_disp_var.get().strip(),
            'vocal_disp_en': self.vocal_disp_en_var.get().strip(),
            'file_suffix': self.file_suffix_var.get().strip(),
            'performers': self.performers.copy()
        }
        self.dialog.destroy()
        
    def cancel(self):
        self.result = None
        self.dialog.destroy()

class SongConfigDialog:
    def __init__(self, parent, song_data=None):
        self.result = None
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configure Song")
    
        window_width = 800
        window_height = 580
    
        # Center the dialog on screen
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # --- Basic variables (pre-filled if available)
        self.pv_id_var = tk.StringVar(value=song_data.get('pv_id', '') if song_data else '')
        self.song_name_var = tk.StringVar(value=song_data.get('song_name', '') if song_data else '')
        self.song_name_en_var = tk.StringVar(value=song_data.get('song_name_en', '') if song_data else '')
        self.song_name_reading_var = tk.StringVar(value=song_data.get('song_name_reading', '') if song_data else '')
        self.bpm_var = tk.StringVar(value=song_data.get('bpm', '') if song_data else '')
        # date is not manually editable; it will be overwritten in accept()
        self.date_var = tk.StringVar(value=song_data.get('date', '') if song_data else '')
        self.sabi_start_var = tk.StringVar(value=song_data.get('sabi_start', '') if song_data else '')
        self.sabi_play_var = tk.StringVar(value=song_data.get('sabi_play', '') if song_data else '')
    
        # --- Difficulty variables (copied if they already exist)
        self.difficulties = {}
        if song_data and 'difficulties' in song_data:
            self.difficulties = song_data['difficulties'].copy()
    
        # --- Performers (list of character codes)
        self.performers = song_data.get('performers', ['MIK']) if song_data else ['MIK']
    
        # --- Existing songinfo and audio_variants
        self.songinfo = song_data.get('songinfo', {}) if song_data else {}
        self.audio_variants = song_data.get('audio_variants', []) if song_data else []
    
        self.create_widgets()
        
    def validate_numeric(self, char):
        """Validate that only numbers are entered"""
        return char.isdigit()

    def create_widgets(self):
        # Register numeric input validation
        vcmd = (self.dialog.register(self.validate_numeric), '%S')

        # Main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tabs
        self.create_basic_tab(vcmd)
        self.create_difficulty_tab()
        self.create_performers_tab()
        self.create_songinfo_tab()
        self.create_variants_tab()

        # "Accept" / "Cancel" buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(button_frame, text="Accept", command=self.accept).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)

    def create_basic_tab(self, vcmd):
        basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_frame, text="Basic Information")

        # PV ID (numbers only, max 4 digits)
        ttk.Label(basic_frame, text="PV ID: *").grid(row=0, column=0, sticky=tk.W, pady=2)
        pv_entry = ttk.Entry(basic_frame, textvariable=self.pv_id_var, width=40, validate='key', validatecommand=vcmd)
        pv_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # Original name (required)
        ttk.Label(basic_frame, text="Original name: *").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(basic_frame, textvariable=self.song_name_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # English name (required)
        ttk.Label(basic_frame, text="English name: *").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(basic_frame, textvariable=self.song_name_en_var, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # Hiragana name (required)
        ttk.Label(basic_frame, text="Hiragana name: *").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(basic_frame, textvariable=self.song_name_reading_var, width=40).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # BPM (numbers only, required)
        ttk.Label(basic_frame, text="BPM: *").grid(row=4, column=0, sticky=tk.W, pady=2)
        bpm_entry = ttk.Entry(basic_frame, textvariable=self.bpm_var, width=40, validate='key', validatecommand=vcmd)
        bpm_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # Sabi start time (numbers only)
        ttk.Label(basic_frame, text="Sabi start time:").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(
            basic_frame,
            from_=0,
            to=999999,
            textvariable=self.sabi_start_var,
            width=10,
            validate='key',
            validatecommand=vcmd
        ).grid(row=5, column=1, sticky=(tk.W), pady=2, padx=(10, 0))

        # Sabi duration (numbers only)
        ttk.Label(basic_frame, text="Sabi duration:").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(
            basic_frame,
            from_=0,
            to=999999,
            textvariable=self.sabi_play_var,
            width=10,
            validate='key',
            validatecommand=vcmd
        ).grid(row=6, column=1, sticky=(tk.W), pady=2, padx=(10, 0))

        # Note about required fields
        ttk.Label(basic_frame, text="* Required fields", foreground="red", font=('TkDefaultFont', 8)).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        basic_frame.columnconfigure(1, weight=1)
        
    def create_difficulty_tab(self):
        diff_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(diff_frame, text="Difficulties")

        # 1) Boolean variables: True if the difficulty exists in song_data['difficulties']
        self.easy_var = tk.BooleanVar(value=('easy' in self.difficulties))
        self.normal_var = tk.BooleanVar(value=('normal' in self.difficulties))
        self.hard_var = tk.BooleanVar(value=('hard' in self.difficulties))
        self.extreme_var = tk.BooleanVar(value=('extreme' in self.difficulties))
        self.extreme_extra_var = tk.BooleanVar(value=('extreme_extra' in self.difficulties))

        # 2) Function to convert "PV_LV_07_5" → "7.5"
        def pv_to_numeric(pv_str):
            try:
                parts = pv_str.split('_')  # e.g., ["PV", "LV", "07", "5"]
                integer = int(parts[2])
                decimal = int(parts[3])
                return f"{integer}.{decimal}"
            except:
                return ''

        # 3) Initialize StringVar for the combobox:
        #    If the key exists in self.difficulties, show its numeric value; else, empty string.
        if 'easy' in self.difficulties:
            easy_default = pv_to_numeric(self.difficulties['easy']['level'])
        else:
            easy_default = ''
        self.easy_level_var = tk.StringVar(value=easy_default)

        if 'normal' in self.difficulties:
            normal_default = pv_to_numeric(self.difficulties['normal']['level'])
        else:
            normal_default = ''
        self.normal_level_var = tk.StringVar(value=normal_default)

        if 'hard' in self.difficulties:
            hard_default = pv_to_numeric(self.difficulties['hard']['level'])
        else:
            hard_default = ''
        self.hard_level_var = tk.StringVar(value=hard_default)

        if 'extreme' in self.difficulties:
            extreme_default = pv_to_numeric(self.difficulties['extreme']['level'])
        else:
            extreme_default = ''
        self.extreme_level_var = tk.StringVar(value=extreme_default)

        if 'extreme_extra' in self.difficulties:
            extreme_extra_default = pv_to_numeric(self.difficulties['extreme_extra']['level'])
        else:
            extreme_extra_default = ''
        self.extreme_extra_level_var = tk.StringVar(value=extreme_extra_default)

        # 4) Define value ranges per difficulty
        #    (each list contains strings like "7.5", "8.0", ...).
        easy_options = ["1.0","1.5","2.0","2.5","3.0","3.5","4.0","4.5"]
        normal_options = ["3.0","3.5","4.0","4.5","5.0","5.5","6.0"]
        hard_options = ["5.0","5.5","6.0","6.5","7.0","7.5","8.0","8.5"]
        extreme_options = ["6.0","6.5","7.0","7.5","8.0","8.5","9.0","9.5","10.0"]

        # 5) List to iterate and create widgets
        difficulties = [
            ("Easy", self.easy_var, self.easy_level_var, easy_options),
            ("Normal", self.normal_var, self.normal_level_var, normal_options),
            ("Hard", self.hard_var, self.hard_level_var, hard_options),
            ("Extreme", self.extreme_var, self.extreme_level_var, extreme_options),
            ("Extra Extreme", self.extreme_extra_var, self.extreme_extra_level_var, extreme_options)
        ]

        for i, (name, var, level_var, options) in enumerate(difficulties):
            # Checkbox
            ttk.Checkbutton(diff_frame, text=name, variable=var).grid(row=i, column=0, sticky=tk.W, pady=2)
            # Label "Level:"
            ttk.Label(diff_frame, text="Level:").grid(row=i, column=1, sticky=tk.W, padx=(20, 5))
            # Read-only Combobox with its specific range
            ttk.Combobox(
                diff_frame,
                textvariable=level_var,
                values=options,
                width=10,
                state="readonly"
            ).grid(row=i, column=2, sticky=tk.W)

        # Note about selecting at least one difficulty
        ttk.Label(diff_frame, text="* At least one difficulty must be selected", foreground="red", font=('TkDefaultFont', 8)).grid(row=len(difficulties), column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

    def create_performers_tab(self):
        perf_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(perf_frame, text="Performers")

        # Label + Listbox for selected performers
        ttk.Label(perf_frame, text="Selected performers:").pack(anchor=tk.W)
        self.performers_listbox = tk.Listbox(perf_frame, height=6)
        self.performers_listbox.pack(fill='x', pady=(5, 10))

        # Add / Remove buttons
        perf_buttons = ttk.Frame(perf_frame)
        perf_buttons.pack(fill='x')
        ttk.Button(perf_buttons, text="Add", command=self.add_performer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(perf_buttons, text="Remove", command=self.remove_performer).pack(side=tk.LEFT)

        # Read-only character combobox
        ttk.Label(perf_frame, text="Select character:").pack(anchor=tk.W, pady=(20, 5))
        self.characters = {
            'MIK': 'Hatsune Miku',
            'RIN': 'Kagamine Rin',
            'LEN': 'Kagamine Len',
            'LUK': 'Megurine Luka',
            'KAI': 'KAITO',
            'MEI': 'MEIKO',
            'HAK': 'Yowane Haku',
            'NER': 'Akita Neru',
            'SAK': 'Sakine Meiko',
            'TET': 'Kasane Teto'
        }
        self.character_var = tk.StringVar(value='MIK')
        char_combo = ttk.Combobox(
            perf_frame,
            textvariable=self.character_var,
            width=30,
            state="readonly"
        )
        char_combo['values'] = [f"{code} - {name}" for code, name in self.characters.items()]
        char_combo.pack(fill='x')

        self.update_performers_display()
        
    def create_songinfo_tab(self):
        info_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(info_frame, text="Song Information")

        self.songinfo_vars = {}
        fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']

        # Original fields (any language)
        for field in fields:
            self.songinfo_vars[field] = tk.StringVar(value=self.songinfo.get(field, ''))
        # English fields
        for field in fields:
            self.songinfo_vars[field + '_en'] = tk.StringVar(value=self.songinfo.get(field + '_en', ''))

        labels = {
            'arranger': 'Arranger:',
            'guitar_player': 'Guitar Player:',
            'lyrics': 'Lyricist:',
            'manipulator': 'Manipulator:',
            'music': 'Composer/Artist:',
            'pv_editor': 'PV Editor:'
        }
        labels_en = {
            'arranger_en': 'Arranger (EN):',
            'guitar_player_en': 'Guitar Player (EN):',
            'lyrics_en': 'Lyricist (EN):',
            'manipulator_en': 'Manipulator (EN):',
            'music_en': 'Composer/Artist (EN):',
            'pv_editor_en': 'PV Editor (EN):'
        }

        row = 0
        ttk.Label(info_frame, text="Original", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        for field in fields:
            ttk.Label(info_frame, text=labels[field]).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(info_frame, textvariable=self.songinfo_vars[field], width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
            row += 1

        ttk.Separator(info_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        ttk.Label(info_frame, text="English", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        for field in fields:
            field_en = field + '_en'
            ttk.Label(info_frame, text=labels_en[field_en]).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(info_frame, textvariable=self.songinfo_vars[field_en], width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
            row += 1

        # Note about filling at least one field in both Original and English sections
        ttk.Label(info_frame, text="* At least one field in Original and one in English must be completed", 
                  foreground="red", font=('TkDefaultFont', 8)).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        info_frame.columnconfigure(1, weight=1)

    def update_variants_display(self):
        # This method populates the audio variants treeview
        for item in self.variants_tree.get_children():
            self.variants_tree.delete(item)

        for i, variant in enumerate(self.audio_variants):
            self.variants_tree.insert(
                '', 'end',
                values=(
                    variant.get('name', ''),
                    variant.get('name_en', ''),
                    variant.get('vocal_disp', '')
                )
            )

    def create_variants_tab(self):
        variants_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(variants_frame, text="Audio Variants")

        ttk.Label(variants_frame, text="Configured audio variants:").pack(anchor=tk.W)

        # Treeview of audio variants
        self.variants_tree = ttk.Treeview(
            variants_frame,
            columns=('name', 'name_en', 'artist'),
            show='headings',
            height=8
        )
        self.variants_tree.heading('name', text='Original Name')
        self.variants_tree.heading('name_en', text='English Name')
        self.variants_tree.heading('artist', text='Artist')
        self.variants_tree.pack(fill='both', expand=True, pady=(5, 10))

        # Buttons to add/edit/remove variants
        variants_buttons = ttk.Frame(variants_frame)
        variants_buttons.pack(fill='x')
        ttk.Button(variants_buttons, text="Add Variant", command=self.add_variant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(variants_buttons, text="Edit Variant", command=self.edit_variant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(variants_buttons, text="Remove Variant", command=self.remove_variant).pack(side=tk.LEFT)

        # Call update_variants_display (after the treeview is defined)
        self.update_variants_display()
        
    def update_performers_display(self):
        self.performers_listbox.delete(0, tk.END)
        for performer in self.performers:
            char_name = self.characters.get(performer, performer)
            self.performers_listbox.insert(tk.END, f"{performer} - {char_name}")
    
    def add_performer(self):
        # Enforce a maximum of 6 performers
        if len(self.performers) >= 6:
            messagebox.showerror("Error", "Cannot add more than 6 performers")
            return
    
        selected = self.character_var.get().split(' - ')[0]
        if selected not in self.performers:
            self.performers.append(selected)
            self.update_performers_display()
    
    def remove_performer(self):
        # Enforce at least 1 performer
        if len(self.performers) <= 1:
            messagebox.showerror("Error", "There must be at least 1 performer")
            return
    
        selection = self.performers_listbox.curselection()
        if selection:
            index = selection[0]
            del self.performers[index]
            self.update_performers_display()
    
    def add_variant(self):
        dialog = SongVariantDialog(self.dialog)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.audio_variants.append(dialog.result)
            self.update_variants_display()
    
    def edit_variant(self):
        selection = self.variants_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a variant to edit")
            return
        item = selection[0]
        index = self.variants_tree.index(item)
        dialog = SongVariantDialog(self.dialog, self.audio_variants[index])
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.audio_variants[index] = dialog.result
            self.update_variants_display()
    
    def remove_variant(self):
        selection = self.variants_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a variant to remove")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this variant?"):
            item = selection[0]
            index = self.variants_tree.index(item)
            del self.audio_variants[index]
            self.update_variants_display()
    
    def accept(self):
        # -------------------------------
        # 1) PV ID: required, numeric, positive, in range 001-9999
        if not self.pv_id_var.get().strip():
            messagebox.showerror("Error", "PV ID is required")
            return
        pv_id_raw = self.pv_id_var.get().strip()
        try:
            pv_id_num = int(pv_id_raw)
            if pv_id_num < 1 or pv_id_num > 9999:
                messagebox.showerror("Error", "PV ID must be between 001 and 9999")
                return
            pv_id_formatted = f"{pv_id_num:03d}"
        except ValueError:
            messagebox.showerror("Error", "PV ID must be a valid number")
            return
    
        # -------------------------------
        # 2) Song names: required
        if not self.song_name_var.get().strip():
            messagebox.showerror("Error", "Original name is required")
            return
        if not self.song_name_en_var.get().strip():
            messagebox.showerror("Error", "English name is required")
            return
    
        # -------------------------------
        # 3) Hiragana: required, must contain only Hiragana characters (plus 'ー' and spaces)
        hira = self.song_name_reading_var.get().strip()
        if not hira:
            messagebox.showerror("Error", "Hiragana name is required")
            return
        if not re.fullmatch(r'[\u3040-\u309Fー\s]+', hira):
            messagebox.showerror("Error", "Hiragana name must only contain Hiragana characters")
            return
    
        # -------------------------------
        # 4) BPM: required, positive integer
        if not self.bpm_var.get().strip():
            messagebox.showerror("Error", "BPM is required")
            return
        try:
            bpm_val = int(self.bpm_var.get().strip())
            if bpm_val <= 0:
                messagebox.showerror("Error", "BPM must be a positive integer")
                return
        except ValueError:
            messagebox.showerror("Error", "BPM must be a valid integer")
            return
    
        # -------------------------------
        # 5) At least one difficulty must be selected
        has_difficulty = (self.easy_var.get() or self.normal_var.get() or 
                          self.hard_var.get() or self.extreme_var.get() or 
                          self.extreme_extra_var.get())
        if not has_difficulty:
            messagebox.showerror("Error", "At least one difficulty must be selected")
            return
    
        # -------------------------------
        # 6) Performers: minimum 1, maximum 6
        if len(self.performers) < 1:
            messagebox.showerror("Error", "There must be at least 1 performer")
            return
        if len(self.performers) > 6:
            messagebox.showerror("Error", "Cannot have more than 6 performers")
            return
    
        # -------------------------------
        # 7) Song Information: at least one field in Original and one in English must be completed
        fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']
        has_original = any(self.songinfo_vars[field].get().strip() for field in fields)
        has_english = any(self.songinfo_vars[field + '_en'].get().strip() for field in fields)
    
        if not has_original:
            messagebox.showerror("Error", "At least one field in Original section must be completed")
            return
        if not has_english:
            messagebox.showerror("Error", "At least one field in English section must be completed")
            return
    
        # -------------------------------
        # 8) Convert each numeric level (e.g., "7.5") to "PV_LV_07_5"
        def numeric_to_pv(numeric_str):
            try:
                num = float(numeric_str)
                integer = int(num)
                decimal = int((num - integer) * 10)
                return f"PV_LV_{integer:02d}_{decimal}"
            except:
                return "PV_LV_05_0"
    
        difficulties = {}
        if self.easy_var.get():
            if not self.easy_level_var.get():
                messagebox.showerror("Error", "Easy difficulty level must be selected")
                return
            difficulties['easy'] = {
                'level': numeric_to_pv(self.easy_level_var.get()),
                'level_sort_index': '50'
            }
        if self.normal_var.get():
            if not self.normal_level_var.get():
                messagebox.showerror("Error", "Normal difficulty level must be selected")
                return
            difficulties['normal'] = {
                'level': numeric_to_pv(self.normal_level_var.get()),
                'level_sort_index': '50'
            }
        if self.hard_var.get():
            if not self.hard_level_var.get():
                messagebox.showerror("Error", "Hard difficulty level must be selected")
                return
            difficulties['hard'] = {
                'level': numeric_to_pv(self.hard_level_var.get()),
                'level_sort_index': '80'
            }
        if self.extreme_var.get():
            if not self.extreme_level_var.get():
                messagebox.showerror("Error", "Extreme difficulty level must be selected")
                return
            difficulties['extreme'] = {
                'level': numeric_to_pv(self.extreme_level_var.get()),
                'level_sort_index': '20'
            }
        if self.extreme_extra_var.get():
            if not self.extreme_extra_level_var.get():
                messagebox.showerror("Error", "Extra Extreme difficulty level must be selected")
                return
            difficulties['extreme_extra'] = {
                'level': numeric_to_pv(self.extreme_extra_level_var.get()),
                'level_sort_index': '50'
            }
    
        # -------------------------------
        # 9) Songinfo: collect non-empty fields
        songinfo = {}
        for field, var in self.songinfo_vars.items():
            value = var.get().strip()
            if value:
                songinfo[field] = value
    
        # -------------------------------
        # 10) Date: assign current date in "yyyymmdd" format
        from datetime import datetime
        current_date = datetime.now().strftime("%Y%m%d")
    
        # -------------------------------
        # 11) Sabi start/duration: from self.sabi_start_var / self.sabi_play_var
        sabi_start = self.sabi_start_var.get().strip() if self.sabi_start_var.get().strip() else "0"
        sabi_play = self.sabi_play_var.get().strip() if self.sabi_play_var.get().strip() else "0"
    
        # -------------------------------
        # 12) Build final result
        self.result = {
            'pv_id': pv_id_formatted,
            'song_name': self.song_name_var.get().strip(),
            'song_name_en': self.song_name_en_var.get().strip(),
            'song_name_reading': hira,
            'bpm': str(bpm_val),
            'date': current_date,
            'sabi_start': sabi_start,
            'sabi_play': sabi_play,
            'difficulties': difficulties,
            'performers': self.performers,
            'songinfo': songinfo,
            'audio_variants': self.audio_variants
        }
    
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()

class ProjectDivaModEditor:
    def __init__(self):
        if DRAG_DROP_AVAILABLE:
            try:
                self.root = TkinterDnD.Tk()
            except:
                import tkinter as tk
                self.root = tk.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("MikuMikuDB Editor")
        
        # Get screen dimensions for better responsiveness
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set minimum size and initial size based on screen resolution
        min_width = 800
        min_height = 600
        
        # Calculate optimal window size (80% of screen, but not less than minimum)
        window_width = max(min_width, int(screen_width * 0.8))
        window_height = max(min_height, int(screen_height * 0.8))
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(min_width, min_height)
        
        # Center the window on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Maximize only if screen is large enough
        # if screen_width >= 1200 and screen_height >= 800:
        #    self.root.state("zoomed")

        self.root.state("zoomed")
        
        self.set_icon()
        
        # Data
        self.pack_name = ""
        self.pack_name_jp = ""
        self.songs = []

        # Setup scrollable main frame BEFORE other components
        self.setup_scrollable_main_frame()
        
        self.setup_drag_drop()
        self.setup_drag_visual_feedback()
        self.setup_autosave()
        self.create_widgets()
    
    def setup_scrollable_main_frame(self):
        """Setup scrollable main frame for better resolution support"""
        try:
            # Create main canvas and scrollbar
            self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
            self.main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
            
            # Create scrollable frame
            self.scrollable_frame = ttk.Frame(self.main_canvas)
            
            # Configure canvas
            self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
            
            # Pack canvas and scrollbar
            self.main_canvas.pack(side="left", fill="both", expand=True)
            self.main_scrollbar.pack(side="right", fill="y")
            
            # Create window in canvas
            self.canvas_window = self.main_canvas.create_window(
                (0, 0), window=self.scrollable_frame, anchor="nw"
            )
            
            # Configure scrollable frame
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            )
            
            # Configure canvas window width
            self.main_canvas.bind(
                "<Configure>",
                self.on_canvas_configure
            )
            
            # Bind mousewheel to canvas
            self.bind_mousewheel()
            
            # Now use self.scrollable_frame as the parent for all widgets instead of self.root
            
        except Exception as e:
            print(f"Error setting up scrollable frame: {e}")
            # Fallback to using root directly
            self.scrollable_frame = self.root

    def on_canvas_configure(self, event):
        """Handle canvas resize to adjust scrollable frame width"""
        try:
            canvas_width = event.width
            self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)
        except:
            pass

    def bind_mousewheel(self):
        """Bind mousewheel events for scrolling"""
        try:
            # Bind mousewheel events
            self.main_canvas.bind("<MouseWheel>", self.on_mousewheel)
            self.main_canvas.bind("<Button-4>", self.on_mousewheel)
            self.main_canvas.bind("<Button-5>", self.on_mousewheel)
            
            # Bind focus events to enable/disable scrolling
            self.main_canvas.bind("<Enter>", self.bind_to_mousewheel)
            self.main_canvas.bind("<Leave>", self.unbind_from_mousewheel)
            
        except Exception as e:
            print(f"Error binding mousewheel: {e}")

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        try:
            # Windows and MacOS
            if event.delta:
                delta = -1 * (event.delta / 120)
            # Linux
            elif event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                delta = 0
                
            # Scroll the canvas
            self.main_canvas.yview_scroll(int(delta), "units")
            
        except:
            pass

    def bind_to_mousewheel(self, event):
        """Enable mousewheel scrolling when mouse enters canvas"""
        try:
            self.root.bind_all("<MouseWheel>", self.on_mousewheel)
            self.root.bind_all("<Button-4>", self.on_mousewheel)
            self.root.bind_all("<Button-5>", self.on_mousewheel)
        except:
            pass

    def unbind_from_mousewheel(self, event):
        """Disable mousewheel scrolling when mouse leaves canvas"""
        try:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except:
            pass

    def setup_autosave(self):
        """Set up the autosave system"""
        self.autosave_folder = "Autosaves"
        self.autosave_interval = 5 * 60 * 1000
        self.max_autosave_files = 60

        # Create autosave folder if doesn't exists
        if not os.path.exists(self.autosave_folder):
            os.makedirs(self.autosave_folder)

        # Start autosave timer
        self.schedule_autosave()

    def schedule_autosave(self):
        """Schedule the next autosave"""
        self.root.after(self.autosave_interval, self.autosave)

    def autosave(self):
        """Perform automatic autosave"""
        try:
            if self.songs or self.pack_name_var.get().strip():
                timestamp = datetime.now().strftime("%Y%m%d_-_%H_%M_%S")
                filename = os.path.join(self.autosave_folder, f"autosave_{timestamp}.pdpack")

                # Prepare configuration
                config = {
                    'pack_name': self.pack_name_var.get(),
                    'pack_name_jp': self.pack_name_jp_var.get(),
                    'songs': self.songs
                }

                # Save file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                # Clear old files if necessary
                self.cleanup_old_autosaves()

                print(f"Autosave done: {filename}")

        except Exception as e:
            print(f"Autosave error: {str(e)}")

        finally:
            # Program the next autosave
            self.schedule_autosave()

    def cleanup_old_autosaves(self):
        """Delete old autosave files if the limit is exceeded"""
        try:
            pattern = os.path.join(self.autosave_folder, "autosave_*.pdpack")
            autosave_files = glob.glob(pattern)

            # If there are more files than the allowed limit
            if len(autosave_files) > self.max_autosave_files:
                # Sort by modification date (oldest first)
                autosave_files.sort(key=os.path.getmtime)

                # Calculate how many files to delete
                files_to_remove = len(autosave_files) - self.max_autosave_files

                # Delete the oldest files
                for i in range(files_to_remove):
                    os.remove(autosave_files[i])
                    print(f"Autosave file removed: {autosave_files[i]}")

        except Exception as e:
            print(f"Error clearing autosaves: {str(e)}")

    def set_icon(self):
        try:
            self.root.iconbitmap("icon.ico")
        except Exception as e:
            print("Error setting iconbitmap:", e)
        
    def create_widgets(self):
        # Main title
        title_label = ttk.Label(self.scrollable_frame, text="MikuMikuDB Editor", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Pack information frame
        pack_frame = ttk.LabelFrame(self.scrollable_frame, text="Song Pack Information", padding="10")
        pack_frame.pack(fill='x', padx=10, pady=5)
        
        # Pack name
        ttk.Label(pack_frame, text="Song Pack Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pack_name_var = tk.StringVar()
        ttk.Entry(pack_frame, textvariable=self.pack_name_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(pack_frame, text="Japanese name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pack_name_jp_var = tk.StringVar()
        ttk.Entry(pack_frame, textvariable=self.pack_name_jp_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        pack_frame.columnconfigure(1, weight=1)
        
        # Songs frame
        songs_frame = ttk.LabelFrame(self.scrollable_frame, text="Songs", padding="10")
        songs_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Song list
        self.songs_tree = ttk.Treeview(songs_frame, columns=('id', 'name', 'name_en'), show='headings', height=15)
        self.songs_tree.heading('id', text='PV ID')
        self.songs_tree.heading('name', text='Original Name')
        self.songs_tree.heading('name_en', text='English Name')
        
        self.songs_tree.column('id', width=80)
        self.songs_tree.column('name', width=300)
        self.songs_tree.column('name_en', width=300)
        
        scrollbar = ttk.Scrollbar(songs_frame, orient='vertical', command=self.songs_tree.yview)
        self.songs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.songs_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Song buttons
        songs_buttons = ttk.Frame(self.root)
        songs_buttons.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(songs_buttons, text="Add Song", command=self.add_song).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(songs_buttons, text="Edit Song", command=self.edit_song).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(songs_buttons, text="Delete Song", command=self.delete_song).pack(side=tk.LEFT, padx=(0, 5))
        
        # Main buttons
        main_buttons = ttk.Frame(self.root)
        main_buttons.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(main_buttons, text="Generate File", command=self.generate_file).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="Import mod_pv_db.txt", command=self.import_mod_pv_db).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="Load Configuration", command=self.load_config).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="Load Autosave", command=self.load_autosave).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="Save Configuration", command=self.save_config).pack(side=tk.RIGHT, padx=(10, 0))
        
    def update_songs_display(self):
        for item in self.songs_tree.get_children():
            self.songs_tree.delete(item)
        
        for song in self.songs:
            self.songs_tree.insert('', 'end', values=(
                song.get('pv_id', ''),
                song.get('song_name', ''),
                song.get('song_name_en', '')
            ))
    
    def add_song(self):
        dialog = SongConfigDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.songs.append(dialog.result)
            self.update_songs_display()
    
    def edit_song(self):
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a song to edit")
            return
    
        # Get the index of the selected song
        item = selection[0]
        index = self.songs_tree.index(item)
    
        # Pass the existing data to the dialog so it is pre-filled
        dialog = SongConfigDialog(self.root, self.songs[index])
        self.root.wait_window(dialog.dialog)
    
        # If the user made changes and clicked Accept, replace the entry in self.songs
        if dialog.result:
            self.songs[index] = dialog.result
            self.update_songs_display()
    
    def delete_song(self):
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a song to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this song?"):
            item = selection[0]
            index = self.songs_tree.index(item)
            del self.songs[index]
            self.update_songs_display()
    
    def generate_file(self):
        if not self.pack_name_var.get().strip():
            messagebox.showerror("Error", "Enter the Song Pack name")
            return

        if not self.songs:
            messagebox.showerror("Error", "Add at least one song")
            return

        for song in self.songs:
            if not song.get('performers') or len(song['performers']) < 1:
                messagebox.showerror("Error", f"Song PV {song.get('pv_id')} must have at least 1 performer")
                return

        # Generate file content
        content = self.generate_file_content()

        # Save file
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="mod_pv_db.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"File generated successfully: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
    
    def generate_file_content(self):
        content = []

        # Header
        content.append("# Generated by MikuMikuDB Editor")
        content.append("# Created by NyxC")
        content.append("")

        content.append(f"#" + "-" * 30)
        pack_name_jp = self.pack_name_jp_var.get().strip() or self.pack_name_var.get().strip()
        content.append(f"# {self.pack_name_var.get()} Additional Charts")
        content.append("#")

        # Song list
        for song in self.songs:
            song_line = f"# pv_{song['pv_id']}\t{song['song_name']}"
            if song['song_name_en']:
                song_line += f" | {song['song_name_en']}"
            content.append(song_line)

        content.append("#" + "-" * 30)
        content.append("")

        # Generate each song
        for i, song in enumerate(self.songs):
            if i > 0:
                content.append("")  # Empty line between songs

            pv_id = song['pv_id']

            # Audio variants (if any)
            if song.get('audio_variants'):
                # Original song variant (index 0)
                content.extend([
                    f"pv_{pv_id}.another_song.0.name={song['song_name']}",
                    f"pv_{pv_id}.another_song.0.name_en={song['song_name_en']}",
                    f"pv_{pv_id}.another_song.0.name_reading={song['song_name_reading']}",
                ])
                # vocal_chara_num for variant 0
                content.append(f"pv_{pv_id}.another_song.0.vocal_chara_num={song['performers'][0]}")

                # Additional variants (indices 1..N)
                for j, variant in enumerate(song['audio_variants'], 1):
                    # Fix: Use .get() with fallback for name_reading
                    name_reading = variant.get('name_reading', variant.get('name', ''))

                    content.extend([
                        f"pv_{pv_id}.another_song.{j}.name={variant['name']}",
                        f"pv_{pv_id}.another_song.{j}.name_en={variant['name_en']}",
                        f"pv_{pv_id}.another_song.{j}.name_reading={name_reading}",
                    ])

                    # vocal_chara_num: first performer of this variant
                    variant_performer = variant.get('performers', [song['performers'][0]])[0]
                    content.append(f"pv_{pv_id}.another_song.{j}.vocal_chara_num={variant_performer}")

                    # File name
                    suffix = variant.get('file_suffix', '').strip()
                    if not suffix:
                        suffix = str(j)
                    content.append(f"pv_{pv_id}.another_song.{j}.song_file_name=rom/sound/song/pv_{pv_id}_{suffix}.ogg")

                    # vocal_disp_name and vocal_disp_name_en if provided
                    if variant.get('vocal_disp', ''):
                        content.append(f"pv_{pv_id}.another_song.{j}.vocal_disp_name={variant['vocal_disp']}")
                    if variant.get('vocal_disp_en', ''):
                        content.append(f"pv_{pv_id}.another_song.{j}.vocal_disp_name_en={variant['vocal_disp_en']}")

                # Total length (original + additional)
                content.append(f"pv_{pv_id}.another_song.length={len(song['audio_variants']) + 1}")

            # Basic song info
            content.extend([
                f"pv_{pv_id}.bpm={song['bpm']}",
                f"pv_{pv_id}.chainslide_failure_name=slide_ng03",
                f"pv_{pv_id}.chainslide_first_name=slide_long02a",
                f"pv_{pv_id}.chainslide_sub_name=slide_button08",
                f"pv_{pv_id}.chainslide_success_name=slide_ok03",
                f"pv_{pv_id}.date={song['date']}"
            ])

            # Difficulties
            difficulties = song.get('difficulties', {})

            # Easy
            if 'easy' in difficulties:
                content.extend([
                    f"pv_{pv_id}.difficulty.easy.0.edition=0",
                    f"pv_{pv_id}.difficulty.easy.0.level={difficulties['easy']['level']}",
                    f"pv_{pv_id}.difficulty.easy.0.level_sortindex={difficulties['easy']['level_sort_index']}",
                    f"pv_{pv_id}.difficulty.easy.0.script_filename=rom/script/pv_{pv_id}_easy.dsc",
                    f"pv_{pv_id}.difficulty.easy.0.scriptformat=0x15122517",
                    f"pv_{pv_id}.difficulty.easy.0.version=1",
                    f"pv_{pv_id}.difficulty.easy.length=1"
                ])
            else:
                content.append(f"pv_{pv_id}.difficulty.easy.length=0")

            # Extreme
            extreme_count = 0
            if 'extreme' in difficulties:
                content.extend([
                    f"pv_{pv_id}.difficulty.extreme.0.edition=0",
                    f"pv_{pv_id}.difficulty.extreme.0.level={difficulties['extreme']['level']}",
                    f"pv_{pv_id}.difficulty.extreme.0.level_sortindex={difficulties['extreme']['level_sort_index']}",
                    f"pv_{pv_id}.difficulty.extreme.0.script_filename=rom/script/pv_{pv_id}_extreme.dsc",
                    f"pv_{pv_id}.difficulty.extreme.0.scriptformat=0x15122517",
                    f"pv_{pv_id}.difficulty.extreme.0.version=1"
                ])
                extreme_count += 1

            if 'extreme_extra' in difficulties:
                content.extend([
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.attribute.extra=1",
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.attribute.original=0",
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.edition=1",
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.level={difficulties['extreme_extra']['level']}",
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.level_sortindex={difficulties['extreme_extra']['level_sort_index']}",
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.script_filename=rom/script/pv_{pv_id}_extreme_{extreme_count}.dsc",
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.scriptformat=0x15122517",
                    f"pv_{pv_id}.difficulty.extreme.{extreme_count}.version=1"
                ])
                extreme_count += 1

            content.append(f"pv_{pv_id}.difficulty.extreme.length={extreme_count}")

            # Hard
            if 'hard' in difficulties:
                content.extend([
                    f"pv_{pv_id}.difficulty.hard.0.edition=0",
                    f"pv_{pv_id}.difficulty.hard.0.level={difficulties['hard']['level']}",
                    f"pv_{pv_id}.difficulty.hard.0.level_sortindex={difficulties['hard']['level_sort_index']}",
                    f"pv_{pv_id}.difficulty.hard.0.script_filename=rom/script/pv_{pv_id}_hard.dsc",
                    f"pv_{pv_id}.difficulty.hard.0.scriptformat=0x15122517",
                    f"pv_{pv_id}.difficulty.hard.0.version=1",
                    f"pv_{pv_id}.difficulty.hard.length=1"
                ])
            else:
                content.append(f"pv_{pv_id}.difficulty.hard.length=0")

            # Normal
            if 'normal' in difficulties:
                content.extend([
                    f"pv_{pv_id}.difficulty.normal.0.edition=0",
                    f"pv_{pv_id}.difficulty.normal.0.level={difficulties['normal']['level']}",
                    f"pv_{pv_id}.difficulty.normal.0.level_sortindex={difficulties['normal']['level_sort_index']}",
                    f"pv_{pv_id}.difficulty.normal.0.script_filename=rom/script/pv_{pv_id}_normal.dsc",
                    f"pv_{pv_id}.difficulty.normal.0.scriptformat=0x15122517",
                    f"pv_{pv_id}.difficulty.normal.0.version=1",
                    f"pv_{pv_id}.difficulty.normal.length=1"
                ])
            else:
                content.append(f"pv_{pv_id}.difficulty.normal.length=0")

            # Standard settings
            content.extend([
                f"pv_{pv_id}.hiddentiming=0.3",
                f"pv_{pv_id}.high_speedrate=4",
                f"pv_{pv_id}.movie_filename=rom/movie/pv_{pv_id}.mp4",
                f"pv_{pv_id}.movie_pvtype=ONLY",
                f"pv_{pv_id}.movie_surface=FRONT",
                f"pv_{pv_id}.pack=2"
            ])

            # Performers
            performers = song.get('performers', ['MIK'])
            for j, performer in enumerate(performers):
                content.extend([
                    f"pv_{pv_id}.performer.{j}.chara={performer}",
                    f"pv_{pv_id}.performer.{j}.pv_costume=1",
                    f"pv_{pv_id}.performer.{j}.type=VOCAL"
                ])
            content.append(f"pv_{pv_id}.performer.num={len(performers)}")

            # Sabi settings
            content.extend([
                f"pv_{pv_id}.sabi.playtime={song['sabi_play']}",
                f"pv_{pv_id}.sabi.start_time={song['sabi_start']}"
            ])

            # Standard sound settings
            content.extend([
                f"pv_{pv_id}.se_name=01_button1",
                f"pv_{pv_id}.slide_name=slide_se13",
                f"pv_{pv_id}.slidertouch_name=slide_windchime",
                f"pv_{pv_id}.song_filename=rom/sound/song/pv_{pv_id}.ogg"
            ])

            # Song names
            content.extend([
                f"pv_{pv_id}.song_name={song['song_name']}",
                f"pv_{pv_id}.song_name_en={song['song_name_en']}"
            ])
            content.extend([
                f"pv_{pv_id}.song_name_reading={song['song_name_reading']}",
            ])

            # Songinfo - Original versions first
            songinfo = song.get('songinfo', {})
            songinfo_fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']

            # First pass: Add all original songinfo fields
            for field in songinfo_fields:
                if field in songinfo and songinfo[field]:
                    content.append(f"pv_{pv_id}.songinfo.{field}={songinfo[field]}")

            # Second pass: Add all English songinfo fields
            for field in songinfo_fields:
                en_field = f"{field}_en"
                if en_field in songinfo and songinfo[en_field]:
                    content.append(f"pv_{pv_id}.songinfo_en.{field}={songinfo[en_field]}")

            content.append(f"pv_{pv_id}.sudden_timing=0.6")

        return '\n'.join(content)
    
    def import_mod_pv_db(self):
        """Import an existing mod_pv_db.txt file"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Project Diva DB files", "*.txt"),
                ("All files", "*.*")
            ],
            title="Import mod_pv_db.txt file"
        )
    
        if not filename:
            return
    
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
    
            # Parse the file content
            songs = self.parse_mod_pv_db_content(content)
            
            if not songs:
                messagebox.showwarning("Warning", "No valid songs found in the file")
                return
    
            # Ask user if they want to replace current songs or add to them
            if self.songs:
                result = messagebox.askyesnocancel(
                    "Import Options",
                    f"Found {len(songs)} songs in the file.\n\n"
                    "Yes: Replace current songs\n"
                    "No: Add to current songs\n"
                    "Cancel: Cancel import"
                )
                
                if result is None:  # Cancel
                    return
                elif result:  # Yes - Replace
                    self.songs = songs
                else:  # No - Add
                    self.songs.extend(songs)
            else:
                self.songs = songs
    
            self.update_songs_display()
            messagebox.showinfo("Success", f"Successfully imported {len(songs)} songs from mod_pv_db.txt")
    
        except Exception as e:
            messagebox.showerror("Error", f"Error importing file: {str(e)}")
    
    def parse_mod_pv_db_content(self, content):
        """Parse mod_pv_db.txt content and extract song data"""
        songs = []
        lines = content.split('\n')
        
        # Find all PV IDs in the file
        pv_ids = set()
        for line in lines:
            if line.strip() and not line.strip().startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                if key.startswith('pv_') and '.' in key:
                    pv_id = key.split('.')[0].replace('pv_', '')
                    pv_ids.add(pv_id)
        
        # Parse each song
        for pv_id in sorted(pv_ids, key=lambda x: int(x) if x.isdigit() else 0):
            song_data = self.parse_single_song(lines, pv_id)
            if song_data:
                songs.append(song_data)
        
        return songs
    
    def parse_single_song(self, lines, pv_id):
        """Parse a single song's data from the file lines"""
        song = {
            'pv_id': pv_id,
            'song_name': '',
            'song_name_en': '',
            'song_name_reading': '',
            'bpm': 120,
            'date': '20250101',
            'difficulties': {},
            'performers': [],
            'sabi_play': '30.0',
            'sabi_start': '30000',
            'songinfo': {},
            'audio_variants': []
        }
        
        # Create a dictionary for quick lookup
        data_dict = {}
        for line in lines:
            if line.strip() and not line.strip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key.startswith(f'pv_{pv_id}.'):
                    data_dict[key] = value
        
        # Basic song info
        song['song_name'] = data_dict.get(f'pv_{pv_id}.song_name', f'Song {pv_id}')
        song['song_name_en'] = data_dict.get(f'pv_{pv_id}.song_name_en', song['song_name'])
        song['song_name_reading'] = data_dict.get(f'pv_{pv_id}.song_name_reading', song['song_name'])
        
        # BPM and date
        song['bpm'] = int(data_dict.get(f'pv_{pv_id}.bpm', 120))
        song['date'] = data_dict.get(f'pv_{pv_id}.date', '20250101')
        
        # Sabi settings
        song['sabi_play'] = data_dict.get(f'pv_{pv_id}.sabi.playtime', '30.0')
        sabi_start = data_dict.get(f'pv_{pv_id}.sabi.start_time', '30000')
        # Convert milliseconds to seconds if needed
        try:
            if float(sabi_start) > 1000:
                song['sabi_start'] = str(float(sabi_start) / 1000)
            else:
                song['sabi_start'] = sabi_start
        except:
            song['sabi_start'] = '30.0'
        
        # Parse difficulties
        difficulties = ['easy', 'normal', 'hard', 'extreme']
        for diff in difficulties:
            diff_length = data_dict.get(f'pv_{pv_id}.difficulty.{diff}.length', '0')
            if diff_length != '0':
                level = data_dict.get(f'pv_{pv_id}.difficulty.{diff}.0.level', 'PV_LV_05_0')
                level_sort = data_dict.get(f'pv_{pv_id}.difficulty.{diff}.0.level_sortindex', '50')
                
                song['difficulties'][diff] = {
                    'level': level,
                    'level_sort_index': int(level_sort)
                }
        
        # Check for extreme extra
        extreme_length = int(data_dict.get(f'pv_{pv_id}.difficulty.extreme.length', '0'))
        if extreme_length > 1:
            # There's an extra extreme chart (index 1)
            level = data_dict.get(f'pv_{pv_id}.difficulty.extreme.1.level', 'PV_LV_09_0')
            level_sort = data_dict.get(f'pv_{pv_id}.difficulty.extreme.1.level_sortindex', '50')
            
            song['difficulties']['extreme_extra'] = {
                'level': level,
                'level_sort_index': int(level_sort)
            }
        
        # Parse performers
        performer_num = int(data_dict.get(f'pv_{pv_id}.performer.num', '1'))
        for i in range(performer_num):
            chara = data_dict.get(f'pv_{pv_id}.performer.{i}.chara', 'MIK')
            song['performers'].append(chara)
        
        # Parse songinfo
        songinfo_fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']
        for field in songinfo_fields:
            value = data_dict.get(f'pv_{pv_id}.songinfo.{field}', '')
            if value:
                song['songinfo'][field] = value
            
            # English version
            en_value = data_dict.get(f'pv_{pv_id}.songinfo_en.{field}', '')
            if en_value:
                song['songinfo'][f'{field}_en'] = en_value
        
        # Parse audio variants
        another_song_length = int(data_dict.get(f'pv_{pv_id}.another_song.length', '0'))
        if another_song_length > 1:  # More than just the original (index 0)
            for i in range(1, another_song_length):  # Start from 1, skip original
                variant = {
                    'name': data_dict.get(f'pv_{pv_id}.another_song.{i}.name', f'Variant {i}'),
                    'name_en': data_dict.get(f'pv_{pv_id}.another_song.{i}.name_en', f'Variant {i}'),
                    'name_reading': data_dict.get(f'pv_{pv_id}.another_song.{i}.name_reading', f'Variant {i}'),
                    'vocal_disp': data_dict.get(f'pv_{pv_id}.another_song.{i}.vocal_disp_name', ''),
                    'vocal_disp_en': data_dict.get(f'pv_{pv_id}.another_song.{i}.vocal_disp_name_en', '')
                }
                song['audio_variants'].append(variant)
        
        return song
    
    def save_config(self):
        """Save configuration with custom encryption"""
        if not self.songs:
            messagebox.showwarning("Warning", "No songs to save")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdpack",
            filetypes=[
                ("Project Diva Pack files", "*.pdpack")
            ],
            initialfile="config.pdpack"
        )

        if filename:
            try:
                config = {
                    'pack_name': self.pack_name_var.get(),
                    'pack_name_jp': self.pack_name_jp_var.get(),
                    'songs': self.songs,
                    'version': '2.0',  # Version identifier for encrypted format
                    'created_by': 'MikuMikuDB Editor',
                    'encryption': True
                }

                # Initialize encryption handler
                encryptor = CustomEncryption()

                # Encrypt the data
                encrypted_data = encryptor.encrypt_data(config)

                # Write encrypted data to file
                with open(filename, 'wb') as f:
                    f.write(encrypted_data)

                messagebox.showinfo("Success", f"Encrypted configuration saved: {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Error saving encrypted configuration: {str(e)}")

    def load_config(self):
        """Load configuration with custom decryption"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Project Diva Pack files", "*.pdpack")
            ]
        )

        if filename:
            try:
                # Read file content
                with open(filename, 'rb') as f:
                    file_content = f.read()

                # Try to determine if it's encrypted or legacy JSON
                if file_content.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                    # New encrypted format
                    encryptor = CustomEncryption()
                    config = encryptor.decrypt_data(file_content)

                elif file_content.startswith(b'{'):
                    # Legacy JSON format
                    json_string = file_content.decode('utf-8')
                    config = json.loads(json_string)

                    # Show migration prompt
                    result = messagebox.askyesno(
                        "Legacy Format Detected",
                        "This file uses the old unencrypted format.\n\n"
                        "Would you like to convert it to the new encrypted format?\n"
                        "(The original file will be backed up)"
                    )

                    if result:
                        self._migrate_legacy_file(filename, config)

                else:
                    raise Exception("Unrecognized file format")

                # Load configuration data
                self.pack_name_var.set(config.get('pack_name', ''))
                self.pack_name_jp_var.set(config.get('pack_name_jp', ''))
                self.songs = config.get('songs', [])

                self.update_songs_display()

                encryption_status = "encrypted" if config.get('encryption', False) else "unencrypted"
                messagebox.showinfo("Success", f"Configuration loaded ({encryption_status}): {os.path.basename(filename)}")

            except Exception as e:
                messagebox.showerror("Error", f"Error loading configuration: {str(e)}")

    def _migrate_legacy_file(self, filename, config):
        """Migrate legacy JSON file to encrypted format"""
        try:
            # Create backup
            backup_filename = filename + '.backup'
            if os.path.exists(filename):
                import shutil
                shutil.copy2(filename, backup_filename)

            # Update config for encrypted format
            config.update({
                'version': '2.0',
                'created_by': 'MikuMikuDB Editor',
                'encryption': True,
                'migrated_from': 'legacy_json'
            })

            # Encrypt and save
            encryptor = CustomEncryption()
            encrypted_data = encryptor.encrypt_data(config)

            with open(filename, 'wb') as f:
                f.write(encrypted_data)

            messagebox.showinfo(
                "Migration Complete",
                f"File successfully converted to encrypted format.\n"
                f"Backup saved as: {os.path.basename(backup_filename)}"
            )

        except Exception as e:
            messagebox.showerror("Migration Error", f"Failed to migrate file: {str(e)}")

    def create_autosave(self):
        """Create encrypted autosave file"""
        if not self.songs:
            return  # No data to save

        try:
            # Ensure autosave directory exists
            os.makedirs(self.autosave_folder, exist_ok=True)

            # Generate timestamp filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.autosave_folder, f"autosave_{timestamp}.pdpack")

            config = {
                'pack_name': self.pack_name_var.get(),
                'pack_name_jp': self.pack_name_jp_var.get(),
                'songs': self.songs,
                'version': '2.0',
                'created_by': 'MikuMikuDB Editor (Autosave)',
                'encryption': True,
                'autosave': True,
                'timestamp': timestamp
            }

            # Encrypt and save autosave
            encryptor = CustomEncryption()
            encrypted_data = encryptor.encrypt_data(config)

            with open(filename, 'wb') as f:
                f.write(encrypted_data)

            # Clean up old autosave files (keep only last 10)
            self._cleanup_autosave_files()

        except Exception as e:
            print(f"Autosave failed: {str(e)}")  # Silent fail for autosave

    def _cleanup_autosave_files(self):
        """Keep only the 10 most recent autosave files"""
        try:
            import glob
            pattern = os.path.join(self.autosave_folder, "autosave_*.pdpack")
            autosave_files = glob.glob(pattern)

            if len(autosave_files) > 10:
                # Sort by modification time, oldest first
                autosave_files.sort(key=os.path.getmtime)

                # Remove oldest files
                for old_file in autosave_files[:-10]:
                    os.remove(old_file)

        except Exception as e:
            print(f"Autosave cleanup failed: {str(e)}")

    def load_autosave(self):
        """Load an encrypted autosave file"""
        if not os.path.exists(self.autosave_folder):
            messagebox.showinfo("Information", "No autosave files available")
            return

        # Search for autosave files
        import glob
        pattern = os.path.join(self.autosave_folder, "autosave_*.pdpack")
        autosave_files = glob.glob(pattern)

        if not autosave_files:
            messagebox.showinfo("Information", "No autosave files available")
            return

        # Show selection dialog
        autosave_files.sort(key=os.path.getmtime, reverse=True)  # Most recent first

        # Create selection window
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Encrypted Autosave")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select encrypted autosave file:", font=('Arial', 12, 'bold')).pack(pady=10)

        # File list
        listbox = tk.Listbox(dialog, height=15)
        listbox.pack(fill='both', expand=True, padx=10, pady=5)

        for file in autosave_files:
            filename = os.path.basename(file)
            # Extract timestamp from filename
            try:
                timestamp_part = filename.replace('autosave_', '').replace('.pdpack', '')
                year = timestamp_part[:4]
                month = timestamp_part[4:6]
                day = timestamp_part[6:8]
                hour = timestamp_part[9:11]
                minute = timestamp_part[12:14]
                second = timestamp_part[15:17]

                display_name = f"{day}/{month}/{year} {hour}:{minute}:{second} - {filename} [ENCRYPTED]"
            except:
                display_name = f"{filename} [ENCRYPTED]"

            listbox.insert(tk.END, display_name)

        def load_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Select an autosave file")
                return

            selected_file = autosave_files[selection[0]]
            dialog.destroy()

            # Load the selected encrypted file
            try:
                with open(selected_file, 'rb') as f:
                    encrypted_data = f.read()

                # Decrypt the data
                encryptor = CustomEncryption()
                config = encryptor.decrypt_data(encrypted_data)

                self.pack_name_var.set(config.get('pack_name', ''))
                self.pack_name_jp_var.set(config.get('pack_name_jp', ''))
                self.songs = config.get('songs', [])

                self.update_songs_display()
                messagebox.showinfo("Success", f"Encrypted autosave loaded: {os.path.basename(selected_file)}")

            except Exception as e:
                messagebox.showerror("Error", f"Error loading encrypted autosave: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Load", command=load_selected).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def setup_drag_drop(self):
        """Setup drag and drop functionality for the main window"""
        if not DRAG_DROP_AVAILABLE:
            print("tkinterdnd2 not available. Drag and drop functionality disabled.")
            print("Install with: pip install tkinterdnd2")
            self.setup_file_selection_alternative()
            return
        
        try:
            # Enable drag and drop for the main window
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_file_drop)
            
            # Add visual feedback to scrollable frame instead of root
            self.drag_drop_label = ttk.Label(
                self.scrollable_frame, 
                text="📁 Drag & Drop .pdpack or .txt files here",
                font=('Arial', 10, 'italic'),
                foreground='gray'
            )
            self.drag_drop_label.pack(pady=5)
            
        except Exception as e:
            print(f"Error setting up drag and drop: {e}")
            self.setup_file_selection_alternative()

    def setup_file_selection_alternative(self):
        """Setup alternative file selection when drag and drop is not available"""
        try:
            # Create a frame for file selection in scrollable frame
            file_frame = ttk.LabelFrame(self.scrollable_frame, text="File Import", padding=10)
            file_frame.pack(fill='x', padx=10, pady=5)
            
            # Info label
            info_label = ttk.Label(
                file_frame,
                text="📁 Import Configuration or Database Files\n"
                     "Supported: .pdpack (Configuration) | .txt (Database)",
                font=('Arial', 10),
                justify='center'
            )
            info_label.pack(pady=5)
            
            # Buttons frame
            buttons_frame = ttk.Frame(file_frame)
            buttons_frame.pack(pady=10)
            
            # Import configuration button
            import_config_btn = ttk.Button(
                buttons_frame,
                text="Import Configuration (.pdpack)",
                command=self.import_configuration_file
            )
            import_config_btn.pack(side='left', padx=5)
            
            # Import database button
            import_db_btn = ttk.Button(
                buttons_frame,
                text="Import Database (.txt)",
                command=self.import_database_file
            )
            import_db_btn.pack(side='left', padx=5)
            
        except Exception as e:
            print(f"Error setting up file selection alternative: {e}")

    def import_configuration_file(self):
        """Import a .pdpack configuration file"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Select Configuration File",
                filetypes=[
                    ("PDPack files", "*.pdpack"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.process_dropped_file(file_path)
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error importing configuration file: {str(e)}")
    
    def import_database_file(self):
        """Import a .txt database file"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Select Database File",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.process_dropped_file(file_path)
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error importing database file: {str(e)}")
    
    def on_file_drop(self, event):
        """Handle dropped files"""
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # Process only the first file if multiple are dropped
        file_path = files[0]
        
        # Validate and process the file
        self.process_dropped_file(file_path)
    
    def process_dropped_file(self, file_path):
        """Process a dropped file and determine its type"""
        try:
            if not os.path.isfile(file_path):
                messagebox.showerror("Error", "Invalid file path")
                return
            
            file_extension = os.path.splitext(file_path)[1].lower()
            filename = os.path.basename(file_path)
            
            # Show processing dialog
            processing_dialog = self.show_processing_dialog(f"Processing {filename}...")
            
            try:
                if file_extension == '.pdpack':
                    success = self.load_pdpack_file(file_path)
                    file_type = "Configuration"
                    
                elif file_extension == '.txt':
                    success = self.load_txt_file(file_path)
                    file_type = "Database"
                    
                else:
                    processing_dialog.destroy()
                    messagebox.showerror(
                        "Unsupported File Type", 
                        f"File type '{file_extension}' is not supported.\n\n"
                        "Supported formats:\n"
                        "• .pdpack (Configuration files)\n"
                        "• .txt (Database files)"
                    )
                    return
                
                processing_dialog.destroy()
                
                if success:
                    messagebox.showinfo(
                        "File Loaded Successfully", 
                        f"{file_type} file loaded: {filename}"
                    )
                
            except Exception as e:
                processing_dialog.destroy()
                messagebox.showerror("Processing Error", f"Error processing file: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error handling dropped file: {str(e)}")
    
    def show_processing_dialog(self, message):
        """Show a processing dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Processing...")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (100 // 2)
        dialog.geometry(f"300x100+{x}+{y}")
        
        ttk.Label(dialog, text=message, font=('Arial', 10)).pack(expand=True)
        
        # Update to show the dialog
        dialog.update()
        
        return dialog
    
    def load_pdpack_file(self, file_path):
        """Load and validate a .pdpack file"""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Validate and decrypt/parse
            if file_content.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                # Encrypted format
                encryptor = CustomEncryption()
                config = encryptor.decrypt_data(file_content)
                file_format = "encrypted"
                
            elif file_content.startswith(b'{'):
                # Legacy JSON format
                json_string = file_content.decode('utf-8')
                config = json.loads(json_string)
                file_format = "legacy JSON"
                
            else:
                raise Exception("Invalid .pdpack file format")
            
            # Validate configuration structure
            if not self.validate_pdpack_config(config):
                raise Exception("Invalid configuration structure")
            
            # Ask user about loading
            result = messagebox.askyesnocancel(
                "Load Configuration",
                f"Found valid .pdpack file ({file_format} format)\n"
                f"Songs: {len(config.get('songs', []))}\n"
                f"Pack Name: {config.get('pack_name', 'Unknown')}\n\n"
                "Yes: Replace current data\n"
                "No: Merge with current data\n"
                "Cancel: Don't load"
            )
            
            if result is None:  # Cancel
                return False
            elif result:  # Yes - Replace
                self.pack_name_var.set(config.get('pack_name', ''))
                self.pack_name_jp_var.set(config.get('pack_name_jp', ''))
                self.songs = config.get('songs', [])
            else:  # No - Merge
                if config.get('songs'):
                    self.songs.extend(config.get('songs', []))
            
            self.update_songs_display()
            return True
            
        except Exception as e:
            raise Exception(f"Failed to load .pdpack file: {str(e)}")
    
    def load_txt_file(self, file_path):
        """Load and validate a .txt database file"""
        try:
            # Read and validate file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate mod_pv_db format
            if not self.validate_txt_format(content):
                raise Exception("Invalid mod_pv_db.txt format")
            
            # Parse the file content
            songs = self.parse_mod_pv_db_content(content)
            
            if not songs:
                raise Exception("No valid songs found in the database file")
            
            # Ask user about loading
            result = messagebox.askyesnocancel(
                "Import Database File",
                f"Found valid mod_pv_db.txt file\n"
                f"Songs detected: {len(songs)}\n\n"
                "Yes: Replace current songs\n"
                "No: Add to current songs\n"
                "Cancel: Don't import"
            )
            
            if result is None:  # Cancel
                return False
            elif result:  # Yes - Replace
                self.songs = songs
            else:  # No - Add
                self.songs.extend(songs)
            
            self.update_songs_display()
            return True
            
        except Exception as e:
            raise Exception(f"Failed to load .txt file: {str(e)}")
    
    def validate_pdpack_config(self, config):
        """Validate .pdpack configuration structure"""
        try:
            # Check if it's a dictionary
            if not isinstance(config, dict):
                return False
            
            # Check required fields
            if 'songs' not in config:
                return False
            
            # Validate songs structure
            songs = config['songs']
            if not isinstance(songs, list):
                return False
            
            # Validate each song (basic validation)
            for song in songs:
                if not isinstance(song, dict):
                    return False
                
                # Check required song fields
                required_fields = ['pv_id', 'song_name', 'bpm']
                for field in required_fields:
                    if field not in song:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def validate_txt_format(self, content):
        """Validate mod_pv_db.txt format"""
        try:
            lines = content.strip().split('\n')
            
            # Check for at least some lines
            if len(lines) < 5:
                return False
            
            # Look for typical mod_pv_db patterns
            has_pv_entries = False
            has_valid_structure = False
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Check for key=value format
                if '=' not in line:
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                
                # Check for pv_ entries
                if key.startswith('pv_') and '.' in key:
                    has_pv_entries = True
                    
                    # Check for typical structure
                    if any(pattern in key for pattern in [
                        '.song_name', '.bpm', '.difficulty', '.performer'
                    ]):
                        has_valid_structure = True
            
            return has_pv_entries and has_valid_structure
            
        except Exception:
            return False
    
    # File type detection utility
    def detect_file_type(self, file_path):
        """Detect and validate file type"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdpack':
                # Read first few bytes to determine format
                with open(file_path, 'rb') as f:
                    header = f.read(50)
                
                if header.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                    return 'pdpack_encrypted'
                elif header.startswith(b'{'):
                    return 'pdpack_json'
                else:
                    return 'pdpack_invalid'
                    
            elif file_extension == '.txt':
                # Quick validation of txt format
                with open(file_path, 'r', encoding='utf-8') as f:
                    sample = f.read(1000)  # Read first 1000 chars
                
                if 'pv_' in sample and '=' in sample:
                    return 'txt_modpvdb'
                else:
                    return 'txt_invalid'
            
            return 'unsupported'
            
        except Exception:
            return 'error'
    
    # Enhanced file validation with detailed feedback
    def get_file_info(self, file_path):
        """Get detailed information about a file"""
        try:
            file_type = self.detect_file_type(file_path)
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            info = {
                'filename': filename,
                'size': file_size,
                'type': file_type,
                'valid': False,
                'details': {}
            }
            
            if file_type == 'pdpack_encrypted':
                # Try to decrypt and get info
                try:
                    with open(file_path, 'rb') as f:
                        encrypted_data = f.read()
                    
                    encryptor = CustomEncryption()
                    config = encryptor.decrypt_data(encrypted_data)
                    
                    info['valid'] = True
                    info['details'] = {
                        'format': 'Encrypted Configuration',
                        'songs': len(config.get('songs', [])),
                        'pack_name': config.get('pack_name', 'Unknown'),
                        'version': config.get('version', '1.0')
                    }
                except Exception as e:
                    info['details']['error'] = str(e)
                    
            elif file_type == 'pdpack_json':
                # Parse JSON and get info
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    info['valid'] = True
                    info['details'] = {
                        'format': 'Legacy JSON Configuration',
                        'songs': len(config.get('songs', [])),
                        'pack_name': config.get('pack_name', 'Unknown'),
                        'version': config.get('version', '1.0')
                    }
                except Exception as e:
                    info['details']['error'] = str(e)
                    
            elif file_type == 'txt_modpvdb':
                # Parse txt and get info
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count PV entries
                    pv_ids = set()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip() and not line.strip().startswith('#') and '=' in line:
                            key = line.split('=')[0].strip()
                            if key.startswith('pv_') and '.' in key:
                                pv_id = key.split('.')[0].replace('pv_', '')
                                pv_ids.add(pv_id)
                    
                    info['valid'] = True
                    info['details'] = {
                        'format': 'mod_pv_db.txt Database',
                        'songs': len(pv_ids),
                        'lines': len(lines)
                    }
                except Exception as e:
                    info['details']['error'] = str(e)
            
            return info
            
        except Exception as e:
            return {
                'filename': os.path.basename(file_path),
                'size': 0,
                'type': 'error',
                'valid': False,
                'details': {'error': str(e)}
            }
    
    # Enhanced drag visual feedback
    def setup_drag_visual_feedback(self):
        """Setup visual feedback for drag and drop operations"""
        try:
            # Create a frame for drag and drop area in scrollable frame
            self.drag_drop_frame = ttk.LabelFrame(self.scrollable_frame, text="File Import", padding=10)
            self.drag_drop_frame.pack(fill='x', padx=10, pady=5)
            
            # Main drag and drop label
            self.drag_drop_label = ttk.Label(
                self.drag_drop_frame,
                text="📁 Drag & Drop files here\n"
                     "Supported: .pdpack (Configuration) | .txt (Database)",
                font=('Arial', 10),
                justify='center',
                foreground='gray'
            )
            self.drag_drop_label.pack(expand=True, fill='both', pady=10)
            
            # Status label for feedback
            self.drag_status_label = ttk.Label(
                self.drag_drop_frame,
                text="Ready to receive files...",
                font=('Arial', 8),
                foreground='blue'
            )
            self.drag_status_label.pack()
            
            # Bind drag events for visual feedback
            if DRAG_DROP_AVAILABLE:
                self.root.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.root.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
        except Exception as e:
            print(f"Could not setup visual feedback: {e}")
    
    def on_drag_enter(self, event):
        """Visual feedback when drag enters window"""
        try:
            self.drag_drop_label.configure(foreground='green')
            self.drag_status_label.configure(text="Drop file to import...", foreground='green')
        except:
            pass
        
    def on_drag_leave(self, event):
        """Visual feedback when drag leaves window"""
        try:
            self.drag_drop_label.configure(foreground='gray')
            self.drag_status_label.configure(text="Ready to receive files...", foreground='blue')
        except:
            pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProjectDivaModEditor()
    app.run()
