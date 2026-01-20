import customtkinter as ctk
import serial
import serial.tools.list_ports
import time
import json
import os
import requests
import threading
from keys_config import KEY_MAP, COLOR_MAP, ICON_MAP

# DATEIPFAD FÜR SETTINGS
SETTINGS_FILE = "gui_settings.json"
BAUD_RATE = 115200
REV_KEY = {v: k for k, v in KEY_MAP.items()}
MEDIA_KEYWORDS = ["LAUTER", "LEISER", "STUMM", "PLAY", "PAUSE", "NÄCHSTER", "VORHERIGER", "STOP", "HELLIGKEIT"]
SYSTEM_KEYWORDS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
                   "F13", "F14", "F15", "F16", "F17", "F18", "F19", "WIN", "ALT", "STRG", "SHIFT"]


class StreamDeckGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hex Deck Pro - Workspace")
        self.geometry("1150x850")

        self.load_gui_settings()

        self.ser = None
        self.selected_idx = None

        # --- HAUPT LAYOUT ---
        self.nav_sidebar = ctk.CTkFrame(self, width=120, corner_radius=0)
        self.nav_sidebar.pack(side="left", fill="y")

        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(side="right", fill="both", expand=True)

        # Navigations-Buttons
        self.btn_profile = ctk.CTkButton(self.nav_sidebar, text="🙍 Profile",
                                         command=self.show_profile, corner_radius=0, height=50)
        self.btn_profile.pack(fill="x", pady=(20, 5), padx=5)

        self.btn_settings = ctk.CTkButton(self.nav_sidebar, text="⚙ Settings",
                                          command=self.show_settings, corner_radius=0, height=50)
        self.btn_settings.pack(fill="x", pady=5, padx=5)

        # Tabs
        self.tab_profile = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_settings = ctk.CTkFrame(self.content_container, fg_color="transparent")

        self.setup_profile_tab()
        self.setup_settings_tab()
        self.fill_lists()
        self.show_profile()

        self.after(100, self.auto_connect)
        threading.Thread(target=self.listen_to_pico, daemon=True).start()

    def show_profile(self):
        self.tab_settings.pack_forget()
        self.tab_profile.pack(fill="both", expand=True)
        self.btn_profile.configure(fg_color=("gray75", "gray25"))
        self.btn_settings.configure(fg_color="transparent")

    def listen_to_pico(self):
        while True:
            if self.ser and self.ser.is_open:
                try:
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode().strip()
                        if line.startswith("PRESSED:"):
                            idx = int(line.split(":")[1])
                            self.trigger_webhook(idx)
                except:
                    pass
            time.sleep(0.01)

    def trigger_webhook(self, idx):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    webhooks = settings.get("webhooks", {})
                    config = webhooks.get(str(idx), {})

                    if isinstance(config, dict) and config.get("active", False):
                        url = config.get("url", "")
                        if url and url.startswith("http"):
                            def make_request():
                                try:
                                    r = requests.post(url, timeout=5)
                                    print(f"Webhook {idx} Erfolg! Status: {r.status_code}")
                                except Exception as e:
                                    print(f"Webhook Fehler: {e}")

                            threading.Thread(target=make_request, daemon=True).start()
            except Exception as e:
                print(f"Fehler beim Webhook-Trigger: {e}")

    def toggle_webhook_ui(self):
        if self.webhook_active_var.get():
            self.webhook_entry.pack(pady=5)
            self.btn_save_webhook.pack(pady=5)
        else:
            self.webhook_entry.pack_forget()
            self.btn_save_webhook.pack_forget()

    def save_webhook(self):
        if self.selected_idx is None: return
        url = self.webhook_entry.get()
        active = self.webhook_active_var.get()

        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
            except:
                pass

        if "webhooks" not in settings: settings["webhooks"] = {}
        settings["webhooks"][str(self.selected_idx)] = {"url": url, "active": active}

        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)

        self.toggle_webhook_ui()  # UI aktualisieren
        self.status_label.configure(text="Gespeichert!", text_color="green")

    def show_settings(self):
        self.tab_profile.pack_forget()
        self.tab_settings.pack(fill="both", expand=True)
        self.btn_settings.configure(fg_color=("gray75", "gray25"))
        self.btn_profile.configure(fg_color="transparent")

    def load_gui_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    ctk.set_appearance_mode(settings.get("appearance_mode", "System"))
                    ctk.set_default_color_theme(settings.get("color_theme", "blue"))
            except:
                ctk.set_appearance_mode("System")
        else:
            ctk.set_appearance_mode("System")

    def save_gui_settings(self, key, value):
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
            except:
                pass
        settings[key] = value
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)

    def setup_profile_tab(self):
        self.profile_container = ctk.CTkFrame(self.tab_profile, fg_color="transparent")
        self.profile_container.pack(fill="both", expand=True)
        self.main_area = ctk.CTkFrame(self.profile_container, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True)
        self.sidebar = ctk.CTkFrame(self.profile_container, width=320, border_width=2, border_color=("#1f538d"))

        # Button Grid (Hex)
        self.button_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.button_container.place(relx=0.5, rely=0.45, anchor="center")
        grid_positions = [(0, 1), (0, 3), (1, 4), (1, 2), (1, 0), (2, 1), (2, 3)]
        self.btns = []
        for i, (r, c) in enumerate(grid_positions):
            b = ctk.CTkButton(self.button_container, text="?", width=140, height=140, corner_radius=40,
                              font=("Arial", 60), command=lambda idx=i: self.select(idx))
            b.grid(row=r, column=c, columnspan=2, padx=10, pady=10)
            b.current_key, b.current_color, b.current_mod = "F13", "Aus", 0
            self.btns.append(b)

        # --- SIDEBAR SCROLLBEREICHE (SORTIERT) ---
        # 1. Normale Tasten
        ctk.CTkLabel(self.sidebar, text="⌨ Standard Tasten", font=("Arial", 13, "bold")).pack(pady=(10, 0))
        self.standard_scroll = ctk.CTkScrollableFrame(self.sidebar, width=250, height=150)
        self.standard_scroll.pack(pady=5, padx=10)

        # 2. Windows / System Tasten
        ctk.CTkLabel(self.sidebar, text="🪟 Windows / System", font=("Arial", 13, "bold")).pack(pady=(10, 0))
        self.system_scroll = ctk.CTkScrollableFrame(self.sidebar, width=250, height=150)
        self.system_scroll.pack(pady=5, padx=10)

        # 3. Media Tasten
        ctk.CTkLabel(self.sidebar, text="🎵 Media Steuerung", font=("Arial", 13, "bold")).pack(pady=(10, 0))
        self.media_scroll = ctk.CTkScrollableFrame(self.sidebar, width=250, height=100)
        self.media_scroll.pack(pady=5, padx=10)

        # Rest der Sidebar (Farbe, Modifikatoren, Webhook)
        ctk.CTkLabel(self.sidebar, text="🎨 Farbe:", font=("Arial", 13, "bold")).pack(pady=(10, 0))
        self.c_menu = ctk.CTkComboBox(self.sidebar, values=list(COLOR_MAP.keys()), command=self.save_c, state="readonly")
        self.c_menu.pack(pady=5)

        self.webhook_active_var = ctk.BooleanVar(value=False)
        self.webhook_checkbox = ctk.CTkCheckBox(self.sidebar, text="Webhook nutzen", variable=self.webhook_active_var, command=self.save_webhook)
        self.webhook_checkbox.pack(pady=10)
        self.webhook_entry = ctk.CTkEntry(self.sidebar, placeholder_text="http://...", width=250)
        self.btn_save_webhook = ctk.CTkButton(self.sidebar, text="URL Speichern", command=self.save_webhook)

        # Status & Brightness
        self.bottom_bar = ctk.CTkFrame(self.main_area, height=80, fg_color="transparent")
        self.bottom_bar.pack(side="bottom", fill="x", padx=20, pady=10)
        self.status_label = ctk.CTkLabel(self.bottom_bar, text="Suche Pico...", text_color="orange")
        self.status_label.pack(side="left", padx=20)
        self.bright_slider = ctk.CTkSlider(self.bottom_bar, from_=0, to=255, width=300, command=self.update_bright)
        self.bright_slider.pack(side="right", padx=20)

    def animate_sidebar_open(self):
        current_x = 1.3
        self.sidebar.place(relx=current_x, rely=0, anchor="ne", relheight=1.0)

        def step():
            nonlocal current_x
            if current_x > 1.0:
                current_x -= 0.04;
                self.sidebar.place(relx=current_x);
                self.after(5, step)

        step()

    def hide_sidebar(self):
        if self.sidebar.winfo_manager() == "place":
            current_x = 1.0

            def step():
                nonlocal current_x
                if current_x < 1.4:
                    current_x += 0.05;
                    self.sidebar.place(relx=current_x);
                    self.after(5, step)
                else:
                    self.sidebar.place_forget();
                    self.selected_idx = None
                    for b in self.btns: b.configure(border_width=0)

            step()

    def select(self, idx):
        if self.sidebar.winfo_manager() != "place": self.animate_sidebar_open()
        self.selected_idx = idx
        for i, b in enumerate(self.btns): b.configure(border_width=4 if i == idx else 0, border_color="#1f538d")

        # Webhook laden
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    config = json.load(f).get("webhooks", {}).get(str(idx), {})
                    self.webhook_entry.delete(0, "end")
                    if isinstance(config, dict):
                        self.webhook_entry.insert(0, config.get("url", ""))
                        self.webhook_active_var.set(config.get("active", False))
            except:
                pass
        self.toggle_webhook_ui()

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme);
        self.save_gui_settings("appearance_mode", new_theme)
        self.after(10, self.update_button_colors)

    def update_button_colors(self):
        mode = ctk.get_appearance_mode()
        new_color = "white" if mode == "Dark" else "black"
        for b in self.btns: b.configure(text_color=new_color)

    def setup_settings_tab(self):
        frame = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text="Design & Hardware", font=("Arial", 24, "bold")).pack(pady=20)
        self.theme_menu = ctk.CTkOptionMenu(frame, values=["System", "Dark", "Light"], command=self.change_theme)
        self.theme_menu.pack(pady=10)
        self.anim_menu = ctk.CTkOptionMenu(frame, values=["Aus", "Welle", "Atmen", "Scanner", "Blinken"],
                                           command=self.save_anim)
        self.anim_menu.pack(pady=10)

    def save_anim(self, v):
        mapping = {"Aus": 0, "Welle": 1, "Atmen": 2, "Scanner": 3, "Blinken": 4}
        self.send("SET_ANIM", mapping.get(v, 0));
        self.save_gui_settings("hardware_animation", v)

    def auto_connect(self):
        for p in serial.tools.list_ports.comports():
            try:
                test_ser = serial.Serial(p.device, BAUD_RATE, timeout=0.5)
                time.sleep(0.5);
                test_ser.write(b"GET_CONFIG\n")
                res = test_ser.readline().decode().strip()
                if res.startswith("CONFIG:"):
                    self.ser = test_ser
                    self.status_label.configure(text=f"Verbunden: {p.device}", text_color="green")
                    self.load_pico_config_from_data(res);
                    return
                test_ser.close()
            except:
                continue
        self.after(2000, self.auto_connect)

    def load_pico_config_from_data(self, raw_data):
        try:
            data = raw_data.replace("CONFIG:", "").split(";")
            self.bright_slider.set(int(data[-1]))
            for i in range(len(self.btns)):
                parts = data[i].split(",")
                if len(parts) == 3:
                    c_name, kc, mod = parts
                    self.btns[i].current_key = REV_KEY.get(int(kc), "F13")
                    self.btns[i].current_color = c_name
                    self.btns[i].current_mod = int(mod)
                    rgb = COLOR_MAP.get(c_name, (50, 50, 50))
                    self.btns[i].configure(fg_color='#%02x%02x%02x' % rgb if c_name != "Aus" else "#3b3b3b",
                                           text=ICON_MAP.get(int(kc), "⌨"))
        except:
            pass

    def fill_lists(self):
        """Verteilt Tasten basierend auf Schlüsselwörtern"""
        for frame in [self.standard_scroll, self.system_scroll, self.media_scroll]:
            for widget in frame.winfo_children(): widget.destroy()

        l_text_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"

        for name in sorted(KEY_MAP.keys()):
            name_up = name.upper()

            # 1. Check Media
            if any(k in name_up for k in MEDIA_KEYWORDS):
                target = self.media_scroll
            # 2. Check System
            elif any(k in name_up for k in SYSTEM_KEYWORDS):
                target = self.system_scroll
            # 3. Rest ist Standard
            else:
                target = self.standard_scroll

            btn = ctk.CTkButton(target, text=name, fg_color="transparent", text_color=l_text_color,
                                anchor="w", height=24, command=lambda n=name: self.save_k(n))
            btn.pack(fill="x", padx=2, pady=1)

    def save_k(self, v):
        if self.selected_idx is None: return
        code = KEY_MAP[v];
        self.btns[self.selected_idx].current_key = v
        self.btns[self.selected_idx].configure(text=ICON_MAP.get(code, "⌨"));
        self.send("SET_KEY", code)

    def save_mod(self):
        val = (1 if self.ctrl_var.get() else 0) + (2 if self.shift_var.get() else 0) + (4 if self.alt_var.get() else 0)
        self.btns[self.selected_idx].current_mod = val;
        self.send("SET_MOD", val)

    def save_c(self, v):
        self.btns[self.selected_idx].current_color = v
        rgb = COLOR_MAP.get(v, (50, 50, 50))
        self.btns[self.selected_idx].configure(fg_color='#%02x%02x%02x' % rgb if v != "Aus" else "#3b3b3b")
        self.send("SET_COLOR", v)

    def update_bright(self, v):
        self.send("SET_BRIGHTNESS", int(v))

    def send(self, cmd, val):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{cmd}:{self.selected_idx}:{val}\n".encode())
            except:
                pass


if __name__ == "__main__":
    app = StreamDeckGUI()
    app.mainloop()