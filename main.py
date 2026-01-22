import ctypes
import os

def set_taskbar_icon():
    if os.name == 'nt':
        myappid = 'dreameDeck.1.1.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Funktion aufrufen
set_taskbar_icon()

from ui.main_window import StreamDeckGUI
import customtkinter as ctk


from config.colors import (CTK_ACCENT_DEFAULT)

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme(CTK_ACCENT_DEFAULT)
    
    app = StreamDeckGUI()
    app.wm_iconbitmap('app_icon.ico')
    app.mainloop()