# ！/usr/bin/env python3
# - * - コーディング：UTF-8-* -
"""
Project Diva mod_pv_db.txtジェネレーターGUI
"Project Diva の楽曲パック用 mod_pv_db.txt ファイルをGUIインターフェースで生成します
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
    """.pdpackファイル用のカスタム暗号化ハンドラー"""
    
    def __init__(self, password="MikuMikuDB_NyxC_2025"):
        self.password = password.encode()
        self.salt = b'mikumiku_salt_v1'  # 一貫性のために塩を固定しました
    
    def _derive_key(self):
        """パスワードから暗号化キーを導き出します"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_data(self, data):
        """JSONデータを暗号化して暗号化されたバイト"""
        try:
            # データをJSON文字列に変換します
            json_string = json.dumps(data, indent=2, ensure_ascii=False)
            json_bytes = json_string.encode('utf-8')
            
            # フェルネット暗号を作成します
            key = self._derive_key()
            fernet = Fernet(key)
            
            # データを暗号化します
            encrypted_data = fernet.encrypt(json_bytes)
            
            # ファイル識別用のカスタムヘッダーを追加します
            header = b'PDPACK_ENCRYPTED_V1\n'
            return header + encrypted_data
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_bytes):
        """暗号化されたバイトをJSONデータに復号化します"""
        try:
            # カスタムヘッダーを確認してください
            if not encrypted_bytes.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                raise Exception("無効または破損した暗号化ファイル形式")
            
            # ヘッダーを取り外します
            encrypted_data = encrypted_bytes[len(b'PDPACK_ENCRYPTED_V1\n'):]
            
            # フェルネット暗号を作成します
            key = self._derive_key()
            fernet = Fernet(key)
            
            # データを復号化します
            decrypted_bytes = fernet.decrypt(encrypted_data)
            json_string = decrypted_bytes.decode('utf-8')
            
            # 解析JSON
            return json.loads(json_string)
            
        except Exception as e:
            raise Exception(f"復号化に失敗しました: {str(e)}")

class SongVariantDialog:
    def __init__(self, parent, variant_data=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("オーディオバリアントを構成する")

        window_width = 540
        window_height = 520

        # 画面の中心
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 変数
        self.name_var = tk.StringVar(value=variant_data.get('name', '') if variant_data else '')
        self.name_en_var = tk.StringVar(value=variant_data.get('name_en', '') if variant_data else '')
        self.name_reading_var = tk.StringVar(value=variant_data.get('name_reading', variant_data.get('name', '')) if variant_data else '')
        self.vocal_disp_var = tk.StringVar(value=variant_data.get('vocal_disp', '') if variant_data else '')
        self.vocal_disp_en_var = tk.StringVar(value=variant_data.get('vocal_disp_en', '') if variant_data else '')
        
        # ←ヌエボ（接尾辞Yパフォーマー）
        self.file_suffix_var = tk.StringVar(value=variant_data.get('file_suffix', '') if variant_data else '')
        self.performers = variant_data.get('performers', ['MIK']) if variant_data else ['MIK']
        
        # 利用可能な文字
        self.characters = {
            'MIK': '初音ミク',
            'RIN': '鏡音リン',
            'LEN': '鏡音レン',
            'LUK': '巡音ルカ',
            'KAI': 'カイト',
            'MEI': 'メイコ',
            'HAK': '弱音ハク',
            'NER': '亞北ネル',
            'SAK': '咲音メイコ',
            'TET': '重音テト'
        }
        
        self.create_widgets()
        
    def is_hiragana(self, text):
        """テキストにヒラガナ文字のみが含まれているかどうかを確認します（および一般的な句読点/スペース）"""
        # Hiragana Range：U+3040-U+309F
        # また、一般的な句読点、スペース、数字を許可します
        hiragana_pattern = r'^[\u3040-\u309F\s\u3000ー・。、！？\d]+$'
        return bool(re.match(hiragana_pattern, text))
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # - - タイトル
        ttk.Label(
            main_frame,
            text="オーディオバリアントを構成します",
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # ---基本フィールド（行1..5）
        fields = [
            ("バリアント名: *", self.name_var),
            ("英語名: *", self.name_en_var),
            ("バリアント読み（ひらがな）: *", self.name_reading_var),   # ←フィールドを追加しました
            ("バリアントのアーティスト: *", self.vocal_disp_var),
            ("アーティスト（英語）: *", self.vocal_disp_en_var)
        ]

        for i, (label, var) in enumerate(fields, 1):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(main_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
            
            # name_readingフィールドの検証コールバックを追加します
            if "reading" in label.lower():
                var.trace('w', self.validate_hiragana)

        # Hiraganaの検証ラベルを追加します
        self.hiragana_validation_label = ttk.Label(
            main_frame, 
            text="", 
            foreground="red",
            font=('Arial', 8)
        )
        self.hiragana_validation_label.grid(row=len(fields)+1, column=1, sticky=tk.W, padx=(10, 0))

        # ---パフォーマーセクション（基本フィールドの後）
        row_performers = len(fields) + 2  # 検証ラベルの後の無料行

        # ラベル
        ttk.Label(
            main_frame,
            text="選択されたパフォーマー："
        ).grid(row=row_performers, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))

        # 現在のパフォーマーが表示されるリストボックス
        self.performers_listbox = tk.Listbox(main_frame, height=4)
        self.performers_listbox.grid(
            row=row_performers+1, column=0, columnspan=2,
            sticky=(tk.W, tk.E), pady=(0, 5)
        )

        # 追加 /ストラップ
        perf_btn_frame = ttk.Frame(main_frame)
        perf_btn_frame.grid(row=row_performers+2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        ttk.Button(
            perf_btn_frame,
            text="追加",
            command=self.add_variant_performer
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            perf_btn_frame,
            text="取り除く",
            command=self.remove_variant_performer
        ).pack(side=tk.LEFT)

        # 文字を選択するコンボボックス
        ttk.Label(
            main_frame,
            text="文字を選択："
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

        # ---ファイルサフィックスのフィールド（パフォーマーの後）
        row_file = row_performers + 4
        ttk.Label(
            main_frame,
            text="ファイル名サフィックス： *"
        ).grid(row=row_file, column=0, sticky=tk.W, pady=2)
        ttk.Entry(
            main_frame,
            textvariable=self.file_suffix_var,
            width=40
        ).grid(row=row_file, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # ---必須フィールドに関する注意
        ttk.Label(
            main_frame,
            text="*必要なフィールド",
            font=('Arial', 8),
            foreground="gray"
        ).grid(row=row_file+1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # ---ボタンを受け入れ /キャンセルします
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row_file+2, column=0, columnspan=2, pady=(20, 0))
        ttk.Button(button_frame, text="受け入れる", command=self.accept).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="キャンセル", command=self.cancel).pack(side=tk.LEFT)

        # 拡張を構成します
        main_frame.columnconfigure(1, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

        # 最初のパフォーマーリストを表示します
        self.update_variant_performers_display()
        
        # 初期検証
        self.validate_hiragana()

    def validate_hiragana(self, *args):
        """name_readingにはHiraganaのみが含まれていることを確認します"""
        text = self.name_reading_var.get()
        if text and not self.is_hiragana(text):
            self.hiragana_validation_label.config(text="hiragana文字のみを使用してください")
        else:
            self.hiragana_validation_label.config(text="")

    def update_variant_performers_display(self):
        self.performers_listbox.delete(0, tk.END)
        for p in self.performers:
            name = self.characters.get(p, p)
            self.performers_listbox.insert(tk.END, f"{p} - {name}")

    def add_variant_performer(self):
        # 6人以上のパフォーマーを許可しないでください
        if len(self.performers) >= 6:
            messagebox.showerror("エラー", "6人以上のパフォーマーをバリアントに追加することはできません")
            return

        selected = self.character_var.get().split(' - ')[0]
        if selected not in self.performers:
            self.performers.append(selected)
            self.update_variant_performers_display()

    def remove_variant_performer(self):
        # 6人未満のパフォーマーを許可しないでください
        if len(self.performers) <= 1:
            messagebox.showerror("エラー", "バリアントには少なくとも1人のパフォーマーが必要です")
            return

        sel = self.performers_listbox.curselection()
        if sel:
            idx = sel[0]
            del self.performers[idx]
            self.update_variant_performers_display()
        
    def accept(self):
        # 少なくとも1人のパフォーマーがいることを確認します
        if not self.performers or len(self.performers) < 1:
            messagebox.showerror("エラー", "バリアントには少なくとも1人のパフォーマーが必要です")
            return

        # 必要なフィールドを検証します
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
                "必須フィールドが不足しています", 
                f"以下の必須フィールドに入力してください:\n\n• " + "\n• ".join(missing_fields)
            )
            return

        # name_readingがHiraganaで書かれていることを確認します
        name_reading = self.name_reading_var.get().strip()
        if not self.is_hiragana(name_reading):
            messagebox.showerror(
                "無効な入力",
                "バリアントの読みはひらがな文字のみを含める必要があります。\n\n",
                "読みのフィールドにはひらがな（ひらがな）を使用してください。"
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
        self.dialog.title("曲を設定")
    
        window_width = 800
        window_height = 580
    
        # 画面にダイアログを中央に配置します
        self.dialog.update_idletasks()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # ---基本変数（利用可能な場合は事前に充填）
        self.pv_id_var = tk.StringVar(value=song_data.get('pv_id', '') if song_data else '')
        self.song_name_var = tk.StringVar(value=song_data.get('song_name', '') if song_data else '')
        self.song_name_en_var = tk.StringVar(value=song_data.get('song_name_en', '') if song_data else '')
        self.song_name_reading_var = tk.StringVar(value=song_data.get('song_name_reading', '') if song_data else '')
        self.bpm_var = tk.StringVar(value=song_data.get('bpm', '') if song_data else '')
        # 日付は手動で編集できません。 Accept（）で上書きされます
        self.date_var = tk.StringVar(value=song_data.get('date', '') if song_data else '')
        self.sabi_start_var = tk.StringVar(value=song_data.get('sabi_start', '') if song_data else '')
        self.sabi_play_var = tk.StringVar(value=song_data.get('sabi_play', '') if song_data else '')
    
        # ---難易度変数（すでに存在する場合はコピー）
        self.difficulties = {}
        if song_data and 'difficulties' in song_data:
            self.difficulties = song_data['difficulties'].copy()
    
        # ---パフォーマー（文字コードのリスト）
        self.performers = song_data.get('performers', ['MIK']) if song_data else ['MIK']
    
        # ---既存のsonginfoおよびaudio_variants
        self.songinfo = song_data.get('songinfo', {}) if song_data else {}
        self.audio_variants = song_data.get('audio_variants', []) if song_data else []
    
        self.create_widgets()
        
    def validate_numeric(self, char):
        """数値のみが入力されていることを確認します"""
        return char.isdigit()

    def create_widgets(self):
        # 数値入力検証を登録します
        vcmd = (self.dialog.register(self.validate_numeric), '%S')

        # メインノートブック（タブ付きインターフェイス）
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # タブ
        self.create_basic_tab(vcmd)
        self.create_difficulty_tab()
        self.create_performers_tab()
        self.create_songinfo_tab()
        self.create_variants_tab()

        # 「受け入れる」 /「キャンセル」ボタン
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(button_frame, text="受け入れる", command=self.accept).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="キャンセル", command=self.cancel).pack(side=tk.RIGHT)

    def create_basic_tab(self, vcmd):
        basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_frame, text="基本情報")

        # PV ID（数字のみ、最大4桁）
        ttk.Label(basic_frame, text="PV ID： *").grid(row=0, column=0, sticky=tk.W, pady=2)
        pv_entry = ttk.Entry(basic_frame, textvariable=self.pv_id_var, width=40, validate='key', validatecommand=vcmd)
        pv_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # 元の名前（必須）
        ttk.Label(basic_frame, text="元の名前： *").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(basic_frame, textvariable=self.song_name_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # 英語名（必須）
        ttk.Label(basic_frame, text="英語名： *").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(basic_frame, textvariable=self.song_name_en_var, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # ヒラガナ名（必須）
        ttk.Label(basic_frame, text="ヒラガナ名： *").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(basic_frame, textvariable=self.song_name_reading_var, width=40).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # BPM（数字のみ、必須）
        ttk.Label(basic_frame, text="BPM： *").grid(row=4, column=0, sticky=tk.W, pady=2)
        bpm_entry = ttk.Entry(basic_frame, textvariable=self.bpm_var, width=40, validate='key', validatecommand=vcmd)
        bpm_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))

        # サビの開始時間（数字のみ）
        ttk.Label(basic_frame, text="開始時間は言う：").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(
            basic_frame,
            from_=0,
            to=999999,
            textvariable=self.sabi_start_var,
            width=10,
            validate='key',
            validatecommand=vcmd
        ).grid(row=5, column=1, sticky=(tk.W), pady=2, padx=(10, 0))

        # サビの期間（数字のみ）
        ttk.Label(basic_frame, text="期間を言う：").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(
            basic_frame,
            from_=0,
            to=999999,
            textvariable=self.sabi_play_var,
            width=10,
            validate='key',
            validatecommand=vcmd
        ).grid(row=6, column=1, sticky=(tk.W), pady=2, padx=(10, 0))

        # 必要なフィールドについてのメモ
        ttk.Label(basic_frame, text="*必要なフィールド", foreground="red", font=('TkDefaultFont', 8)).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        basic_frame.columnconfigure(1, weight=1)
        
    def create_difficulty_tab(self):
        diff_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(diff_frame, text="困難")

        # 1）ブール変数：true song_data ['難易度]に難易度が存在する場合
        self.easy_var = tk.BooleanVar(value=('easy' in self.difficulties))
        self.normal_var = tk.BooleanVar(value=('normal' in self.difficulties))
        self.hard_var = tk.BooleanVar(value=('hard' in self.difficulties))
        self.extreme_var = tk.BooleanVar(value=('extreme' in self.difficulties))
        self.extreme_extra_var = tk.BooleanVar(value=('extreme_extra' in self.difficulties))

        # 2）「PV_LV_07_5」→「7.5」を変換する機能
        def pv_to_numeric(pv_str):
            try:
                parts = pv_str.split('_')  # 例えば、["pv"、 "lv"、 "07"、 "5"]
                integer = int(parts[2])
                decimal = int(parts[3])
                return f"{integer}.{decimal}"
            except:
                return ''

        # 3）コンボボックスのStringVarを初期化します。
        # キーがself.difcultiesに存在する場合、その数値を表示します。それ以外の場合、空の文字列。
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

        # 4）難易度あたりの値の範囲を定義します
        # （各リストには、「7.5」、「8.0」などの文字列が含まれています）。
        easy_options = ["1.0","1.5","2.0","2.5","3.0","3.5","4.0","4.5"]
        normal_options = ["3.0","3.5","4.0","4.5","5.0","5.5","6.0"]
        hard_options = ["5.0","5.5","6.0","6.5","7.0","7.5","8.0","8.5"]
        extreme_options = ["6.0","6.5","7.0","7.5","8.0","8.5","9.0","9.5","10.0"]

        # 5）ウィジェットを反復して作成するリストをリストします
        difficulties = [
            ("かんたん", self.easy_var, self.easy_level_var, easy_options),
            ("ふつう", self.normal_var, self.normal_level_var, normal_options),
            ("むずかしい", self.hard_var, self.hard_level_var, hard_options),
            ("エクストリーム", self.extreme_var, self.extreme_level_var, extreme_options),
            ("エクストラエクストリーム", self.extreme_extra_var, self.extreme_extra_level_var, extreme_options)
        ]

        for i, (name, var, level_var, options) in enumerate(difficulties):
            # チェックボックス
            ttk.Checkbutton(diff_frame, text=name, variable=var).grid(row=i, column=0, sticky=tk.W, pady=2)
            # ラベル「レベル：」
            ttk.Label(diff_frame, text="レベル：").grid(row=i, column=1, sticky=tk.W, padx=(20, 5))
            # 特定の範囲の読み取り専用コンボボックス
            ttk.Combobox(
                diff_frame,
                textvariable=level_var,
                values=options,
                width=10,
                state="readonly"
            ).grid(row=i, column=2, sticky=tk.W)

        # 少なくとも1つの難易度を選択することに注意してください
        ttk.Label(diff_frame, text="*少なくとも1つの難易度を選択する必要があります", foreground="red", font=('TkDefaultFont', 8)).grid(row=len(difficulties), column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

    def create_performers_tab(self):
        perf_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(perf_frame, text="パフォーマー")

        # 選択したパフォーマー用のラベル +リストボックス
        ttk.Label(perf_frame, text="選択されたパフォーマー：").pack(anchor=tk.W)
        self.performers_listbox = tk.Listbox(perf_frame, height=6)
        self.performers_listbox.pack(fill='x', pady=(5, 10))

        # ボタンを追加 /削除します
        perf_buttons = ttk.Frame(perf_frame)
        perf_buttons.pack(fill='x')
        ttk.Button(perf_buttons, text="追加", command=self.add_performer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(perf_buttons, text="取り除く", command=self.remove_performer).pack(side=tk.LEFT)

        # 読み取り専用のキャラクターコンボボックス
        ttk.Label(perf_frame, text="文字を選択：").pack(anchor=tk.W, pady=(20, 5))
        self.characters = {
            'MIK': '初音ミク',
            'RIN': '鏡音リン',
            'LEN': '鏡音レン',
            'LUK': '巡音ルカ',
            'KAI': 'カイト',
            'MEI': 'メイコ',
            'HAK': '弱音ハク',
            'NER': '亞北ネル',
            'SAK': '咲音メイコ',
            'TET': '重音テト'
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
        self.notebook.add(info_frame, text="歌情報")

        self.songinfo_vars = {}
        fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']

        # オリジナルフィールド（任意の言語）
        for field in fields:
            self.songinfo_vars[field] = tk.StringVar(value=self.songinfo.get(field, ''))
        # 英語のフィールド
        for field in fields:
            self.songinfo_vars[field + '_en'] = tk.StringVar(value=self.songinfo.get(field + '_en', ''))

        labels = {
            'arranger': '編曲者:',
            'guitar_player': 'ギタープレイヤー:',
            'lyrics': '作詞者:',
            'manipulator': 'マニピュレーター:',
            'music': '作曲者／アーティスト:',
            'pv_editor': 'PV編集者:'
        }
        labels_en = {
            'arranger_en': '編曲者 (EN):',
            'guitar_player_en': 'ギタープレイヤー (EN):',
            'lyrics_en': '作詞者 (EN):',
            'manipulator_en': 'マニピュレーター (EN):',
            'music_en': '作曲者／アーティスト (EN):',
            'pv_editor_en': 'PV編集者 (EN):'
        }

        row = 0
        ttk.Label(info_frame, text="オリジナル", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        for field in fields:
            ttk.Label(info_frame, text=labels[field]).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(info_frame, textvariable=self.songinfo_vars[field], width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
            row += 1

        ttk.Separator(info_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        ttk.Label(info_frame, text="英語", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        for field in fields:
            field_en = field + '_en'
            ttk.Label(info_frame, text=labels_en[field_en]).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(info_frame, textvariable=self.songinfo_vars[field_en], width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
            row += 1

        # オリジナルセクションと英語の両方のセクションで少なくとも1つのフィールドを埋めることについてのメモ
        ttk.Label(info_frame, text="*オリジナルの少なくとも1つのフィールドと英語のフィールドを完成させる必要があります", 
                  foreground="red", font=('TkDefaultFont', 8)).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        info_frame.columnconfigure(1, weight=1)

    def update_variants_display(self):
        # このメソッドは、オーディオバリアントツリービューに入力されます
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
        self.notebook.add(variants_frame, text="オーディオバリエーション")

        ttk.Label(variants_frame, text="構成されたオーディオバリアント：").pack(anchor=tk.W)

        # オーディオバリエーションのツリービュー
        self.variants_tree = ttk.Treeview(
            variants_frame,
            columns=('name', 'name_en', 'artist'),
            show='headings',
            height=8
        )
        self.variants_tree.heading('name', text='原名')
        self.variants_tree.heading('name_en', text='英語名')
        self.variants_tree.heading('artist', text='アーティスト')
        self.variants_tree.pack(fill='both', expand=True, pady=(5, 10))

        # バリアントを追加/編集/削除するボタン
        variants_buttons = ttk.Frame(variants_frame)
        variants_buttons.pack(fill='x')
        ttk.Button(variants_buttons, text="バリアントを追加します", command=self.add_variant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(variants_buttons, text="バリアントを編集します", command=self.edit_variant).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(variants_buttons, text="バリアントを削除します", command=self.remove_variant).pack(side=tk.LEFT)

        # update_variants_displayを呼び出します（treeviewが定義された後）
        self.update_variants_display()
        
    def update_performers_display(self):
        self.performers_listbox.delete(0, tk.END)
        for performer in self.performers:
            char_name = self.characters.get(performer, performer)
            self.performers_listbox.insert(tk.END, f"{performer} - {char_name}")
    
    def add_performer(self):
        # 最大6人のパフォーマーを実施します
        if len(self.performers) >= 6:
            messagebox.showerror("エラー", "6人以上のパフォーマーを追加することはできません")
            return
    
        selected = self.character_var.get().split(' - ')[0]
        if selected not in self.performers:
            self.performers.append(selected)
            self.update_performers_display()
    
    def remove_performer(self):
        # 少なくとも1人のパフォーマーを強制します
        if len(self.performers) <= 1:
            messagebox.showerror("エラー", "少なくとも1人のパフォーマーがいる必要があります")
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
            messagebox.showwarning("警告", "編集するバリアントを選択します")
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
            messagebox.showwarning("警告", "削除するバリアントを選択します")
            return
        if messagebox.askyesno("確認", "このバリアントを削除してもよろしいですか？"):
            item = selection[0]
            index = self.variants_tree.index(item)
            del self.audio_variants[index]
            self.update_variants_display()
    
    def accept(self):
        # ----------------------------------------
        # 1）PV ID：必要、数値、正、範囲001-9999
        if not self.pv_id_var.get().strip():
            messagebox.showerror("エラー", "PV IDが必要です")
            return
        pv_id_raw = self.pv_id_var.get().strip()
        try:
            pv_id_num = int(pv_id_raw)
            if pv_id_num < 1 or pv_id_num > 9999:
                messagebox.showerror("エラー", "PV IDは001〜9999の間でなければなりません")
                return
            pv_id_formatted = f"{pv_id_num:03d}"
        except ValueError:
            messagebox.showerror("エラー", "PV IDは有効な番号である必要があります")
            return
    
        # ----------------------------------------
        # 2）曲名：必須
        if not self.song_name_var.get().strip():
            messagebox.showerror("エラー", "元の名前が必要です")
            return
        if not self.song_name_en_var.get().strip():
            messagebox.showerror("エラー", "英語名が必要です")
            return
    
        # ----------------------------------------
        # 3）hiragana：必須、ヒラガナ文字（プラス「ー」とスペース）のみを含める必要があります
        hira = self.song_name_reading_var.get().strip()
        if not hira:
            messagebox.showerror("エラー", "ヒラガナの名前が必要です")
            return
        if not re.fullmatch(r'[\u3040-\u309Fー\s]+', hira):
            messagebox.showerror("エラー", "ヒラガナの名前には、ヒラガナ文字のみが含まれている必要があります")
            return
    
        # ----------------------------------------
        # 4）bpm：必須、正の整数
        if not self.bpm_var.get().strip():
            messagebox.showerror("エラー", "BPMが必要です")
            return
        try:
            bpm_val = int(self.bpm_var.get().strip())
            if bpm_val <= 0:
                messagebox.showerror("エラー", "BPMは正の整数でなければなりません")
                return
        except ValueError:
            messagebox.showerror("エラー", "BPMは有効な整数でなければなりません")
            return
    
        # ----------------------------------------
        # 5）少なくとも1つの難易度を選択する必要があります
        has_difficulty = (self.easy_var.get() or self.normal_var.get() or 
                          self.hard_var.get() or self.extreme_var.get() or 
                          self.extreme_extra_var.get())
        if not has_difficulty:
            messagebox.showerror("エラー", "少なくとも1つの難易度を選択する必要があります")
            return
    
        # ----------------------------------------
        # 6）パフォーマー：最小1、最大6
        if len(self.performers) < 1:
            messagebox.showerror("エラー", "少なくとも1人のパフォーマーがいる必要があります")
            return
        if len(self.performers) > 6:
            messagebox.showerror("エラー", "6人以上のパフォーマーを持つことはできません")
            return
    
        # ----------------------------------------
        # 7）曲情報：オリジナルの少なくとも1つのフィールドと英語のフィールドを完成させる必要があります
        fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']
        has_original = any(self.songinfo_vars[field].get().strip() for field in fields)
        has_english = any(self.songinfo_vars[field + '_en'].get().strip() for field in fields)
    
        if not has_original:
            messagebox.showerror("エラー", "元のセクションの少なくとも1つのフィールドを完了する必要があります")
            return
        if not has_english:
            messagebox.showerror("エラー", "英語セクションの少なくとも1つのフィールドを完了する必要があります")
            return
    
        # ----------------------------------------
        # 8）各数値レベル（例：「7.5」）を「PV_LV_07_5」に変換します
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
                messagebox.showerror("エラー", "簡単な難易度を選択する必要があります")
                return
            difficulties['easy'] = {
                'level': numeric_to_pv(self.easy_level_var.get()),
                'level_sort_index': '50'
            }
        if self.normal_var.get():
            if not self.normal_level_var.get():
                messagebox.showerror("エラー", "通常の難易度を選択する必要があります")
                return
            difficulties['normal'] = {
                'level': numeric_to_pv(self.normal_level_var.get()),
                'level_sort_index': '50'
            }
        if self.hard_var.get():
            if not self.hard_level_var.get():
                messagebox.showerror("エラー", "難易度レベルを選択する必要があります")
                return
            difficulties['hard'] = {
                'level': numeric_to_pv(self.hard_level_var.get()),
                'level_sort_index': '80'
            }
        if self.extreme_var.get():
            if not self.extreme_level_var.get():
                messagebox.showerror("エラー", "極端な難易度を選択する必要があります")
                return
            difficulties['extreme'] = {
                'level': numeric_to_pv(self.extreme_level_var.get()),
                'level_sort_index': '20'
            }
        if self.extreme_extra_var.get():
            if not self.extreme_extra_level_var.get():
                messagebox.showerror("エラー", "余分な極端な難易度を選択する必要があります")
                return
            difficulties['extreme_extra'] = {
                'level': numeric_to_pv(self.extreme_extra_level_var.get()),
                'level_sort_index': '50'
            }
    
        # ----------------------------------------
        # 9）Songinfo：空でないフィールドを収集します
        songinfo = {}
        for field, var in self.songinfo_vars.items():
            value = var.get().strip()
            if value:
                songinfo[field] = value
    
        # ----------------------------------------
        # 10）日付：「yyyymmdd」形式で現在の日付を割り当てます
        from datetime import datetime
        current_date = datetime.now().strftime("%Y%m%d")
    
        # ----------------------------------------
        # 11）start / duration：from self.sabi_start_var / self.sabi_play_varから
        sabi_start = self.sabi_start_var.get().strip() if self.sabi_start_var.get().strip() else "0"
        sabi_play = self.sabi_play_var.get().strip() if self.sabi_play_var.get().strip() else "0"
    
        # ----------------------------------------
        # 12）最終結果を作成します
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

        self.root.title("ミクミクDBエディター")
        
        # より良い応答性のために画面寸法を取得します
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 画面解像度に基づいて最小サイズと初期サイズを設定します
        min_width = 800
        min_height = 600
        
        # 最適なウィンドウサイズを計算します（画面の80％ですが、最低値以上）
        window_width = max(min_width, int(screen_width * 0.8))
        window_height = max(min_height, int(screen_height * 0.8))
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(min_width, min_height)
        
        # 画面上のウィンドウを中央に配置します
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 画面が十分に大きい場合にのみ最大化します
        # screen_width> = 1200およびscreen_height> = 800の場合：
        # self.root.state（ "Zoomed"）

        self.root.state("zoomed")
        
        self.set_icon()
        
        # データ
        self.pack_name = ""
        self.pack_name_jp = ""
        self.songs = []

        # 他のコンポーネントの前にスクロール可能なメインフレームをセットアップします
        self.setup_scrollable_main_frame()
        
        self.setup_drag_drop()
        self.setup_drag_visual_feedback()
        self.setup_autosave()
        self.create_widgets()
    
    def setup_scrollable_main_frame(self):
        """より良い解像度サポートのために、スクロール可能なメインフレームをセットアップします"""
        try:
            # メインキャンバスとスクロールバーを作成します
            self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
            self.main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
            
            # スクロール可能なフレームを作成します
            self.scrollable_frame = ttk.Frame(self.main_canvas)
            
            # キャンバスを構成します
            self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
            
            # キャンバスとスクロールバーをパックします
            self.main_canvas.pack(side="left", fill="both", expand=True)
            self.main_scrollbar.pack(side="right", fill="y")
            
            # キャンバスにウィンドウを作成します
            self.canvas_window = self.main_canvas.create_window(
                (0, 0), window=self.scrollable_frame, anchor="nw"
            )
            
            # スクロール可能なフレームを構成します
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            )
            
            # キャンバスウィンドウの幅を構成します
            self.main_canvas.bind(
                "<Configure>",
                self.on_canvas_configure
            )
            
            # マウスホイールをキャンバスに結合します
            self.bind_mousewheel()
            
            # 自己の代わりにすべてのウィジェットの親としてself.scrollable_frameを使用する
            
        except Exception as e:
            print(f"スクロール可能なフレームの設定中にエラーが発生しました: {e}")
            # ルートを直接使用することへのフォールバック
            self.scrollable_frame = self.root

    def on_canvas_configure(self, event):
        """キャンバスのサイズを処理して、スクロール可能なフレーム幅を調整します"""
        try:
            canvas_width = event.width
            self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)
        except:
            pass

    def bind_mousewheel(self):
        """スクロール用のマウスホイールイベントをバインドします"""
        try:
            # マウスホイールイベントを結合します
            self.main_canvas.bind("<MouseWheel>", self.on_mousewheel)
            self.main_canvas.bind("<Button-4>", self.on_mousewheel)
            self.main_canvas.bind("<Button-5>", self.on_mousewheel)
            
            # フォーカスイベントをバインドして、スクロールを有効/無効にします
            self.main_canvas.bind("<Enter>", self.bind_to_mousewheel)
            self.main_canvas.bind("<Leave>", self.unbind_from_mousewheel)
            
        except Exception as e:
            print(f"マウスホイールのバインド中にエラーが発生しました: {e}")

    def on_mousewheel(self, event):
        """マウスホイールスクロールを処理します"""
        try:
            # 窓とmacos
            if event.delta:
                delta = -1 * (event.delta / 120)
            # Linux
            elif event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                delta = 0
                
            # キャンバスをスクロールします
            self.main_canvas.yview_scroll(int(delta), "units")
            
        except:
            pass

    def bind_to_mousewheel(self, event):
        """マウスがキャンバスに入るときにマウスホイールスクロールを有効にします"""
        try:
            self.root.bind_all("<MouseWheel>", self.on_mousewheel)
            self.root.bind_all("<Button-4>", self.on_mousewheel)
            self.root.bind_all("<Button-5>", self.on_mousewheel)
        except:
            pass

    def unbind_from_mousewheel(self, event):
        """マウスがキャンバスを去るときにマウスホイールスクロールを無効にします"""
        try:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except:
            pass

    def setup_autosave(self):
        """AutoSaveシステムをセットアップします"""
        self.autosave_folder = "自動保存"
        self.autosave_interval = 5 * 60 * 1000
        self.max_autosave_files = 60

        # 存在しない場合はAutoSaveフォルダーを作成します
        if not os.path.exists(self.autosave_folder):
            os.makedirs(self.autosave_folder)

        # AutoSaveタイマーを開始します
        self.schedule_autosave()

    def schedule_autosave(self):
        """次のAutoSaveをスケジュールします"""
        self.root.after(self.autosave_interval, self.autosave)

    def autosave(self):
        """自動AutoSaveを実行します"""
        try:
            if self.songs or self.pack_name_var.get().strip():
                timestamp = datetime.now().strftime("%Y%m%d_-_%H_%M_%S")
                filename = os.path.join(self.autosave_folder, f"autosave_{timestamp}.pdpack")

                # 構成を準備します
                config = {
                    'pack_name': self.pack_name_var.get(),
                    'pack_name_jp': self.pack_name_jp_var.get(),
                    'songs': self.songs
                }

                # ファイルを保存します
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                # 必要に応じて古いファイルをクリアします
                self.cleanup_old_autosaves()

                print(f"自動保存完了: {filename}")

        except Exception as e:
            print(f"自動保存エラー: {str(e)}")

        finally:
            # 次のAutoSaveをプログラムします
            self.schedule_autosave()

    def cleanup_old_autosaves(self):
        """制限を超えた場合は、古いAutoSaveファイルを削除します"""
        try:
            pattern = os.path.join(self.autosave_folder, "autosave_*.pdpack")
            autosave_files = glob.glob(pattern)

            # 許可された制限よりも多くのファイルがある場合
            if len(autosave_files) > self.max_autosave_files:
                # 変更日（最古）ごとにソート
                autosave_files.sort(key=os.path.getmtime)

                # 削除するファイルの数を計算します
                files_to_remove = len(autosave_files) - self.max_autosave_files

                # 最古のファイルを削除します
                for i in range(files_to_remove):
                    os.remove(autosave_files[i])
                    print(f"自動保存ファイルを削除しました: {autosave_files[i]}")

        except Exception as e:
            print(f"自動保存のクリア中にエラーが発生しました: {str(e)}")

    def set_icon(self):
        try:
            self.root.iconbitmap("icon.ico")
        except Exception as e:
            print(f"アイコンビットマップの設定中にエラーが発生しました: {e}")
        
    def create_widgets(self):
        # メインタイトル
        title_label = ttk.Label(self.scrollable_frame, text="Mikumikudb編集者", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # 情報フレームをパックします
        pack_frame = ttk.LabelFrame(self.scrollable_frame, text="ソングパック情報", padding="10")
        pack_frame.pack(fill='x', padx=10, pady=5)
        
        # パック名
        ttk.Label(pack_frame, text="ソングパックの名前：").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pack_name_var = tk.StringVar()
        ttk.Entry(pack_frame, textvariable=self.pack_name_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        ttk.Label(pack_frame, text="日本語名：").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pack_name_jp_var = tk.StringVar()
        ttk.Entry(pack_frame, textvariable=self.pack_name_jp_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        
        pack_frame.columnconfigure(1, weight=1)
        
        # 曲フレーム
        songs_frame = ttk.LabelFrame(self.scrollable_frame, text="歌", padding="10")
        songs_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 歌リスト
        self.songs_tree = ttk.Treeview(songs_frame, columns=('id', 'name', 'name_en'), show='headings', height=15)
        self.songs_tree.heading('id', text='PV ID')
        self.songs_tree.heading('name', text='原名')
        self.songs_tree.heading('name_en', text='英語名')
        
        self.songs_tree.column('id', width=80)
        self.songs_tree.column('name', width=300)
        self.songs_tree.column('name_en', width=300)
        
        scrollbar = ttk.Scrollbar(songs_frame, orient='vertical', command=self.songs_tree.yview)
        self.songs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.songs_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 歌のボタン
        songs_buttons = ttk.Frame(self.root)
        songs_buttons.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(songs_buttons, text="曲を追加します", command=self.add_song).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(songs_buttons, text="曲を編集します", command=self.edit_song).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(songs_buttons, text="曲を削除します", command=self.delete_song).pack(side=tk.LEFT, padx=(0, 5))
        
        # メインボタン
        main_buttons = ttk.Frame(self.root)
        main_buttons.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(main_buttons, text="ファイルを生成します", command=self.generate_file).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="mod_pv_db.txtをインポートします", command=self.import_mod_pv_db).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="設定を読み込みます", command=self.load_config).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="AutoSaveをロードします", command=self.load_autosave).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(main_buttons, text="構成を保存します", command=self.save_config).pack(side=tk.RIGHT, padx=(10, 0))
        
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
            messagebox.showwarning("警告", "編集する曲を選択します")
            return
    
        # 選択した曲のインデックスを取得します
        item = selection[0]
        index = self.songs_tree.index(item)
    
        # 既存のデータをダイアログに渡して、事前に充填されるように
        dialog = SongConfigDialog(self.root, self.songs[index])
        self.root.wait_window(dialog.dialog)
    
        # ユーザーが変更を加えて受け入れた場合は、self.songsのエントリを交換します。
        if dialog.result:
            self.songs[index] = dialog.result
            self.update_songs_display()
    
    def delete_song(self):
        selection = self.songs_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "削除する曲を選択します")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this song?"):
            item = selection[0]
            index = self.songs_tree.index(item)
            del self.songs[index]
            self.update_songs_display()
    
    def generate_file(self):
        if not self.pack_name_var.get().strip():
            messagebox.showerror("エラー", "ソングパック名を入力してください")
            return

        if not self.songs:
            messagebox.showerror("エラー", "少なくとも1つの曲を追加します")
            return

        for song in self.songs:
            if not song.get('performers') or len(song['performers']) < 1:
                messagebox.showerror("エラー", f"ソングPV {song.get('pv_id')} には少なくとも1人のパフォーマーが必要です")
                return

        # ファイルコンテンツを生成します
        content = self.generate_file_content()

        # ファイルを保存します
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")],
            initialfile="mod_pv_db.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"ファイルが正常に生成されました: {filename}")
            except Exception as e:
                messagebox.showerror("エラー", f"ファイルの保存中にエラーが発生しました: {str(e)}")
    
    def generate_file_content(self):
        content = []

        # ヘッダー
        content.append("# MikuMikuDBエディターによって生成されました")
        content.append("# 作成者: NyxC")
        content.append("")

        content.append(f"#" + "-" * 30)
        pack_name_jp = self.pack_name_jp_var.get().strip() or self.pack_name_var.get().strip()
        content.append(f"# {self.pack_name_var.get()} 追加チャート")
        content.append("#")

        # 歌リスト
        for song in self.songs:
            song_line = f"# pv_{song['pv_id']}\t{song['song_name']}"
            if song['song_name_en']:
                song_line += f" | {song['song_name_en']}"
            content.append(song_line)

        content.append("#" + "-" * 30)
        content.append("")

        # 各曲を生成します
        for i, song in enumerate(self.songs):
            if i > 0:
                content.append("")  # 歌の間の空の線

            pv_id = song['pv_id']

            # オーディオバリアント（存在する場合）
            if song.get('audio_variants'):
                # オリジナルソングバリアント（インデックス0）
                content.extend([
                    f"pv_{pv_id}.another_song.0.name={song['song_name']}",
                    f"pv_{pv_id}.another_song.0.name_en={song['song_name_en']}",
                    f"pv_{pv_id}.another_song.0.name_reading={song['song_name_reading']}",
                ])
                # バリアント0のvocal_chara_num
                content.append(f"pv_{pv_id}.another_song.0.vocal_chara_num={song['performers'][0]}")

                # 追加のバリアント（インデックス1..n）
                for j, variant in enumerate(song['audio_variants'], 1):
                    # 修正：name_readingにフォールバックで.get（）を使用します
                    name_reading = variant.get('name_reading', variant.get('name', ''))

                    content.extend([
                        f"pv_{pv_id}.another_song.{j}.name={variant['name']}",
                        f"pv_{pv_id}.another_song.{j}.name_en={variant['name_en']}",
                        f"pv_{pv_id}.another_song.{j}.name_reading={name_reading}",
                    ])

                    # vocal_chara_num：このバリアントの最初のパフォーマー
                    variant_performer = variant.get('performers', [song['performers'][0]])[0]
                    content.append(f"pv_{pv_id}.another_song.{j}.vocal_chara_num={variant_performer}")

                    # ファイル名
                    suffix = variant.get('file_suffix', '').strip()
                    if not suffix:
                        suffix = str(j)
                    content.append(f"pv_{pv_id}.another_song.{j}.song_file_name=rom/sound/song/pv_{pv_id}_{suffix}.ogg")

                    # vocal_disp_nameおよびvocal_disp_name_enが提供されている場合
                    if variant.get('vocal_disp', ''):
                        content.append(f"pv_{pv_id}.another_song.{j}.vocal_disp_name={variant['vocal_disp']}")
                    if variant.get('vocal_disp_en', ''):
                        content.append(f"pv_{pv_id}.another_song.{j}.vocal_disp_name_en={variant['vocal_disp_en']}")

                # 全長（オリジナル +追加）
                content.append(f"pv_{pv_id}.another_song.length={len(song['audio_variants']) + 1}")

            # 基本的な歌情報
            content.extend([
                f"pv_{pv_id}.bpm={song['bpm']}",
                f"pv_{pv_id}.chainslide_failure_name=slide_ng03",
                f"pv_{pv_id}.chainslide_first_name=slide_long02a",
                f"pv_{pv_id}.chainslide_sub_name=slide_button08",
                f"pv_{pv_id}.chainslide_success_name=slide_ok03",
                f"pv_{pv_id}.date={song['date']}"
            ])

            # 困難
            difficulties = song.get('difficulties', {})

            # 簡単
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

            # 過激
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

            # 難しい
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

            # 普通
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

            # 標準設定
            content.extend([
                f"pv_{pv_id}.hiddentiming=0.3",
                f"pv_{pv_id}.high_speedrate=4",
                f"pv_{pv_id}.movie_filename=rom/movie/pv_{pv_id}.mp4",
                f"pv_{pv_id}.movie_pvtype=ONLY",
                f"pv_{pv_id}.movie_surface=FRONT",
                f"pv_{pv_id}.pack=2"
            ])

            # パフォーマー
            performers = song.get('performers', ['MIK'])
            for j, performer in enumerate(performers):
                content.extend([
                    f"pv_{pv_id}.performer.{j}.chara={performer}",
                    f"pv_{pv_id}.performer.{j}.pv_costume=1",
                    f"pv_{pv_id}.performer.{j}.type=VOCAL"
                ])
            content.append(f"pv_{pv_id}.performer.num={len(performers)}")

            # 設定は言います
            content.extend([
                f"pv_{pv_id}.sabi.playtime={song['sabi_play']}",
                f"pv_{pv_id}.sabi.start_time={song['sabi_start']}"
            ])

            # 標準のサウンド設定
            content.extend([
                f"pv_{pv_id}.se_name=01_button1",
                f"pv_{pv_id}.slide_name=slide_se13",
                f"pv_{pv_id}.slidertouch_name=slide_windchime",
                f"pv_{pv_id}.song_filename=rom/sound/song/pv_{pv_id}.ogg"
            ])

            # 歌名
            content.extend([
                f"pv_{pv_id}.song_name={song['song_name']}",
                f"pv_{pv_id}.song_name_en={song['song_name_en']}"
            ])
            content.extend([
                f"pv_{pv_id}.song_name_reading={song['song_name_reading']}",
            ])

            # Songinfo-最初のバージョン
            songinfo = song.get('songinfo', {})
            songinfo_fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']

            # 最初のパス：すべてのオリジナルのsonginfoフィールドを追加します
            for field in songinfo_fields:
                if field in songinfo and songinfo[field]:
                    content.append(f"pv_{pv_id}.songinfo.{field}={songinfo[field]}")

            # 2番目のパス：すべての英語Songinfoフィールドを追加します
            for field in songinfo_fields:
                en_field = f"{field}_en"
                if en_field in songinfo and songinfo[en_field]:
                    content.append(f"pv_{pv_id}.songinfo_en.{field}={songinfo[en_field]}")

            content.append(f"pv_{pv_id}.sudden_timing=0.6")

        return '\n'.join(content)
    
    def import_mod_pv_db(self):
        """既存のmod_pv_db.txtファイルをインポートします"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("プロジェクトディーバ DB ファイル", "*.txt"),
                ("すべてのファイル", "*.*")
            ],
            title="mod_pv_db.txt をインポートする"
        )
    
        if not filename:
            return
    
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
    
            # ファイルコンテンツを解析します
            songs = self.parse_mod_pv_db_content(content)
            
            if not songs:
                messagebox.showwarning("警告", "ファイルに有効な曲は見つかりません")
                return
    
            # 現在の曲を交換するか、追加するかどうかをユーザーに尋ねます
            if self.songs:
                result = messagebox.askyesnocancel(
                    "インポートオプション",
                    f"ファイル内に {len(songs)} 曲が見つかりました。\n\n"
                    "はい: 現在の曲を置き換える\n"
                    "いいえ: 現在の曲に追加する\n"
                    "キャンセル: インポートをキャンセルする"
                )
                
                if result is None:  # キャンセル
                    return
                elif result:  # はい - 交換してください
                    self.songs = songs
                else:  # いいえ - 追加
                    self.songs.extend(songs)
            else:
                self.songs = songs
    
            self.update_songs_display()
            messagebox.showinfo("成功", f"mod_pv_db.txt から {len(songs)} 曲を正常にインポートしました")
    
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルのインポート中にエラーが発生しました: {str(e)}")
    
    def parse_mod_pv_db_content(self, content):
        """parse mod_pv_db.txtコンテンツと抽出ソングデータ"""
        songs = []
        lines = content.split('\n')
        
        # ファイル内のすべてのPV IDを見つけます
        pv_ids = set()
        for line in lines:
            if line.strip() and not line.strip().startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                if key.startswith('pv_') and '.' in key:
                    pv_id = key.split('.')[0].replace('pv_', '')
                    pv_ids.add(pv_id)
        
        # 各曲を解析します
        for pv_id in sorted(pv_ids, key=lambda x: int(x) if x.isdigit() else 0):
            song_data = self.parse_single_song(lines, pv_id)
            if song_data:
                songs.append(song_data)
        
        return songs
    
    def parse_single_song(self, lines, pv_id):
        """ファイル行からの単一の曲のデータを解析します"""
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
        
        # クイックルックアップのために辞書を作成します
        data_dict = {}
        for line in lines:
            if line.strip() and not line.strip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key.startswith(f'pv_{pv_id}.'):
                    data_dict[key] = value
        
        # 基本的な歌情報
        song['song_name'] = data_dict.get(f'pv_{pv_id}.song_name', f'Song {pv_id}')
        song['song_name_en'] = data_dict.get(f'pv_{pv_id}.song_name_en', song['song_name'])
        song['song_name_reading'] = data_dict.get(f'pv_{pv_id}.song_name_reading', song['song_name'])
        
        # BPMと日付
        song['bpm'] = int(data_dict.get(f'pv_{pv_id}.bpm', 120))
        song['date'] = data_dict.get(f'pv_{pv_id}.date', '20250101')
        
        # 設定は言います
        song['sabi_play'] = data_dict.get(f'pv_{pv_id}.sabi.playtime', '30.0')
        sabi_start = data_dict.get(f'pv_{pv_id}.sabi.start_time', '30000')
        # 必要に応じて、ミリ秒を秒に変換します
        try:
            if float(sabi_start) > 1000:
                song['sabi_start'] = str(float(sabi_start) / 1000)
            else:
                song['sabi_start'] = sabi_start
        except:
            song['sabi_start'] = '30.0'
        
        # 解析の困難
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
        
        # 極端な余分を確認してください
        extreme_length = int(data_dict.get(f'pv_{pv_id}.difficulty.extreme.length', '0'))
        if extreme_length > 1:
            # 余分な極端なチャートがあります（インデックス1）
            level = data_dict.get(f'pv_{pv_id}.difficulty.extreme.1.level', 'PV_LV_09_0')
            level_sort = data_dict.get(f'pv_{pv_id}.difficulty.extreme.1.level_sortindex', '50')
            
            song['difficulties']['extreme_extra'] = {
                'level': level,
                'level_sort_index': int(level_sort)
            }
        
        # パージーパフォーマー
        performer_num = int(data_dict.get(f'pv_{pv_id}.performer.num', '1'))
        for i in range(performer_num):
            chara = data_dict.get(f'pv_{pv_id}.performer.{i}.chara', 'MIK')
            song['performers'].append(chara)
        
        # Parse Songinfo
        songinfo_fields = ['arranger', 'guitar_player', 'lyrics', 'manipulator', 'music', 'pv_editor']
        for field in songinfo_fields:
            value = data_dict.get(f'pv_{pv_id}.songinfo.{field}', '')
            if value:
                song['songinfo'][field] = value
            
            # 英語版
            en_value = data_dict.get(f'pv_{pv_id}.songinfo_en.{field}', '')
            if en_value:
                song['songinfo'][f'{field}_en'] = en_value
        
        # 解析オーディオバリアント
        another_song_length = int(data_dict.get(f'pv_{pv_id}.another_song.length', '0'))
        if another_song_length > 1:  # オリジナル以上のもの（インデックス0）
            for i in range(1, another_song_length):  # 1から始めて、オリジナルをスキップします
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
        """カスタム暗号化で構成を保存します"""
        if not self.songs:
            messagebox.showwarning("警告", "保存する曲はありません")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdpack",
            filetypes=[
                ("プロジェクトディーバ パックファイル", "*.pdpack")
            ],
            initialfile="config.pdpack"
        )

        if filename:
            try:
                config = {
                    'pack_name': self.pack_name_var.get(),
                    'pack_name_jp': self.pack_name_jp_var.get(),
                    'songs': self.songs,
                    'version': '2.0',  # 暗号化された形式のバージョン識別子
                    'created_by': 'MikuMikuDB Editor',
                    'encryption': True
                }

                # 暗号化ハンドラーを初期化します
                encryptor = CustomEncryption()

                # データを暗号化します
                encrypted_data = encryptor.encrypt_data(config)

                # 暗号化されたデータをファイルに書き込みます
                with open(filename, 'wb') as f:
                    f.write(encrypted_data)

                messagebox.showinfo("成功", f"暗号化された設定が保存されました: {filename}")

            except Exception as e:
                messagebox.showerror("エラー", f"暗号化された設定の保存中にエラーが発生しました: {str(e)}")

    def load_config(self):
        """カスタム復号化で構成をロードします"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("プロジェクトディーバ パックファイル", "*.pdpack")
            ]
        )

        if filename:
            try:
                # ファイルコンテンツを読み取ります
                with open(filename, 'rb') as f:
                    file_content = f.read()

                # 暗号化されているかレガシーJSONかどうかを判断してみてください
                if file_content.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                    # 新しい暗号化形式
                    encryptor = CustomEncryption()
                    config = encryptor.decrypt_data(file_content)

                elif file_content.startswith(b'{'):
                    # レガシーJSON形式
                    json_string = file_content.decode('utf-8')
                    config = json.loads(json_string)

                    # 移行プロンプトを表示します
                    result = messagebox.askyesno(
                        "レガシーフォーマットを検出しました",
                        "このファイルは旧式の暗号化されていない形式を使用しています。\n\n"
                        "新しい暗号化形式に変換しますか？\n"
                        "（元のファイルはバックアップされます）"
                    )

                    if result:
                        self._migrate_legacy_file(filename, config)

                else:
                    raise Exception("認識できないファイル形式")

                # 構成データをロードします
                self.pack_name_var.set(config.get('pack_name', ''))
                self.pack_name_jp_var.set(config.get('pack_name_jp', ''))
                self.songs = config.get('songs', [])

                self.update_songs_display()

                encryption_status = "encrypted" if config.get('encryption', False) else "unencrypted"
                messagebox.showinfo("成功", f"設定がロードされました（{encryption_status}）: {os.path.basename(filename)}")

            except Exception as e:
                messagebox.showerror("エラー", f"設定の読み込み中にエラーが発生しました: {str(e)}")

    def _migrate_legacy_file(self, filename, config):
        """Legacy JSONファイルを暗号化された形式に移行します"""
        try:
            # バックアップを作成します
            backup_filename = filename + '.backup'
            if os.path.exists(filename):
                import shutil
                shutil.copy2(filename, backup_filename)

            # 暗号化された形式の構成を更新します
            config.update({
                'version': '2.0',
                'created_by': 'MikuMikuDB Editor',
                'encryption': True,
                'migrated_from': 'legacy_json'
            })

            # 暗号化して保存します
            encryptor = CustomEncryption()
            encrypted_data = encryptor.encrypt_data(config)

            with open(filename, 'wb') as f:
                f.write(encrypted_data)

            messagebox.showinfo(
                "移行完了",
                f"ファイルは暗号化形式に正常に変換されました。\n"
                f"バックアップとして保存されました: {os.path.basename(backup_filename)}"
            )

        except Exception as e:
            messagebox.showerror("移行エラー", f"ファイルの移行に失敗しました: {str(e)}")

    def create_autosave(self):
        """暗号化されたAutoSaveファイルを作成します"""
        if not self.songs:
            return  # 保存するデータはありません

        try:
            # AutoSaveディレクトリが存在することを確認してください
            os.makedirs(self.autosave_folder, exist_ok=True)

            # タイムスタンプファイル名を生成します
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

            # 暗号化してAutoSaveを保存します
            encryptor = CustomEncryption()
            encrypted_data = encryptor.encrypt_data(config)

            with open(filename, 'wb') as f:
                f.write(encrypted_data)

            # 古いAutoSaveファイルをクリーンアップします（最後の10のみを保持します）
            self._cleanup_autosave_files()

        except Exception as e:
            print(f"自動保存に失敗しました: {str(e)}")  # AutoSaveのサイレントフェイル

    def _cleanup_autosave_files(self):
        """最新の10個のAutoSaveファイルのみを保持します"""
        try:
            import glob
            pattern = os.path.join(self.autosave_folder, "autosave_*.pdpack")
            autosave_files = glob.glob(pattern)

            if len(autosave_files) > 10:
                # 変更時間ごとにソート、最古の最初のもの
                autosave_files.sort(key=os.path.getmtime)

                # 最古のファイルを削除します
                for old_file in autosave_files[:-10]:
                    os.remove(old_file)

        except Exception as e:
            print(f"自動保存のクリーンアップに失敗しました: {str(e)}")

    def load_autosave(self):
        """暗号化されたAutoSaveファイルをロードします"""
        if not os.path.exists(self.autosave_folder):
            messagebox.showinfo("情報", "AutoSaveファイルは利用できません")
            return

        # AutoSaveファイルを検索します
        import glob
        pattern = os.path.join(self.autosave_folder, "autosave_*.pdpack")
        autosave_files = glob.glob(pattern)

        if not autosave_files:
            messagebox.showinfo("情報", "AutoSaveファイルは利用できません")
            return

        # 選択ダイアログを表示します
        autosave_files.sort(key=os.path.getmtime, reverse=True)  # 最新の最初

        # 選択ウィンドウを作成します
        dialog = tk.Toplevel(self.root)
        dialog.title("暗号化された自動保存を読み込む")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="暗号化されたAutoSaveファイルを選択します。", font=('Arial', 12, 'bold')).pack(pady=10)

        # ファイルリスト
        listbox = tk.Listbox(dialog, height=15)
        listbox.pack(fill='both', expand=True, padx=10, pady=5)

        for file in autosave_files:
            filename = os.path.basename(file)
            # ファイル名からタイムスタンプを抽出します
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
                messagebox.showwarning("警告", "AutoSaveファイルを選択します")
                return

            selected_file = autosave_files[selection[0]]
            dialog.destroy()

            # 選択した暗号化されたファイルをロードします
            try:
                with open(selected_file, 'rb') as f:
                    encrypted_data = f.read()

                # データを復号化します
                encryptor = CustomEncryption()
                config = encryptor.decrypt_data(encrypted_data)

                self.pack_name_var.set(config.get('pack_name', ''))
                self.pack_name_jp_var.set(config.get('pack_name_jp', ''))
                self.songs = config.get('songs', [])

                self.update_songs_display()
                messagebox.showinfo("成功", f"暗号化された自動保存が読み込まれました: {os.path.basename(selected_file)}")

            except Exception as e:
                messagebox.showerror("エラー", f"暗号化された自動保存の読み込み中にエラーが発生しました: {str(e)}")

        # ボタン
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="負荷", command=load_selected).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="キャンセル", command=dialog.destroy).pack(side=tk.RIGHT)

    def setup_drag_drop(self):
        """メインウィンドウのドラッグアンドドロップ機能をセットアップします"""
        if not DRAG_DROP_AVAILABLE:
            print("tkinterdnd2 が利用できません。ドラッグ＆ドロップの機能は無効化されました。")
            print("インストールするには: pip install tkinterdnd2")
            self.setup_file_selection_alternative()
            return
        
        try:
            # メインウィンドウのドラッグアンドドロップを有効にします
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_file_drop)
            
            # ルートの代わりにスクロール可能なフレームに視覚的なフィードバックを追加します
            self.drag_drop_label = ttk.Label(
                self.scrollable_frame, 
                text="drad＆drap.pdpackまたは.txtファイルはこちら",
                font=('Arial', 10, 'italic'),
                foreground='gray'
            )
            self.drag_drop_label.pack(pady=5)
            
        except Exception as e:
            print(f"ドラッグ＆ドロップの設定中にエラーが発生しました: {e}")
            self.setup_file_selection_alternative()

    def setup_file_selection_alternative(self):
        """ドラッグアンドドロップが利用できない場合の代替ファイルの選択をセットアップ"""
        try:
            # スクロール可能なフレームでファイル選択のフレームを作成します
            file_frame = ttk.LabelFrame(self.scrollable_frame, text="ファイルのインポート", padding=10)
            file_frame.pack(fill='x', padx=10, pady=5)
            
            # 情報ラベル
            info_label = ttk.Label(
                file_frame,
                text="構成またはデータベースファイルをインポート\n"
                     "対応形式: .pdpack（構成ファイル） | .txt（データベースファイル）",
                font=('Arial', 10),
                justify='center'
            )
            info_label.pack(pady=5)
            
            # ボタンフレーム
            buttons_frame = ttk.Frame(file_frame)
            buttons_frame.pack(pady=10)
            
            # 構成ボタンをインポートします
            import_config_btn = ttk.Button(
                buttons_frame,
                text="設定をインポートする（.pdpack）",
                command=self.import_configuration_file
            )
            import_config_btn.pack(side='left', padx=5)
            
            # [データベース]ボタンをインポートします
            import_db_btn = ttk.Button(
                buttons_frame,
                text="データベースのインポート（.txt）",
                command=self.import_database_file
            )
            import_db_btn.pack(side='left', padx=5)
            
        except Exception as e:
            print(f"ファイル選択の代替設定中にエラーが発生しました: {e}")

    def import_configuration_file(self):
        """.pdpack構成ファイルをインポートします"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="[構成ファイル]を選択します",
                filetypes=[
                    ("PDPackファイル", "*.pdpack"),
                    ("すべてのファイル", "*.*")
                ]
            )
            
            if file_path:
                self.process_dropped_file(file_path)
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("エラー", f"構成ファイルのインポート中にエラーが発生しました: {str(e)}")
    
    def import_database_file(self):
        """.txtデータベースファイルをインポートします"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="データベースファイルを選択します",
                filetypes=[
                    ("テキストファイル", "*.txt"),
                    ("すべてのファイル", "*.*")
                ]
            )
            
            if file_path:
                self.process_dropped_file(file_path)
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("エラー", f"データベースファイルのインポート中にエラーが発生しました: {str(e)}")
    
    def on_file_drop(self, event):
        """ドロップされたファイルを処理します"""
        files = self.root.tk.splitlist(event.data)
        
        if not files:
            return
        
        # 倍数が削除された場合の最初のファイルのみを処理します
        file_path = files[0]
        
        # ファイルを検証して処理します
        self.process_dropped_file(file_path)
    
    def process_dropped_file(self, file_path):
        """ドロップされたファイルを処理し、そのタイプを決定します"""
        try:
            if not os.path.isfile(file_path):
                messagebox.showerror("エラー", "無効なファイルパス")
                return
            
            file_extension = os.path.splitext(file_path)[1].lower()
            filename = os.path.basename(file_path)
            
            # [処理]ダイアログを表示します
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
                        "サポートされていないファイルタイプ", 
                        f"ファイルタイプ '{file_extension}' はサポートされていません。\n\n"
                        "対応形式:\n"
                        "• .pdpack（構成ファイル）\n"
                        "• .txt（データベースファイル）"
                    )
                    return
                
                processing_dialog.destroy()
                
                if success:
                    messagebox.showinfo(
                        "ファイルの読み込みに成功", 
                        f"{file_type} ファイルを読み込みました: {filename}"
                    )
                
            except Exception as e:
                processing_dialog.destroy()
                messagebox.showerror("処理エラー", f"ファイルの処理中にエラーが発生しました: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("エラー", f"ドロップされたファイルの処理中にエラーが発生しました: {str(e)}")
    
    def show_processing_dialog(self, message):
        """処理ダイアログを表示します"""
        dialog = tk.Toplevel(self.root)
        dialog.title("処理中...")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # ダイアログを中央に配置します
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (100 // 2)
        dialog.geometry(f"300x100+{x}+{y}")
        
        ttk.Label(dialog, text=message, font=('Arial', 10)).pack(expand=True)
        
        # ダイアログを表示するには更新します
        dialog.update()
        
        return dialog
    
    def load_pdpack_file(self, file_path):
        """.pdpackファイルをロードして検証します"""
        try:
            # ファイルコンテンツを読み取ります
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # 検証および復号化/解析
            if file_content.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                # 暗号化された形式
                encryptor = CustomEncryption()
                config = encryptor.decrypt_data(file_content)
                file_format = "encrypted"
                
            elif file_content.startswith(b'{'):
                # レガシーJSON形式
                json_string = file_content.decode('utf-8')
                config = json.loads(json_string)
                file_format = "legacy JSON"
                
            else:
                raise Exception("無効な .pdpack ファイル形式")

            # 構成構造を検証します
            if not self.validate_pdpack_config(config):
                raise Exception("無効な構成構造")
            
            # 読み込みについてユーザーに尋ねてください
            result = messagebox.askyesnocancel(
                "構成を読み込む",
                f"有効な .pdpack ファイルが見つかりました（{file_format} 形式）\n"
                f"曲数: {len(config.get('songs', []))}\n"
                f"パック名: {config.get('pack_name', '不明')}\n\n"
                "はい: 現在のデータを置き換える\n"
                "いいえ: 現在のデータと統合する\n"
                "キャンセル: 読み込まない"
            )
            
            if result is None:  # キャンセル
                return False
            elif result:  # はい - 交換してください
                self.pack_name_var.set(config.get('pack_name', ''))
                self.pack_name_jp_var.set(config.get('pack_name_jp', ''))
                self.songs = config.get('songs', [])
            else:  # いいえ - マージ
                if config.get('songs'):
                    self.songs.extend(config.get('songs', []))
            
            self.update_songs_display()
            return True
            
        except Exception as e:
            raise Exception(f".pdpack ファイルの読み込みに失敗しました: {str(e)}")
    
    def load_txt_file(self, file_path):
        """.txtデータベースファイルをロードして検証します"""
        try:
            # ファイルコンテンツを読み取り、検証します
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # mod_pv_db 形式を検証します
            if not self.validate_txt_format(content):
                raise Exception("無効な mod_pv_db.txt 形式")

            # ファイルコンテンツを解析します
            songs = self.parse_mod_pv_db_content(content)

            if not songs:
                raise Exception("データベースファイル内に有効な曲が見つかりませんでした")
            
            # 読み込みについてユーザーに尋ねてください
            result = messagebox.askyesnocancel(
                "データベースファイルをインポート",
                f"有効な mod_pv_db.txt ファイルが見つかりました\n"
                f"検出された曲数: {len(songs)}\n\n"
                "はい: 現在の曲を置き換える\n"
                "いいえ: 現在の曲に追加する\n"
                "キャンセル: インポートしない"
            )
            
            if result is None:  # キャンセル
                return False
            elif result:  # はい - 交換してください
                self.songs = songs
            else:  # いいえ - 追加
                self.songs.extend(songs)
            
            self.update_songs_display()
            return True
            
        except Exception as e:
            raise Exception(f".txt ファイルの読み込みに失敗しました: {str(e)}")
    
    def validate_pdpack_config(self, config):
        """.pdpack構成構造を検証します"""
        try:
            # 辞書のかどうかを確認してください
            if not isinstance(config, dict):
                return False
            
            # 必要なフィールドを確認してください
            if 'songs' not in config:
                return False
            
            # 曲の構造を検証します
            songs = config['songs']
            if not isinstance(songs, list):
                return False
            
            # 各曲を検証する（基本的な検証）
            for song in songs:
                if not isinstance(song, dict):
                    return False
                
                # 必要な曲フィールドを確認してください
                required_fields = ['pv_id', 'song_name', 'bpm']
                for field in required_fields:
                    if field not in song:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def validate_txt_format(self, content):
        """mod_pv_db.txt形式を検証します"""
        try:
            lines = content.strip().split('\n')
            
            # 少なくともいくつかの行を確認してください
            if len(lines) < 5:
                return False
            
            # 典型的なmod_pv_dbパターンを探します
            has_pv_entries = False
            has_valid_structure = False
            
            for line in lines:
                line = line.strip()
                
                # コメントと空の行をスキップします
                if not line or line.startswith('#'):
                    continue
                
                # key = valueフォーマットを確認してください
                if '=' not in line:
                    continue
                
                key, value = line.split('=', 1)
                key = key.strip()
                
                # PV_エントリを確認してください
                if key.startswith('pv_') and '.' in key:
                    has_pv_entries = True
                    
                    # 典型的な構造を確認してください
                    if any(pattern in key for pattern in [
                        '.song_name', '.bpm', '.difficulty', '.performer'
                    ]):
                        has_valid_structure = True
            
            return has_pv_entries and has_valid_structure
            
        except Exception:
            return False
    
    # ファイルタイプ検出ユーティリティ
    def detect_file_type(self, file_path):
        """ファイルタイプを検出して検証します"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdpack':
                # 最初の数バイトを読んで、形式を決定します
                with open(file_path, 'rb') as f:
                    header = f.read(50)
                
                if header.startswith(b'PDPACK_ENCRYPTED_V1\n'):
                    return 'pdpack_encrypted'
                elif header.startswith(b'{'):
                    return 'pdpack_json'
                else:
                    return 'pdpack_invalid'
                    
            elif file_extension == '.txt':
                # TXT形式のクイック検証
                with open(file_path, 'r', encoding='utf-8') as f:
                    sample = f.read(1000)  # 最初の1000文字を読んでください
                
                if 'pv_' in sample and '=' in sample:
                    return 'txt_modpvdb'
                else:
                    return 'txt_invalid'
            
            return 'unsupported'
            
        except Exception:
            return 'error'
    
    # 詳細なフィードバックを使用したファイル検証の強化
    def get_file_info(self, file_path):
        """ファイルに関する詳細情報を取得します"""
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
                # 復号化して情報を取得してみてください
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
                # JSONを解析して情報を取得します
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
                # txtを解析して情報を取得します
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # PVエントリをカウントします
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
    
    # ドラッグビジュアルフィードバックを強化しました
    def setup_drag_visual_feedback(self):
        """ドラッグアンドドロップ操作の視覚フィードバックをセットアップします"""
        try:
            # スクロール可能なフレームでドラッグアンドドロップ領域のフレームを作成します
            self.drag_drop_frame = ttk.LabelFrame(self.scrollable_frame, text="ファイルのインポート", padding=10)
            self.drag_drop_frame.pack(fill='x', padx=10, pady=5)
            
            # メインドラッグアンドドロップラベル
            self.drag_drop_label = ttk.Label(
                self.drag_drop_frame,
                text="ファイルをここにドラッグ＆ドロップしてください\n"
                     "対応形式: .pdpack（構成ファイル） | .txt（データベースファイル）",
                font=('Arial', 10),
                justify='center',
                foreground='gray'
            )
            self.drag_drop_label.pack(expand=True, fill='both', pady=10)
            
            # フィードバックのステータスラベル
            self.drag_status_label = ttk.Label(
                self.drag_drop_frame,
                text="ファイルを受信する準備ができました...",
                font=('Arial', 8),
                foreground='blue'
            )
            self.drag_status_label.pack()
            
            # 視覚的なフィードバックのためにドラッグイベントをバインドします
            if DRAG_DROP_AVAILABLE:
                self.root.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.root.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
        except Exception as e:
            print(f"視覚フィードバックの設定ができませんでした: {e}")
    
    def on_drag_enter(self, event):
        """ドラッグがウィンドウに入ると、視覚的なフィードバック"""
        try:
            self.drag_drop_label.configure(foreground='green')
            self.drag_status_label.configure(text="インポートするためにファイルをドロップします...", foreground='green')
        except:
            pass
        
    def on_drag_leave(self, event):
        """ドラッグがウィンドウを去るときの視覚的なフィードバック"""
        try:
            self.drag_drop_label.configure(foreground='gray')
            self.drag_status_label.configure(text="ファイルを受信する準備ができました...", foreground='blue')
        except:
            pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ProjectDivaModEditor()
    app.run()
