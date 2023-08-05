import PyInstaller.__main__
import shutil
import os

print("Building the exe file...")
PyInstaller.__main__.run(
    [
        "src/main.py",
        "--onefile",
        "--clean",
        # '--noconsole',
        "--add-data",
        "src/auth;auth",
        "--name",
        "StashTabExporter",
        "--add-data",
        "assets/logo.ico;assets/logo.ico",
        "--add-data",
        "src/auth;auth",
        "--add-data",
        "src/systray.py;.",
        "--add-data",
        "src/poeApi.py;.",
        "--add-data",
        "src/confighandler;confighandler",
        "--add-data",
        "src/logger.py;.",
        "--add-data",
        "src/stashFormatter.py;.",
        "--icon=assets/logo.ico",
        "--hidden-import=auth",
        "--hidden-import=uuid",
        "--hidden-import=requests",
        "--hidden-import=systray",
        "--hidden-import=webbrowser",
        "--hidden-import=pystray",
        "--hidden-import=socket",
        "--hidden-import=PIL.Image",
        "--hidden-import=os",
        "--hidden-import=yaml",
        "--hidden-import=config",
        "--hidden-import=poeApi",
        "--hidden-import=logging" "--hidden-import=logger",
        "--hidden-import=logging.handlers",
        "--hidden-import=re",
    ]
)
print("Cleaning...")
shutil.rmtree("build")
print("Copying additional resources...")
os.makedirs("dist/assets", exist_ok=True)
os.makedirs("dist/data", exist_ok=True)
os.makedirs("dist/logs", exist_ok=True)
shutil.copy("assets/logo.png", "dist/assets/logo.png")
shutil.copy("assets/logo.ico", "dist/assets/logo.ico")
shutil.copy("config.yaml", "dist/config.yaml")
shutil.copy("assets/patch_exilence_handle.cmd", "dist/patch_exilence_handle.cmd")
