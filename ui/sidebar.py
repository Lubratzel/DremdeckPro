# ui/sidebar.py
import customtkinter as ctk


class NavSidebar(ctk.CTkFrame):
    def __init__(self, master, on_profile, on_settings):
        super().__init__(master, width=120, corner_radius=0)
        self.pack_propagate(False)

        self.btn_profile = ctk.CTkButton(
            self, text="🙍 Profile", command=on_profile, corner_radius=0, height=50
        )
        self.btn_profile.pack(fill="x", pady=(20, 5), padx=5)

        self.btn_settings = ctk.CTkButton(
            self, text="⚙ Settings", command=on_settings, corner_radius=0, height=50
        )
        self.btn_settings.pack(fill="x", pady=5, padx=5)

    def set_active(self, which: str):
        # which: "profile" oder "settings"
        if which == "profile":
            self.btn_profile.configure(fg_color=("gray75", "gray25"))
            self.btn_settings.configure(fg_color="transparent")
        else:
            self.btn_settings.configure(fg_color=("gray75", "gray25"))
            self.btn_profile.configure(fg_color="transparent")
