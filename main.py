from ui.main_window import StreamDeckGUI
import customtkinter as ctk

from config.colors import (CTK_ACCENT_DEFAULT)

if __name__ == "__main__":
    # Optional: Theme hier setzen
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme(CTK_ACCENT_DEFAULT)
    
    app = StreamDeckGUI()
    app.mainloop()