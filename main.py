import os
import json

def ensure_config_files():
    os.makedirs('config', exist_ok=True)
    notes_path = os.path.join('config', 'notes.json')
    settings_path = os.path.join('config', 'settings.json')

    if not os.path.exists(notes_path):
        with open(notes_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    if not os.path.exists(settings_path):
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

ensure_config_files()

from gui.main_gui import main

if __name__ == "__main__":
    main() 