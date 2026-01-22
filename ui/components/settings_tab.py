# ui/settings_tab.py
import customtkinter as ctk

from config.systemConfig import ANI_NAMES, ANIM_SPEED


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
        update_speed,
        **kwargs
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
            values=ANI_NAMES,
            command=on_save_anim,
        )
        self.anim_menu.pack(pady=10)

        self.update_speed_callback = update_speed

        sframe = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🏃 Animations-Geschwindigkeit:", font=("Arial", 16)).pack(pady=(20, 5))

        # Wir lesen den Wert direkt aus der Variable in der systemConfig.py
        initial_val = ANIM_SPEED

        self.speed_slider = ctk.CTkSlider(
            frame, 
            from_=0.5, 
            to=0.01, 
            command=self.update_speed_label
        )
        self.speed_slider.set(initial_val)
        self.speed_slider.pack(pady=10)

        self.speed_value_label = ctk.CTkLabel(
            frame,
            text="", 
            font=("Arial", 12, "italic"),
            text_color="gray",
        )
        self.speed_value_label.pack(pady=(0, 20))
        
        # Initiales Label-Update
        self.update_speed_label(initial_val)

    def update_speed_label(self, v):
        # Umrechnung für die Anzeige (0.5 -> 1%, 0.01 -> 100%)
        percent = int(((0.5 - v) / (0.49)) * 99 + 1)
        self.speed_value_label.configure(text=f"Geschwindigkeit: {percent}%")
        
        if self.update_speed_callback:
            self.update_speed_callback(v)