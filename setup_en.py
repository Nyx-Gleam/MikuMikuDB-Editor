from cx_Freeze import setup, Executable

__executables = [
    Executable("app_en.py", base="Win32GUI", icon="icon.ico")
]

setup(
    name="Editor",
    version="1.0",
    description="mod_pv_db.txt file generator for Hatsune Miku: Project Diva Mega Mix+ mods",
    executables=__executables
)
