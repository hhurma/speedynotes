import logging
import os
import sys


def _get_log_path() -> str:
    app_name = 'SpeedyNotes'
    try:
        if os.name == 'nt':
            base = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA') or os.path.expanduser('~')
            log_dir = os.path.join(base, app_name, 'logs')
        elif sys.platform == 'darwin':
            log_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Logs', app_name)
        else:
            base = os.getenv('XDG_CACHE_HOME', os.path.join(os.path.expanduser('~'), '.cache'))
            log_dir = os.path.join(base, app_name.lower())
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, 'app.log')
    except Exception:
        # Son çare: geçici dosya dizini
        import tempfile
        return os.path.join(tempfile.gettempdir(), f'{app_name.lower()}_app.log')


def _configure_logging():
    try:
        log_path = _get_log_path()
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[file_handler]
        )
    except Exception:
        # Dosyaya yazılamazsa en azından sessizce konsola yaz (veya default root handler)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )


_configure_logging()


def get_logger(name):
    return logging.getLogger(name)