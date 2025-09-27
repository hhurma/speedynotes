import json
import os
from datetime import datetime

class NoteMemory:
    def __init__(self):
        self.notes = []  # Her not: {"title": ..., "content": ..., "datetime": ...}

    def add_note(self, title="Yeni Not", content="", **kwargs):
        note = {
            "title": title,
            "content": content,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        # Ek alanları (örn. external_path) nota işle
        for k, v in kwargs.items():
            note[k] = v
        self.notes.append(note)
        return len(self.notes) - 1

    def update_note(self, index, content=None, title=None):
        if 0 <= index < len(self.notes):
            if content is not None:
                self.notes[index]["content"] = content
            if title is not None:
                self.notes[index]["title"] = title

    def get_note(self, index):
        if 0 <= index < len(self.notes):
            return self.notes[index]
        return {"title": "", "content": "", "datetime": ""}

    def remove_note(self, index):
        if 0 <= index < len(self.notes):
            del self.notes[index]

    def note_count(self):
        return len(self.notes)

    def save_to_file(self, filepath):
        try:
            # Dış dosya sekmelerini (external_path atanmış notları) kalıcı depoya yazma
            notes_to_persist = [n for n in self.notes if 'external_path' not in n]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(notes_to_persist, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False

    def load_from_file(self, filepath):
        if not os.path.exists(filepath):
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.notes = json.load(f)
        except Exception:
            self.notes = [] 