# ui/profile_tab.py
import customtkinter as ctk


class ProfileTab(ctk.CTkFrame):
    """
    Enthält den kompletten Profile-Tab (Layout + Widgets).
    Logik (Serial senden, speichern, etc.) bleibt im Main Window und wird über Callbacks aufgerufen.
    """

    def __init__(
        self,
        master,
        *,
        color_map: dict,
        get_appearance_mode,
        on_select_button,       # (idx:int) -> None
        on_save_key,            # (name:str) -> None
        on_save_color,          # (name:str) -> None
        on_save_mod,            # () -> None
        on_update_brightness,   # (value:float) -> None
    ):
        super().__init__(master, fg_color="transparent")

        self.color_map = color_map
        self.get_appearance_mode = get_appearance_mode

        # Callbacks
        self.on_select_button = on_select_button
        self.on_save_key = on_save_key
        self.on_save_color = on_save_color
        self.on_save_mod = on_save_mod
        self.on_update_brightness = on_update_brightness

        # Public-ish references (Main Window kann darauf zugreifen)
        self.btns = []
        self.key_btns = {}

        # Vars
        self.ctrl_var = ctk.BooleanVar()
        self.shift_var = ctk.BooleanVar()
        self.alt_var = ctk.BooleanVar()

        self._build_ui()

    def _build_ui(self):
        # Right sidebar
        self.sidebar = ctk.CTkFrame(self, width=320)
        self.sidebar.pack(side="right", fill="y", padx=10, pady=10)

        # Main area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True)

        self.button_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.button_container.place(relx=0.5, rely=0.5, anchor="center")

        # Sidebar Widgets
        self.status_label = ctk.CTkLabel(self.sidebar, text="Suche Pico...", text_color="orange")
        self.status_label.pack(pady=10)

        ctk.CTkLabel(self.sidebar, text="⌨ Standard Tasten").pack()
        self.standard_scroll = ctk.CTkScrollableFrame(self.sidebar, width=250, height=200)
        self.standard_scroll.pack(pady=5)

        ctk.CTkLabel(self.sidebar, text="🪟 Windows Funktionen").pack()
        self.media_scroll = ctk.CTkScrollableFrame(self.sidebar, width=250, height=150)
        self.media_scroll.pack(pady=5)

        # Color picker
        ctk.CTkLabel(self.sidebar, text="🎨 Farbe auswählen:", font=("Arial", 13, "bold")).pack(pady=(15, 0))
        self.c_menu = ctk.CTkComboBox(
            self.sidebar,
            values=list(self.color_map.keys()),
            command=self.on_save_color,
            state="readonly",
        )
        self.c_menu.pack(pady=10)

        # Modifiers
        self.mod_frame = ctk.CTkFrame(self.sidebar, fg_color="#2b2b2b", corner_radius=10)
        ctk.CTkCheckBox(self.mod_frame, text="STRG", variable=self.ctrl_var, command=self.on_save_mod).pack(pady=2)
        ctk.CTkCheckBox(self.mod_frame, text="SHIFT", variable=self.shift_var, command=self.on_save_mod).pack(pady=2)
        ctk.CTkCheckBox(self.mod_frame, text="ALT", variable=self.alt_var, command=self.on_save_mod).pack(pady=2)

        # Brightness
        ctk.CTkLabel(self.sidebar, text="☀️ Helligkeit:", font=("Arial", 13, "bold")).pack(
            side="bottom", pady=(10, 0)
        )
        self.bright_slider = ctk.CTkSlider(self.sidebar, from_=0, to=255, command=self.on_update_brightness)
        self.bright_slider.pack(side="bottom", pady=20)

        # Button grid
        for col in range(6):
            self.button_container.grid_columnconfigure(col, weight=1, uniform="group1")

        grid_positions = [
            (0, 1), (0, 3),
            (1, 4), (1, 2), (1, 0),
            (2, 1), (2, 3),
        ]

        text_color = "white" if self.get_appearance_mode() == "Dark" else "black"

        for i, (r, c) in enumerate(grid_positions):
            b = ctk.CTkButton(
                self.button_container,
                text="?",
                width=140,
                height=140,
                corner_radius=10,
                font=("Arial", 60),
                text_color=text_color,
                command=lambda idx=i: self.on_select_button(idx),
            )
            b.grid(row=r, column=c, columnspan=2, padx=10, pady=10, sticky="nsew")
            b.current_key, b.current_color, b.current_mod = "F13", "Aus", 0
            self.btns.append(b)

    # ---- Helpers, die Main Window nutzen kann ----
    def set_status(self, text: str, color: str):
        self.status_label.configure(text=text, text_color=color)

    def set_brightness(self, value: int):
        self.bright_slider.set(value)

    def set_selected_border(self, idx: int):
        for i, b in enumerate(self.btns):
            b.configure(border_width=3 if i == idx else 0, border_color="#1f538d")

    def show_mod_frame(self, show: bool):
        if show:
            self.mod_frame.pack(pady=20, padx=10)
        else:
            self.mod_frame.pack_forget()

    def set_mod_vars(self, ctrl: bool, shift: bool, alt: bool):
        self.ctrl_var.set(ctrl)
        self.shift_var.set(shift)
        self.alt_var.set(alt)

    def set_color_menu(self, color_name: str):
        self.c_menu.set(color_name)

    def clear_key_buttons(self):
        for _, btn in self.key_btns.items():
            btn.destroy()
        self.key_btns.clear()

    def add_key_button(self, parent, name: str, text_color: str):
        btn = ctk.CTkButton(
            parent,
            text=name,
            fg_color="transparent",
            text_color=text_color,
            anchor="w",
            command=lambda n=name: self.on_save_key(n),
        )
        btn.pack(fill="x", padx=2, pady=1)
        self.key_btns[name] = btn
        return btn
