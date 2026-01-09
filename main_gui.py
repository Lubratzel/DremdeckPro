import customtkinter as ctk
import serial
import serial.tools.list_ports
import time
import json
import os
from keys_config import KEY_MAP, COLOR_MAP, ICON_MAP

# DATEIPFAD FÜR SETTINGS
SETTINGS_FILE = "gui_settings.json"
BAUD_RATE = 115200
REV_KEY = {v: k for k, v in KEY_MAP.items()}
MEDIA_KEYS_CODES = [127, 128, 129, 205, 206, 207, 181, 111, 112]

class StreamDeckGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hex Deck Pro - Workspace")
        self.geometry("1150x850")
        
        self.load_gui_settings()

        self.ser = None
        self.selected_idx = None

        # --- HAUPT LAYOUT ---
        # 1. Rechte Sidebar für die Navigation (Tabs Ersatz)
        self.nav_sidebar = ctk.CTkFrame(self, width=120, corner_radius=0)
        self.nav_sidebar.pack(side="left", fill="y")
        
        # 2. Container für den Inhalt (wechselt zwischen Profile und Settings)
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(side="right", fill="both", expand=True)

        # Navigations-Buttons in der Sidebar
        self.btn_profile = ctk.CTkButton(self.nav_sidebar, text="🙍 Profile", 
                                         command=self.show_profile, corner_radius=0, height=50)
        self.btn_profile.pack(fill="x", pady=(20, 5), padx=5)

        self.btn_settings = ctk.CTkButton(self.nav_sidebar, text="⚙ Settings", 
                                          command=self.show_settings, corner_radius=0, height=50)
        self.btn_settings.pack(fill="x", pady=5, padx=5)

        # --- TABS INITIALISIEREN ---
        # Wir erstellen zwei Frames, die wir einfach übereinander legen oder verstecken
        self.tab_profile = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_settings = ctk.CTkFrame(self.content_container, fg_color="transparent")

        # Setup Funktionen aufrufen (wie vorher)
        self.setup_profile_tab()
        self.setup_settings_tab()

        # Start-Tab anzeigen
        self.show_profile()

        self.after(100, self.auto_connect)

    def show_profile(self):
        """Zeigt den Profil-Tab und versteckt Settings"""
        self.tab_settings.pack_forget()
        self.tab_profile.pack(fill="both", expand=True)
        self.btn_profile.configure(fg_color=("gray75", "gray25")) # Optisches Feedback
        self.btn_settings.configure(fg_color="transparent")

    def show_settings(self):
        """Zeigt den Settings-Tab und versteckt Profile"""
        self.tab_profile.pack_forget()
        self.tab_settings.pack(fill="both", expand=True)
        self.btn_settings.configure(fg_color=("gray75", "gray25"))
        self.btn_profile.configure(fg_color="transparent")

    def load_gui_settings(self):
        """Liest die Theme-Einstellungen aus der JSON Datei"""
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
        """Speichert eine Einstellung in die JSON Datei"""
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
            except: pass
        
        settings[key] = value
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)

    def setup_profile_tab(self):
        # Sidebar (Rechts)
        self.sidebar = ctk.CTkFrame(self.tab_profile, width=320)
        self.sidebar.pack(side="right", fill="y", padx=10, pady=10)
        
        # Hauptbereich (Links)
        self.main_area = ctk.CTkFrame(self.tab_profile, fg_color="transparent")
        self.main_area.pack(side="left", fill="both", expand=True)

        # Container für die Buttons, exakt mittig
        self.button_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.button_container.place(relx=0.5, rely=0.5, anchor="center")

        # Sidebar Elemente (Status, Listen, etc.)
        self.status_label = ctk.CTkLabel(self.sidebar, text="Suche Pico...", text_color="orange")
        self.status_label.pack(pady=10)

        # ... (Deine Scroll-Listen und Menüs in der Sidebar) ...
        ctk.CTkLabel(self.sidebar, text="⌨ Standard Tasten").pack()
        self.standard_scroll = ctk.CTkScrollableFrame(self.sidebar, width=250, height=200)
        self.standard_scroll.pack(pady=5)
        
        ctk.CTkLabel(self.sidebar, text="🪟 Windows Funktionen").pack()
        self.media_scroll = ctk.CTkScrollableFrame(self.sidebar, width=250, height=150)
        self.media_scroll.pack(pady=5)

        self.key_btns = {}
        self.fill_lists()


        ctk.CTkLabel(self.sidebar, text="🎨 Farbe auswählen:", font=("Arial", 13, "bold")).pack(pady=(15, 0))
        self.c_menu = ctk.CTkComboBox(self.sidebar, values=list(COLOR_MAP.keys()), command=self.save_c, state="readonly")
        self.c_menu.pack(pady=10)

        self.mod_frame = ctk.CTkFrame(self.sidebar, fg_color="#2b2b2b", corner_radius=10)
        self.ctrl_var = ctk.BooleanVar(); self.shift_var = ctk.BooleanVar(); self.alt_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self.mod_frame, text="STRG", variable=self.ctrl_var, command=self.save_mod).pack(pady=2)
        ctk.CTkCheckBox(self.mod_frame, text="SHIFT", variable=self.shift_var, command=self.save_mod).pack(pady=2)
        ctk.CTkCheckBox(self.mod_frame, text="ALT", variable=self.alt_var, command=self.save_mod).pack(pady=2)

        ctk.CTkLabel(self.sidebar, text="☀️ Helligkeit:", font=("Arial", 13, "bold")).pack(side="bottom", pady=(10, 0))
        self.bright_slider = ctk.CTkSlider(self.sidebar, from_=0, to=255, command=self.update_bright)
        self.bright_slider.pack(side="bottom", pady=20)

        for col in range(6):
            self.button_container.grid_columnconfigure(col, weight=1, uniform="group1")

        grid_positions = [
            (0, 1), (0, 3),         # Oben
            (1, 0), (1, 2), (1, 4), # Mitte (Versetzt)
            (2, 1), (2, 2)          # Unten (Hier Korrektur auf 1 und 3 für Symmetrie)
        ]
        
        # Falls die untere Reihe im Bild auch versetzt sein soll wie die obere:
        # Nutze (2, 1) und (2, 3) statt (2, 1) und (2, 2)
        grid_positions[5] = (2, 1)
        grid_positions[6] = (2, 3)

        self.btns = []
        text_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"

        for i, (r, c) in enumerate(grid_positions):
            b = ctk.CTkButton(self.button_container, 
                              text="?", 
                              width=140, 
                              height=140, 
                              corner_radius=10, 
                              font=("Arial", 60), 
                              text_color=text_color,
                              command=lambda idx=i: self.select(idx))
            
            # Wichtig: sticky="nsew" sorgt dafür, dass der Button den Platz im Grid voll ausfüllt
            b.grid(row=r, column=c, columnspan=2, padx=10, pady=10, sticky="nsew")
            
            b.current_key, b.current_color, b.current_mod = "F13", "Aus", 0
            self.btns.append(b)
            

    def change_theme(self, new_theme):
        """Wechselt das Theme und erzwingt sofortige Farbanpassung der Schrift"""
        ctk.set_appearance_mode(new_theme)
        self.save_gui_settings("appearance_mode", new_theme)
        
        # Winzige Verzögerung, damit CustomTkinter den Mode intern aktualisieren kann
        self.after(10, self.update_button_colors)
            
    def update_button_colors(self):
        """Prüft den aktuellen Modus und färbt alle Texte um"""
        # ctk.get_appearance_mode() gibt jetzt den tatsächlichen Status (Light/Dark)
        current_actual_mode = ctk.get_appearance_mode()
        new_text_color = "white" if current_actual_mode == "Dark" else "black"
        
        # 1. Große Hex-Buttons anpassen
        for b in self.btns:
            b.configure(text_color=new_text_color)
            
        # 2. Buttons in den Scroll-Listen anpassen
        for btn in self.key_btns.values():
            btn.configure(text_color=new_text_color)
            
        # 3. Status Label anpassen (optional, falls es sonst verschwindet)
        if current_actual_mode == "Light":
            self.status_label.configure(text_color="black" if self.ser is None else "green")

    
    def setup_settings_tab(self):
        """Hier wird das Aussehen der GUI angepasst und gespeichert"""
        frame = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="GUI Design & Akzentfarbe", font=("Arial", 24, "bold")).pack(pady=20)

        # 1. Theme Auswahl (Dark/Light)
        ctk.CTkLabel(frame, text="Modus (Hell/Dunkel):", font=("Arial", 16)).pack(pady=(20, 5))
        current_mode = ctk.get_appearance_mode()
        self.theme_menu = ctk.CTkOptionMenu(frame, values=["System", "Dark", "Light"], 
                                            command=self.change_theme)
        self.theme_menu.set(current_mode)
        self.theme_menu.pack(pady=10)

        # 2. Akzentfarbe Auswahl
        ctk.CTkLabel(frame, text="Akzentfarbe (Buttons/Slider):", font=("Arial", 16)).pack(pady=(20, 5))
        # Standard-Themen von CustomTkinter: "blue", "green", "dark-blue"
        self.accent_menu = ctk.CTkOptionMenu(frame, values=["blue", "green", "dark-blue"], 
                                             command=self.change_accent)
        
        # Wir versuchen den aktuellen Wert aus den Settings zu laden
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved_accent = json.load(f).get("color_theme", "blue")
                self.accent_menu.set(saved_accent)
        except:
            self.accent_menu.set("blue")
            
        self.accent_menu.pack(pady=10)

        ctk.CTkLabel(frame, text="💡 Hinweis: Die Akzentfarbe wird beim nächsten Start aktiv.", 
                     font=("Arial", 12, "italic"), text_color="gray").pack(pady=20)
        
        ctk.CTkLabel(frame, text="Hardware Animation (Pico):", font=("Arial", 16)).pack(pady=(20, 5))
        
        self.anim_menu = ctk.CTkOptionMenu(frame, 
                                           values=["Aus", "Welle", "Atmen"], 
                                           command=self.save_anim)
        self.anim_menu.pack(pady=10)

    def save_anim(self, v):
        # Map den Namen auf die Zahl für den Pico
        mapping = {"Aus": 0, "Welle": 1, "Atmen": 2}
        anim_id = mapping.get(v, 0)
        
        # Sende den Befehl (selected_idx ist hier egal, wir nehmen 0)
        self.send("SET_ANIM", anim_id)
        
        # Speichere die Wahl auch in deiner gui_settings.json
        self.save_gui_settings("hardware_animation", v)

    def change_accent(self, new_accent):
        """Speichert die Akzentfarbe. CustomTkinter benötigt leider einen Neustart dafür."""
        self.save_gui_settings("color_theme", new_accent)
        # Optional: Dem User zeigen, dass er neustarten muss
        self.status_label.configure(text="Akzent gespeichert! Bitte neustarten.", text_color="yellow")
    # --- LOGIK FUNKTIONEN (Gleich geblieben) ---


    def auto_connect(self):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            try:
                test_ser = serial.Serial(p.device, BAUD_RATE, timeout=0.5)
                time.sleep(0.5)
                test_ser.write(b"GET_CONFIG\n")
                res = test_ser.readline().decode().strip()
                if res.startswith("CONFIG:"):
                    self.ser = test_ser
                    self.status_label.configure(text=f"Verbunden: {p.device}", text_color="green")
                    self.load_pico_config_from_data(res)
                    return
                test_ser.close()
            except: continue
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
                    rgb = COLOR_MAP.get(c_name, (50,50,50))
                    self.btns[i].configure(fg_color='#%02x%02x%02x' % rgb if c_name != "Aus" else "#3b3b3b", text=ICON_MAP.get(int(kc), "⌨"))
        except: pass

    def fill_lists(self):
        # Bestimme Farbe für Listen-Text
        mode = ctk.get_appearance_mode()
        l_text_color = "white" if mode == "Dark" else "black"

        for name, code in sorted(KEY_MAP.items()):
            parent = self.media_scroll if code in MEDIA_KEYS_CODES else self.standard_scroll
            btn = ctk.CTkButton(parent, 
                                text=name, 
                                fg_color="transparent", 
                                text_color=l_text_color, # Hier dynamisch
                                anchor="w", 
                                command=lambda n=name: self.save_k(n))
            btn.pack(fill="x", padx=2, pady=1)
            self.key_btns[name] = btn

    def select(self, idx):
        self.selected_idx = idx
        for i, b in enumerate(self.btns): b.configure(border_width=3 if i==idx else 0, border_color="#1f538d")
        curr_key = self.btns[idx].current_key
        self.highlight_key_in_list(curr_key)
        self.c_menu.set(self.btns[idx].current_color)
        mod = self.btns[idx].current_mod
        self.ctrl_var.set(bool(mod & 1)); self.shift_var.set(bool(mod & 2)); self.alt_var.set(bool(mod & 4))
        if KEY_MAP.get(curr_key, 0) in MEDIA_KEYS_CODES: self.mod_frame.pack_forget()
        else: self.mod_frame.pack(pady=20, padx=10)

    def highlight_key_in_list(self, key_name):
        for name, btn in self.key_btns.items(): btn.configure(fg_color="#1f538d" if name == key_name else "transparent")

    def save_k(self, v):
        if self.selected_idx is None: return
        code = KEY_MAP[v]
        self.btns[self.selected_idx].current_key = v
        self.btns[self.selected_idx].configure(text=ICON_MAP.get(code, "⌨"))
        self.highlight_key_in_list(v)
        if code in MEDIA_KEYS_CODES:
            self.mod_frame.pack_forget(); self.send("SET_MOD", 0); self.btns[self.selected_idx].current_mod = 0
        else: self.mod_frame.pack(pady=20, padx=10)
        self.send("SET_KEY", code)

    def save_mod(self):
        val = (1 if self.ctrl_var.get() else 0) + (2 if self.shift_var.get() else 0) + (4 if self.alt_var.get() else 0)
        self.btns[self.selected_idx].current_mod = val
        self.send("SET_MOD", val)

    def save_c(self, v):
        self.btns[self.selected_idx].current_color = v
        rgb = COLOR_MAP.get(v, (50, 50, 50))
        self.btns[self.selected_idx].configure(fg_color='#%02x%02x%02x' % rgb if v != "Aus" else "#3b3b3b")
        self.send("SET_COLOR", v)

    def update_bright(self, v): self.send("SET_BRIGHTNESS", int(v))

    def send(self, cmd, val):
        if self.ser and self.ser.is_open:
            try: self.ser.write(f"{cmd}:{self.selected_idx}:{val}\n".encode())
            except: pass

if __name__ == "__main__":
    app = StreamDeckGUI()
    app.mainloop()

