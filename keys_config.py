# Gemeinsame Konfiguration für PC und Pico

# Mapping von Namen zu HID-Nummern
# 4-29: A-Z | 30-39: 1-0 | 58-69: F1-F12 | 104-115: F13-F24
# 127-207: Medientasten
# Gemeinsame Konfiguration für PC und Pico
# HID Usage IDs – Keyboard/Keypad Page (0x07)
# A-Z: 4–29
# 1–9: 30–38 | 0: 39
# F1–F12: 58–69
# F13–F24: 104–115

KEY_MAP = {
    
    "Stumm (Mute)": 127,
    "Lauter": 128,
    "Leiser": 129,
    "Play/Pause": 205,
    "Nächster Titel": 206,
    "Vorheriger Titel": 207,
    "Stop": 181,
    "Helligkeit +": 111,
    "Helligkeit -": 112,

}

# ----------------------------
# Buchstaben A–Z
# ----------------------------
for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", start=4):
    KEY_MAP[ch] = i

# ----------------------------
# Zahlen 1–9
# ----------------------------
for n in range(1, 10):
    KEY_MAP[str(n)] = 29 + n

# ----------------------------
# Zahl 0
# ----------------------------
KEY_MAP["0"] = 39

# ----------------------------
# F-Tasten F1–F12
# ----------------------------
for n in range(1, 13):
    KEY_MAP[f"F{n}"] = 57 + n

# ----------------------------
# F-Tasten F13–F24
# ----------------------------
for n in range(13, 20):  # range(13, 20) geht von 13 bis 19
    KEY_MAP[f"F{n}"] = 91 + n  # F13=104 ... F19=110


ICON_MAP = {
    128: "🔊", 129: "🔉", 127: "🔇",
    205: "⏯", 206: "⏭", 207: "⏮",
    "default": "⌨"
}


COLOR_MAP = {
    "Weiß": (255, 255, 255),
    "Rot": (255, 0, 0),
    "Grün": (0, 255, 0),
    "Blau": (0, 0, 255),
    "Gelb": (255, 255, 0),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Orange": (255, 165, 0),
    "Lila": (128, 0, 128),
    "Aus": (0, 0, 0) 
}


REVERSE_MAP = {v: k for k, v in KEY_MAP.items()}