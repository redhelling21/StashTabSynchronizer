import pystray
import sys
from PIL import Image

def exit(icon, query):
    icon.stop()
    sys.exit()

def run_systray():
    image = Image.open("assets/logo.png")
    icon = pystray.Icon("GFG", image, "GeeksforGeeks", menu=pystray.Menu(
        pystray.MenuItem("Exit", exit)))
    icon.run_detached()
    return icon