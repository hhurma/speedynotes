import os
import json
import sys

# PyInstaller bundle için kullanıcının home dizinine yaz
if hasattr(sys, '_MEIPASS'):
    SETTINGS_DIR = os.path.expanduser('~/Library/Application Support/SpeedyNotes')
    SETTINGS_PATH = os.path.join(SETTINGS_DIR, 'settings.json')
else:
    SETTINGS_PATH = 'config/settings.json'

# Ayarlardan notes/settings yolunu oku

def get_data_dir():
    if not os.path.exists(SETTINGS_PATH):
        return 'config'
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings.get('data_dir', 'config')
    except Exception:
        return 'config'

def set_data_dir(path):
    # PyInstaller bundle için config klasörü oluştur
    if hasattr(sys, '_MEIPASS'):
        config_dir = SETTINGS_DIR
    else:
        config_dir = 'config'
    os.makedirs(config_dir, exist_ok=True)
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = {}
        settings['data_dir'] = path
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass 