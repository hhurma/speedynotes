import os
import json

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
    os.makedirs('config', exist_ok=True)
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