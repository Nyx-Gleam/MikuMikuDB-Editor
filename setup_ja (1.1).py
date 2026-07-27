from cx_Freeze import setup, Executable

__executables = [
    Executable("app_jp.py", base="Win32GUI", icon="icon.ico")
]

setup(
    name="エディタ",
    version="1.0",
    description="初音ミク『Project Diva Mega Mix+』mods用 mod_pv_db.txt ファイルエディタ",
    executables=__executables
)
