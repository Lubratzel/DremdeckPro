# ui/settings_tab.py
import customtkinter as ctk


class SettingsTab(ctk.CTkFrame):
   
    def __init__(
        self,
        master,
        *,
        get_current_mode,
        get_saved_accent,
        on_change_theme,
        on_change_accent,
        on_save_anim,
    ):
        super().__init__(master, fg_color="transparent")

        # UI bauen
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="GUI Design & Akzentfarbe", font=("Arial", 24, "bold")).pack(pady=20)

        # Theme
        ctk.CTkLabel(frame, text="Modus (Hell/Dunkel):", font=("Arial", 16)).pack(pady=(20, 5))
        self.theme_menu = ctk.CTkOptionMenu(
            frame,
            values=["System", "Dark", "Light"],
            command=on_change_theme,
        )
        self.theme_menu.set(get_current_mode())
        self.theme_menu.pack(pady=10)

        # Accent
        ctk.CTkLabel(frame, text="Akzentfarbe (Buttons/Slider):", font=("Arial", 16)).pack(pady=(20, 5))
        self.accent_menu = ctk.CTkOptionMenu(
            frame,
            values=["blue", "green", "dark-blue"],
            command=on_change_accent,
        )
        self.accent_menu.set(get_saved_accent())
        self.accent_menu.pack(pady=10)

        ctk.CTkLabel(
            frame,
            text="💡 Hinweis: Die Akzentfarbe wird beim nächsten Start aktiv.",
            font=("Arial", 12, "italic"),
            text_color="gray",
        ).pack(pady=20)

        # Animation
        ctk.CTkLabel(frame, text="Hardware Animation (Pico):", font=("Arial", 16)).pack(pady=(20, 5))
        self.anim_menu = ctk.CTkOptionMenu(
            frame,
            values=["Aus", "Welle", "Atmen"],
            command=on_save_anim,
        )
        self.anim_menu.pack(pady=10)
