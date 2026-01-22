import json
from pathlib import Path

import customtkinter as ctk

from config.keys_config import KEY_MAP, COLOR_MAP, ICON_MAP, MEDIA_KEYS_CODES
from config.systemConfig import BAUD_RATE, TIMEOUT_PICO, ANI_OPT
from modules.serial_handler import SerialHandler

from config.colors import (
    TEXT_DARK,
    STATUS_OK,
    STATUS_WARN,
    STATUS_INFO,
    CTK_ACCENT_DEFAULT,
    THEMES
)

from config.systemConfig import (
    ANIM_SPEED
)

from ui.sidebar import NavSidebar

from ui.components.settings_tab import SettingsTab
from ui.components.profile_tab import ProfileTab


BASE_DIR = Path(__file__).resolve().parents[1]  # .../DremdeckPro
SETTINGS_FILE = BASE_DIR / "config" / "gui_settings.json"


class StreamDeckGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hex Deck Pro - Workspace")
        self.geometry("1150x850")

        self.load_gui_settings()

        # Serial
        self.serial = SerialHandler(baud_rate=BAUD_RATE, timeout=TIMEOUT_PICO)

        # State
        self.selected_idx: int | None = None
        self.REV_KEY = {v: k for k, v in KEY_MAP.items()}

        # --- Layout ---
        self.nav_sidebar = NavSidebar(self, on_profile=self.show_profile, on_settings=self.show_settings)
        self.nav_sidebar.pack(side="left", fill="y")

        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(side="right", fill="both", expand=True)

        # --- Tabs als Komponenten ---
        self.profile_tab = ProfileTab(
            self.content_container,
            color_map=COLOR_MAP,
            get_appearance_mode=ctk.get_appearance_mode,
            on_select_button=self.select,
            on_save_key=self.save_k,
            on_save_color=self.save_c,
            on_save_mod=self.save_mod,
            on_update_brightness=self.update_bright,
        )
        self.tab_profile = self.profile_tab
        self.fill_lists()

        self.settings_tab = SettingsTab(
            self.content_container,
            get_current_mode=lambda: ctk.get_appearance_mode(),
            get_saved_accent=self.get_saved_accent,
            on_change_theme=self.change_theme,
            on_change_accent=self.change_accent,
            on_save_anim=self.save_anim,
            update_speed=self.update_ani_speed
        )
        self.tab_settings = self.settings_tab

        # Start
        self.show_profile()
        self.after(100, self.auto_connect)

    
  
    @property
    def btns(self):
        return self.profile_tab.btns

    @property
    def key_btns(self):
        return self.profile_tab.key_btns

   
    def show_profile(self):
        self.tab_settings.pack_forget()
        self.tab_profile.pack(fill="both", expand=True)
        self.nav_sidebar.set_active("profile")

    def show_settings(self):
        self.tab_profile.pack_forget()
        self.tab_settings.pack(fill="both", expand=True)
        self.nav_sidebar.set_active("settings")

    # -------------------------
    # Settings helper
    # -------------------------
    def get_saved_accent(self) -> str:
        try:
            saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return saved.get("color_theme", CTK_ACCENT_DEFAULT)
        except Exception:
            return CTK_ACCENT_DEFAULT

    # -------------------------
    # Settings JSON
    # -------------------------
    def load_gui_settings(self):
        if SETTINGS_FILE.exists():
            try:
                settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                ctk.set_appearance_mode(settings.get("appearance_mode", "System"))
                ctk.set_default_color_theme(settings.get("color_theme", CTK_ACCENT_DEFAULT))
            except Exception:
                ctk.set_appearance_mode("System")
        else:
            ctk.set_appearance_mode("System")

    def save_gui_settings(self, key, value):
        settings = {}
        if SETTINGS_FILE.exists():
            try:
                settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except Exception:
                settings = {}
        settings[key] = value
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    # -------------------------
    # Theme / Accent
    # -------------------------
    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)
        self.save_gui_settings("appearance_mode", new_theme)
        self.after(10, self.update_button_colors)

    def change_accent(self, new_accent):
        self.save_gui_settings("color_theme", new_accent)
        # Hinweis: erst nach Neustart aktiv
        self.profile_tab.set_status("Akzent gespeichert! Bitte neustarten.", STATUS_INFO )

    def update_button_colors(self):
        theme = "dark" if ctk.get_appearance_mode() == "Dark" else "light"
        mode = ctk.get_appearance_mode()
        text_color = THEMES[theme]["text"]

        # Große Buttons
        for b in self.btns:
            b.configure(text_color=text_color)

        # Listen Buttons
        for btn in self.key_btns.values():
            btn.configure(text_color=text_color)

        # Status label (optional)
        if mode == "Light":
            self.profile_tab.status_label.configure(
                text_color=TEXT_DARK if not self.serial.is_connected else STATUS_OK
            )

    # -------------------------
    # Pico / Serial
    # -------------------------
    def auto_connect(self):
        res = self.serial.scan_and_connect()
        if res:
            device, config_line = res
            self.profile_tab.set_status(f"Verbunden: {device}", STATUS_OK)
            self.load_pico_config_from_data(config_line)
            return
        self.after(2000, self.auto_connect)

    def load_pico_config_from_data(self, raw_data: str):
        try:
            data = raw_data.replace("CONFIG:", "").split(";")

            # Brightness
            self.profile_tab.set_brightness(int(data[-1]))

            # Button configs
            for i in range(len(self.btns)):
                parts = data[i].split(",")
                if len(parts) == 3:
                    c_name, kc, mod = parts
                    kc_int = int(kc)

                    self.btns[i].current_key = self.REV_KEY.get(kc_int, "F13")
                    self.btns[i].current_color = c_name
                    self.btns[i].current_mod = int(mod)

                    rgb = COLOR_MAP.get(c_name, (50, 50, 50))
                    fg = "#3b3b3b" if c_name == "Aus" else ("#%02x%02x%02x" % rgb)

                    self.btns[i].configure(
                        fg_color=fg,
                        text=ICON_MAP.get(kc_int, "⌨"),
                    )
        except Exception:
            pass

    def send(self, cmd, idx, val):
        # Wir prüfen, ob der SerialHandler verbunden ist
        if self.serial.is_connected:
            try:
                # Das Format für den Pico: "BEFEHL:INDEX:WERT\n"
                msg = f"{cmd}:{idx}:{val}\n"
                # Wir nutzen die write-Methode deines SerialHandlers
                self.serial.ser.write(msg.encode())
            except Exception as e:
                print(f"Sende-Fehler: {e}")
    # -------------------------
    # Lists / Selection / Save
    # -------------------------
    def fill_lists(self):
        mode = ctk.get_appearance_mode()
        theme = "dark" if ctk.get_appearance_mode() == "Dark" else "light"
        text_color = THEMES[theme]["text"]

        self.profile_tab.clear_key_buttons()

        for name, code in sorted(KEY_MAP.items()):
            parent = self.profile_tab.media_scroll if code in MEDIA_KEYS_CODES else self.profile_tab.standard_scroll
            self.profile_tab.add_key_button(parent, name, text_color)

    def select(self, idx: int):
        self.selected_idx = idx

        self.profile_tab.set_selected_border(idx)

        curr_key = self.btns[idx].current_key
        self.highlight_key_in_list(curr_key)

        self.profile_tab.set_color_menu(self.btns[idx].current_color)

        mod = self.btns[idx].current_mod
        self.profile_tab.set_mod_vars(bool(mod & 1), bool(mod & 2), bool(mod & 4))

        if KEY_MAP.get(curr_key, 0) in MEDIA_KEYS_CODES:
            self.profile_tab.show_mod_frame(False)
        else:
            self.profile_tab.show_mod_frame(True)

    def highlight_key_in_list(self, key_name: str):
        for name, btn in self.key_btns.items():
            btn.configure(fg_color=CTK_ACCENT_DEFAULT if name == key_name else "transparent")

    def save_k(self, v): 
        if self.selected_idx is None: return
        
        code = KEY_MAP[v]
        self.btns[self.selected_idx].current_key = v
        self.btns[self.selected_idx].configure(text=ICON_MAP.get(code, "⌨"))
        self.highlight_key_in_list(v)

        if code in MEDIA_KEYS_CODES:
            self.profile_tab.show_mod_frame(False)
            self.send("SET_MOD", self.selected_idx, 0) # Index hinzugefügt
            self.btns[self.selected_idx].current_mod = 0
        else:
            self.profile_tab.show_mod_frame(True)

        self.send("SET_KEY", self.selected_idx, code) # Einmalig mit korrekten Argumenten

    def save_mod(self):
        if self.selected_idx is None: return
        val = ( (1 if self.profile_tab.ctrl_var.get() else 0) + 
                (2 if self.profile_tab.shift_var.get() else 0) + 
                (4 if self.profile_tab.alt_var.get() else 0) )

        self.btns[self.selected_idx].current_mod = val
        # Korrektur: idx hinzufügen
        self.send("SET_MOD", self.selected_idx, val)

    def save_c(self, v: str):
        if self.selected_idx is not None:
            self.send("SET_COLOR", self.selected_idx, v)

        self.btns[self.selected_idx].current_color = v
        rgb = COLOR_MAP.get(v, (50, 50, 50))
        fg = "#3b3b3b" if v == "Aus" else ("#%02x%02x%02x" % rgb)
        self.btns[self.selected_idx].configure(fg_color=fg)
        self.send("SET_COLOR", v)

    def update_bright(self, v):
        self.send("SET_BRIGHTNESS", 0, int(v))

    def save_anim(self, v: str):
        mapping = ANI_OPT
        anim_id = mapping.get(v, 0)
        # Korrektur: idx 0 für globale Animation hinzufügen
        self.send("SET_ANIM", 0, anim_id) 
        self.save_gui_settings("hardware_animation", v)

    def update_ani_speed(self, v):
        ms_value = int(float(v) * 1000) 
        self.send("SET_SPEED", 0, ms_value)

    def on_program_start(self):
    # Board beim Start auf den Wert aus der Config setzen
        ms_value = int(config.ANIM_SPEED * 1000)
        self.send("SET_SPEED", 0, ms_value)

    def update_ani_speed(self, v):
        # Wert ans Board senden, wenn der Slider bewegt wird
        ms_value = int(float(v) * 1000)
        self.send("SET_SPEED", 0, ms_value)
