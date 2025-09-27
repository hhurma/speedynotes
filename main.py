import os
import json
from helpers.config_helper import get_data_dir, set_data_dir
from gui.first_run_wizard import FirstRunWizard
from PyQt6.QtWidgets import QApplication
import sys

def ensure_config_files():
    data_dir = get_data_dir()
    try:
        os.makedirs(data_dir, exist_ok=True)
    except Exception:
        # Yazma izni yoksa sessizce geç (dış dosya modu hâlâ çalışır)
        return
    notes_path = os.path.join(data_dir, 'notes.json')
    settings_path = os.path.join(data_dir, 'settings.json')

    try:
        if not os.path.exists(notes_path):
            with open(notes_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    try:
        if not os.path.exists(settings_path):
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def run_first_time_wizard_if_needed(skip=False):
    data_dir = get_data_dir()
    notes_path = os.path.join(data_dir, 'notes.json')
    settings_path = os.path.join(data_dir, 'settings.json')
    if skip:
        return
    if not os.path.exists(notes_path) or not os.path.exists(settings_path) or data_dir == 'config':
        app = QApplication.instance() or QApplication([])
        wizard = FirstRunWizard()
        if wizard.exec() == 1 and wizard.get_selected_dir():
            set_data_dir(wizard.get_selected_dir())
            ensure_config_files()

def parse_initial_paths(argv):
    # argv[0] betik yoludur; sonrakiler dosya yolları olabilir
    candidates = argv[1:]
    initial_paths = [p for p in candidates if isinstance(p, str) and os.path.isfile(p)]
    return initial_paths

if __name__ == "__main__":
    initial_paths = parse_initial_paths(sys.argv)
    # Dosya argümanı varsa sihirbazı atla ve kalıcı depolamayı devre dışı bırak
    skip_wizard = len(initial_paths) > 0
    run_first_time_wizard_if_needed(skip=skip_wizard)
    if not skip_wizard:
        ensure_config_files()

    from gui.main_gui import main
    # Kalıcı depolama: sadece argüman yoksa etkin
    main(initial_paths if initial_paths else None)