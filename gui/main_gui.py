from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QTextEdit, QVBoxLayout, QWidget, QInputDialog, QToolBar, QMessageBox, QLabel, QSplashScreen, QTabBar, QToolButton, QHBoxLayout, QDialog, QLineEdit, QListWidget, QListWidgetItem, QDialogButtonBox, QPushButton
from PyQt6.QtGui import QIcon, QAction, QClipboard, QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QSize, QMimeData, QObject, QEvent
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QFileDialog
import sys
import os
import qtawesome as qta
import time
import json

# Ana proje dizinini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from helpers.note_memory_helper import NoteMemory
from utils.logger import get_logger
from helpers.config_helper import get_data_dir
from helpers.translate_helper import gemini_translate, is_text_turkish

# Highlighter'ları import et
try:
    from .python_highlighter import PythonSyntaxHighlighter
    from .html_highlighter import HtmlSyntaxHighlighter
    from .css_highlighter import CssSyntaxHighlighter
except ImportError:
    # Eğer relative import çalışmazsa absolute import dene
    from python_highlighter import PythonSyntaxHighlighter
    from html_highlighter import HtmlSyntaxHighlighter
    from css_highlighter import CssSyntaxHighlighter

class PlainTextEdit(QTextEdit):
    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        cursor = self.textCursor()
        if cursor.hasSelection():
            cevir_action = QAction('Çevir', self)
            cevir_action.triggered.connect(self._cevir_secili_metni)
            menu.addAction(cevir_action)
        menu.exec(event.globalPos())

    def _cevir_secili_metni(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            secili = cursor.selectedText()
            try:
                hedef_dil = 'en' if is_text_turkish(secili) else 'tr'
                ceviri = gemini_translate(secili, hedef_dil)
            except Exception as e:
                ceviri = f"Çeviri hatası: {e}"
            # Sonucu bir pencere içinde göster
            dialog = QDialog(self)
            dialog.setWindowTitle("Çeviri Sonucu")
            layout = QVBoxLayout(dialog)
            ceviri_label = QLabel(ceviri)
            ceviri_label.setWordWrap(True)
            layout.addWidget(ceviri_label)
            btn_layout = QHBoxLayout()
            kopyala_btn = QPushButton("Panoya Kopyala")
            kopyala_btn.clicked.connect(lambda: QApplication.clipboard().setText(ceviri))
            btn_layout.addWidget(kopyala_btn)
            kapat_btn = QPushButton("Kapat")
            kapat_btn.clicked.connect(dialog.accept)
            btn_layout.addWidget(kapat_btn)
            layout.addLayout(btn_layout)
            dialog.exec()

class TabBarDoubleClickFilter(QObject):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback

    def eventFilter(self, obj, event):
        logger = get_logger("TabBarDoubleClickFilter")
        logger.info(f"eventFilter: event type: {event.type()}")
        if event.type() == QEvent.Type.MouseButtonDblClick:
            mouse_event = event  # type: QMouseEvent
            tabbar = obj
            idx = tabbar.tabAt(mouse_event.pos())
            logger.info(f"Çift tıklandı, idx: {idx}")
            self.callback(idx)
            return True
        return False

class CustomTabBar(QTabBar):
    def __init__(self, double_click_callback, parent=None):
        super().__init__(parent)
        self.double_click_callback = double_click_callback
        self._last_click_time = 0
        self._last_click_idx = -2
        self.plus_icon = qta.icon('fa5s.plus', color='green')

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        if index == self.count() - 1 and self.is_plus_tab():
            size.setWidth(size.width() + 10)
        return size

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_plus_tab():
            from PyQt6.QtWidgets import QStylePainter, QStyleOptionTab
            painter = QStylePainter(self)
            opt = QStyleOptionTab()
            self.initStyleOption(opt, self.count() - 1)
            rect = self.tabRect(self.count() - 1)
            icon_size = 18
            icon_rect = rect.adjusted((rect.width() - icon_size)//2, (rect.height() - icon_size)//2, -(rect.width() - icon_size)//2, -(rect.height() - icon_size)//2)
            self.plus_icon.paint(painter, icon_rect)

    def mousePressEvent(self, event):
        idx = self.tabAt(event.pos())
        now = time.time()
        if self.is_plus_tab() and idx == self.count() - 1:
            self.double_click_callback(-1)  # -1 ile yeni not aç
            return
        if idx == self._last_click_idx and (now - self._last_click_time) < 0.4:
            self.double_click_callback(idx)
            self._last_click_time = 0
            self._last_click_idx = -2
        else:
            self._last_click_time = now
            self._last_click_idx = idx
        super().mousePressEvent(event)

    def is_plus_tab(self):
        return self.count() > 0 and self.tabText(self.count() - 1) == ""

    def tabButton(self, index, position):
        # + sekmesinde x butonunu gizle
        if self.is_plus_tab() and index == self.count() - 1:
            return None
        return super().tabButton(index, position)

class NotDefteriGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speedy Notes")
        self.resize(600, 600)
        self.setWindowIcon(QIcon("resources/speedy_notes_icon.svg"))
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._sekme_kapat_indeksli)
        self.tabs.tabBar().tabMoved.connect(self._sekme_tasi)
        # + butonu
        self.plus_button = QToolButton()
        self.plus_button.setIcon(qta.icon('fa5s.plus', color='green'))
        self.plus_button.setAutoRaise(True)
        self.plus_button.clicked.connect(self._yeni_not)
        self.tabs.setCornerWidget(self.plus_button, Qt.Corner.TopRightCorner)
        self.setCentralWidget(self.tabs)
        self.memory = NoteMemory()
        self.tema = "aydinlik"
        self.logger = get_logger("NotDefteriGUI")
        self.notes_path = os.path.join(get_data_dir(), 'notes.json')
        self.settings_path = os.path.join(get_data_dir(), 'settings.json')
        self.memory.load_from_file(self.notes_path)
        self._setup_toolbar()
        self.tabs.currentChanged.connect(self._sekme_degisti)
        self.tabbar_filter = TabBarDoubleClickFilter(self.tabs.tabBar(), self._sekme_baslik_duzenle)
        self.tabs.tabBar().installEventFilter(self.tabbar_filter)
        self._notlari_yukle()
        self._center_window()
        self.tabs.setStyleSheet("""
QTabBar::tab:selected { font-weight: bold; }
""")

    def _setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        yeni_icon = qta.icon('fa5s.plus', color='green')
        yeni_aksiyon = QAction(yeni_icon, "Yeni Not", self)
        yeni_aksiyon.triggered.connect(self._yeni_not)
        toolbar.addAction(yeni_aksiyon)
        
        toolbar.addSeparator()        # Dosya Aç (.py, .txt, .html, .css)
        open_file_icon = qta.icon('fa5s.folder-open', color='blue')
        open_file_action = QAction(open_file_icon, "Dosya Aç (.py, .txt, .html, .css)", self)
        open_file_action.triggered.connect(self._open_file)
        toolbar.addAction(open_file_action)
        self.addAction(open_file_action)

        # Dosyayı Kaydet
        save_file_icon = qta.icon('fa5s.save', color='green')
        save_file_action = QAction(save_file_icon, "Dosyayı Kaydet", self)
        save_file_action.triggered.connect(self._save_current_file)
        toolbar.addAction(save_file_action)
        self.addAction(save_file_action)

        sil_icon = qta.icon('fa5s.trash', color='orange')
        sil_aksiyon = QAction(sil_icon, "Notu Sil", self)
        sil_aksiyon.triggered.connect(self._notu_sil)
        toolbar.addAction(sil_aksiyon)

        kopyala_icon = qta.icon('fa5s.copy', color='blue')
        kopyla_aksiyon = QAction(kopyala_icon, "Notu Kopyala", self)
        kopyla_aksiyon.triggered.connect(self._notu_kopyala)
        toolbar.addAction(kopyla_aksiyon)
        
        toolbar.addSeparator()

        # Bold
        bold_icon = qta.icon('fa5s.bold', color='#1976D2')  # Mavi
        bold_action = QAction(bold_icon, "Kalın (Ctrl+B)", self)
        bold_action.setShortcut('Ctrl+B')
        bold_action.triggered.connect(self._bold_text)
        toolbar.addAction(bold_action)
        self.addAction(bold_action)

        # Italic
        italic_icon = qta.icon('fa5s.italic', color='#388E3C')  # Yeşil
        italic_action = QAction(italic_icon, "İtalik (Ctrl+I)", self)
        italic_action.setShortcut('Ctrl+I')
        italic_action.triggered.connect(self._italic_text)
        toolbar.addAction(italic_action)
        self.addAction(italic_action)

        # Strikethrough
        strike_icon = qta.icon('fa5s.strikethrough', color='#F44336')  # Kırmızı
        strike_action = QAction(strike_icon, "Üstü Çizili (Ctrl+Shift+S)", self)
        strike_action.setShortcut('Ctrl+Shift+S')
        strike_action.triggered.connect(self._strike_text)
        toolbar.addAction(strike_action)
        self.addAction(strike_action)

        font_decrease_icon = qta.icon('fa5s.text-height', color='#F44336')
        font_decrease_action = QAction(font_decrease_icon, "Yazı Boyutunu Azalt (Ctrl+Shift+Aşağı)", self)
        font_decrease_action.setShortcut('Ctrl+Shift+Down')
        font_decrease_action.triggered.connect(self._font_decrease)
        toolbar.addAction(font_decrease_action)
        self.addAction(font_decrease_action)
        
        # Yazı boyutu artır/azalt ikonları
        font_increase_icon = qta.icon('fa5s.text-height', color='#1976D2')
        font_increase_action = QAction(font_increase_icon, "Yazı Boyutunu Artır (Ctrl+Shift+Yukarı)", self)
        font_increase_action.setShortcut('Ctrl+Shift+Up')
        font_increase_action.triggered.connect(self._font_increase)
        toolbar.addAction(font_increase_action)
        self.addAction(font_increase_action)

        
        
        toolbar.addSeparator()

        # Kes
        cut_icon = qta.icon('fa5s.cut', color='#FF9800')  # Turuncu
        cut_action = QAction(cut_icon, "Kes (Ctrl+X)", self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self._cut_text)
        toolbar.addAction(cut_action)
        self.addAction(cut_action)

        # Kopyala
        copy_icon = qta.icon('fa5s.copy', color='#0097A7')  # Camgöbeği
        copy_action = QAction(copy_icon, "Kopyala (Ctrl+C)", self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self._copy_text)
        toolbar.addAction(copy_action)
        self.addAction(copy_action)

        # Yapıştır
        paste_icon = qta.icon('fa5s.paste', color='#7B1FA2')  # Mor
        paste_action = QAction(paste_icon, "Yapıştır (Ctrl+V)", self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self._paste_text)
        toolbar.addAction(paste_action)
        self.addAction(paste_action)

        toolbar.addSeparator()

        # Undo
        undo_icon = qta.icon('fa5s.undo', color='#43A047')  # Yeşil
        undo_action = QAction(undo_icon, "Geri Al (Ctrl+Z)", self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self._undo_text)
        undo_action.setEnabled(False)
        toolbar.addAction(undo_action)
        self.addAction(undo_action)
        self.undo_action = undo_action

        # Redo
        redo_icon = qta.icon('fa5s.redo', color='#43A047')  # Yeşil
        redo_action = QAction(redo_icon, "Yinele (Ctrl+Y)", self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self._redo_text)
        redo_action.setEnabled(False)
        toolbar.addAction(redo_action)
        self.addAction(redo_action)
        self.redo_action = redo_action

        # En sona separator ekle
        toolbar.addSeparator()

        # Ctrl+F kısayolu ile arama
        arama_icon = qta.icon('fa5s.search', color='blue')
        arama_aksiyon = QAction(arama_icon, "Notlarda Ara", self)
        arama_aksiyon.triggered.connect(self._arama_ac)
        toolbar.addAction(arama_aksiyon)
        
        # Tema değiştir ve hakkında ikonları en sona
        tema_icon = qta.icon('fa5s.adjust', color='purple')
        self.tema_aksiyon = QAction(tema_icon, "Tema Değiştir", self)
        self.tema_aksiyon.triggered.connect(self._tema_toggle)
        toolbar.addAction(self.tema_aksiyon)      

        info_icon = qta.icon('fa5s.info-circle', color='gray')
        info_aksiyon = QAction(info_icon, "Hakkında", self)
        info_aksiyon.triggered.connect(self._show_about)
        toolbar.addAction(info_aksiyon)        # Ctrl+N kısayolu ile yeni not
        yeni_shortcut = QAction(self)
        yeni_shortcut.setShortcut('Ctrl+N')
        yeni_shortcut.triggered.connect(self._yeni_not)
        self.addAction(yeni_shortcut)

        # Ctrl+O kısayolu ile dosya aç
        open_shortcut = QAction(self)
        open_shortcut.setShortcut('Ctrl+O')
        open_shortcut.triggered.connect(self._open_file)
        self.addAction(open_shortcut)

        # Ctrl+S kısayolu ile dosya kaydet
        save_shortcut = QAction(self)
        save_shortcut.setShortcut('Ctrl+S')
        save_shortcut.triggered.connect(self._save_current_file)
        self.addAction(save_shortcut)

        # PDF'e Aktar
        pdf_icon = qta.icon('fa5s.file-pdf', color='red')
        pdf_action = QAction(pdf_icon, "Tüm Notları PDF'e Aktar", self)
        pdf_action.triggered.connect(self._export_all_notes_pdf)
        toolbar.addAction(pdf_action)
        self.addAction(pdf_action)

        # İçe Aktar
        import_icon = qta.icon('fa5s.file-import', color='orange')
        import_action = QAction(import_icon, "Notları İçe Aktar", self)
        import_action.triggered.connect(self._import_notes)
        toolbar.addAction(import_action)
        self.addAction(import_action)

        

    def _show_about(self):
        QMessageBox.information(self, "Speedy Notes Hakkında",
            "Speedy Notes\n\nHızlı, modern ve sade not defteri uygulaması.\n\nSürüm: 1.5.0\nYazar: Harun Hurma\n© 2025")

    def _yeni_not(self):
        # Otomatik başlık numaralandırma
        mevcut_numaralar = []
        for note in self.memory.notes:
            if note["title"].startswith("Yeni Not"):
                parca = note["title"].replace("Yeni Not", "").strip()
                if parca.isdigit():
                    mevcut_numaralar.append(int(parca))
        yeni_num = 1
        while yeni_num in mevcut_numaralar:
            yeni_num += 1
        yeni_baslik = f"Yeni Not {yeni_num}"

        # 1. Notu belleğe ekle
        yeni_not_bellek_idx = self.memory.add_note(title=yeni_baslik, content="")
        simdi = self.memory.get_note(yeni_not_bellek_idx)["datetime"]

        # 2. Sekme için widget ve içeriğini oluştur
        widget_icin_sekme = QWidget()
        layout = QVBoxLayout(widget_icin_sekme)
        etiket = QLabel(f"Oluşturulma: {simdi}")
        etiket.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(etiket)
        not_duzenle = PlainTextEdit()
        not_duzenle.textChanged.connect(self._not_guncelle)
        layout.addWidget(not_duzenle)

        # 3. Widget'ı QTabWidget'a ekle
        gercek_sekme_idx = self.tabs.addTab(widget_icin_sekme, yeni_baslik)

        # 4. KRİTİK: Oluşturulan widget'ı _tab_widgets sözlüğüne kaydet
        # Bu, _sekme_widget_olustur'un widget'ı bulmasını ve yeniden oluşturmamasını sağlar.
        self._tab_widgets[gercek_sekme_idx] = widget_icin_sekme

        # 5. Yeni sekmeyi aktif yap (bu _sekme_degisti -> _sekme_widget_olustur tetikler)
        self.tabs.setCurrentIndex(gercek_sekme_idx)
        self.logger.info(f"Yeni not eklendi: {yeni_baslik} (İndeks: {gercek_sekme_idx})")

    def _sekme_kapat_indeksli(self, idx):
        baslik = self.tabs.tabText(idx)
        yanit = QMessageBox.question(
            self,
            "Notu Kapat",
            f"'{baslik}' sekmesini kapatmak istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if yanit != QMessageBox.StandardButton.Yes:
            return
        
        # Dosya yolu varsa temizle
        if hasattr(self, '_file_paths') and idx in self._file_paths:
            del self._file_paths[idx]
        
        if self.tabs.count() == 1:
            self.tabs.removeTab(idx)
            self.memory.remove_note(idx)
            self.logger.info(f"Son sekme kapatıldı, uygulama kapanıyor.")
            self.close()
        else:
            self.tabs.removeTab(idx)
            self.memory.remove_note(idx)
            self.logger.info(f"Sekme kapatıldı: Not {idx+1}")
            
            # Dosya yolu indekslerini güncelle
            if hasattr(self, '_file_paths'):
                updated_paths = {}
                for old_idx, path in self._file_paths.items():
                    if old_idx > idx:
                        updated_paths[old_idx - 1] = path
                    elif old_idx < idx:
                        updated_paths[old_idx] = path
                self._file_paths = updated_paths

    def _notu_sil(self):
        idx = self.tabs.currentIndex()
        not_edit = self.tabs.currentWidget()
        if not_edit:
            not_edit.clear()
            self.memory.update_note(idx, "")
            self.logger.info(f"Not temizlendi: Not {idx+1}")

    def _notu_kopyala(self):
        idx = self.tabs.currentIndex()
        not_edit = self.tabs.currentWidget()
        if not_edit:
            text = not_edit.toPlainText()
            QApplication.clipboard().setText(text)
            self.logger.info(f"Not panoya kopyalandı: Not {idx+1}")
            QMessageBox.information(self, "Kopyalandı", "Not panoya kopyalandı.")

    def _not_guncelle(self):
        idx = self.tabs.currentIndex()
        widget = self.tabs.currentWidget()
        if widget:
            not_edit = widget.findChild(QTextEdit)
            if not_edit:
                self.memory.update_note(idx, content=not_edit.toHtml())
                self._otomatik_kaydet()

    def _sekme_degisti(self, idx):
        self._sekme_widget_olustur(idx)

    def _sekme_baslik_duzenle(self, idx):
        self.logger.info(f"Tab bar çift tıklandı, indeks: {idx}")
        if idx == -1:
            self._yeni_not()
            return
        mevcut_baslik = self.memory.get_note(idx)["title"]
        yeni_baslik, ok = QInputDialog.getText(self, "Sekme Başlığını Düzenle", "Yeni başlık:", text=mevcut_baslik)
        if ok and yeni_baslik.strip():
            self.tabs.setTabText(idx, yeni_baslik.strip())
            self.memory.update_note(idx, title=yeni_baslik.strip())
            self._otomatik_kaydet()
            self.logger.info(f"Sekme başlığı değiştirildi: {yeni_baslik.strip()}")

    def _tema_toggle(self):
        if self.tema == "aydinlik":
            self._tema_degistir("koyu")
        else:
            self._tema_degistir("aydinlik")

    def _tema_degistir(self, tema):
        if tema == "koyu":
            self.setStyleSheet("""
                QMainWindow { background: #232629; color: #f0f0f0; }
                QTextEdit { background: #2b2b2b; color: #f0f0f0; }
                QTabWidget::pane { border: 1px solid #444; }
                QTabBar::tab { background: #232629; color: #f0f0f0; }
                QMenuBar { background: #232629; color: #f0f0f0; }
                QMenu { background: #232629; color: #f0f0f0; }
            """)
            self.tema = "koyu"
            self.logger.info("Tema değiştirildi: koyu")
        else:
            self.setStyleSheet("")
            self.tema = "aydinlik"
            self.logger.info("Tema değiştirildi: aydınlık")

    def _notlari_yukle(self):
        self.tabs.clear()
        self._tab_widgets = {}
        last_index = 0
        
        # Son açık sekme index'ini ve dosya yollarını ayarlamak için ayarları oku
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                last_index = settings.get('last_tab_index', 0)
                # Dosya yollarını geri yükle
                if 'file_paths' in settings:
                    self._file_paths = {int(k): v for k, v in settings['file_paths'].items()}
                else:
                    self._file_paths = {}
        except Exception:
            last_index = 0
            self._file_paths = {}
            
        if self.memory.note_count() == 0:
            self._yeni_not()
        else:
            for i in range(self.memory.note_count()):
                self._sekme_widget_olustur(i)
            if last_index >= self.tabs.count():
                last_index = 0
            self.tabs.setCurrentIndex(last_index)

    def _sekme_widget_olustur(self, idx):
        if idx in self._tab_widgets:
            self.tabs.setTabText(idx, self.memory.get_note(idx)["title"])
            self.tabs.setTabToolTip(idx, self.memory.get_note(idx)["title"])
            self.tabs.setTabEnabled(idx, True)
            return
        note = self.memory.get_note(idx)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Eğer bu sekme bir dosya ise, dosya yolu bilgisini göster
        if hasattr(self, '_file_paths') and idx in self._file_paths:
            file_path = self._file_paths[idx]
            label = QLabel(f"Dosya: {file_path}")
        else:
            label = QLabel(f"Oluşturulma: {note['datetime']}")
        label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(label)
        
        not_edit = PlainTextEdit()
        not_edit.setHtml(note["content"])
        not_edit.textChanged.connect(self._not_guncelle)
        not_edit.undoAvailable.connect(self.undo_action.setEnabled)
        not_edit.redoAvailable.connect(self.redo_action.setEnabled)
        self.undo_action.setEnabled(not_edit.document().isUndoAvailable())
        self.redo_action.setEnabled(not_edit.document().isRedoAvailable())        # Dosya tipine göre syntax highlighting ekle
        if (hasattr(self, '_file_paths') and idx in self._file_paths):
            file_path = self._file_paths[idx]
            file_ext = file_path.lower()
            if file_ext.endswith('.py'):
                highlighter = PythonSyntaxHighlighter(not_edit.document())
                not_edit.highlighter = highlighter
            elif file_ext.endswith(('.html', '.htm')):
                highlighter = HtmlSyntaxHighlighter(not_edit.document())
                not_edit.highlighter = highlighter
            elif file_ext.endswith('.css'):
                highlighter = CssSyntaxHighlighter(not_edit.document())
                not_edit.highlighter = highlighter
        
        layout.addWidget(not_edit)
        self.tabs.currentChanged.disconnect(self._sekme_degisti)
        self.tabs.insertTab(idx, widget, note["title"])
        self.tabs.currentChanged.connect(self._sekme_degisti)
        self._tab_widgets[idx] = widget

    def closeEvent(self, event):
        self.memory.save_to_file(self.notes_path)
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception:
            settings = {}
        settings['last_tab_index'] = self.tabs.currentIndex()
        
        # Dosya yollarını kaydet
        if hasattr(self, '_file_paths'):
            settings['file_paths'] = self._file_paths
        else:
            settings['file_paths'] = {}
            
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        self.logger.info("Notlar kaydedildi.")
        event.accept()

    def _arama_ac(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Notlarda Ara")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        arama_input = QLineEdit()
        arama_input.setPlaceholderText("Aranacak kelime veya cümle...")
        layout.addWidget(arama_input)
        sonuc_list = QListWidget()
        layout.addWidget(sonuc_list)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        def arama_yap():
            sonuc_list.clear()
            kelime = arama_input.text().strip().lower()
            if not kelime:
                return
            for idx, note in enumerate(self.memory.notes):
                icerik_plain = QTextEdit()
                icerik_plain.setHtml(note["content"])
                plain = icerik_plain.toPlainText()
                if kelime in note["title"].lower() or kelime in plain.lower():
                    ilk_satir = plain.split('\n', 1)[0][:50]
                    item = QListWidgetItem(f"{note['title']} - {ilk_satir}")
                    item.setData(Qt.ItemDataRole.UserRole, idx)
                    sonuc_list.addItem(item)
        arama_input.textChanged.connect(arama_yap)

        def sonuca_git(item):
            idx = item.data(Qt.ItemDataRole.UserRole)
            self.tabs.setCurrentIndex(idx)
            dialog.accept()
        sonuc_list.itemDoubleClicked.connect(sonuca_git)
        arama_input.returnPressed.connect(arama_yap)
        arama_input.setFocus()
        dialog.exec()

    def _center_window(self):
        ekran = QApplication.primaryScreen().geometry()
        pencere = self.frameGeometry()
        pencere.moveCenter(ekran.center())
        self.move(pencere.topLeft())

    def _bold_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            fmt = not_edit.currentCharFormat()
            fmt.setFontWeight(700 if fmt.fontWeight() != 700 else 400)
            not_edit.mergeCurrentCharFormat(fmt)

    def _italic_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            fmt = not_edit.currentCharFormat()
            fmt.setFontItalic(not fmt.fontItalic())
            not_edit.mergeCurrentCharFormat(fmt)

    def _strike_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            fmt = not_edit.currentCharFormat()
            fmt.setFontStrikeOut(not fmt.fontStrikeOut())
            not_edit.mergeCurrentCharFormat(fmt)

    def _cut_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            not_edit.cut()

    def _copy_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            not_edit.copy()

    def _paste_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            not_edit.paste()

    def _undo_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            not_edit.undo()

    def _redo_text(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            not_edit.redo()

    def _font_increase(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            fmt = not_edit.currentCharFormat()
            size = fmt.fontPointSize() or not_edit.fontPointSize() or 12
            fmt.setFontPointSize(size + 1)
            not_edit.mergeCurrentCharFormat(fmt)

    def _font_decrease(self):
        not_edit = self._aktif_not_edit()
        if not_edit:
            fmt = not_edit.currentCharFormat()
            size = fmt.fontPointSize() or not_edit.fontPointSize() or 12
            fmt.setFontPointSize(max(6, size - 1))
            not_edit.mergeCurrentCharFormat(fmt)

    def _aktif_not_edit(self):
        widget = self.tabs.currentWidget()
        if widget:
            return widget.findChild(QTextEdit)
        return None

    def _sekme_tasi(self, eski_idx, yeni_idx):
        self.logger.info(f"Sekme taşıma isteği: {eski_idx} -> {yeni_idx}. Mevcut not sayısı: {self.memory.note_count()}, Sekme sayısı: {self.tabs.count()}")

        # Qt tarafından sağlanan indekslerin geçerliliğini QTabWidget sayısına göre kontrol et
        if not (0 <= eski_idx < self.tabs.count() and 0 <= yeni_idx < self.tabs.count()):
            self.logger.error(f"Qt tarafından sağlanan geçersiz sekme indeksleri: eski_idx={eski_idx}, yeni_idx={yeni_idx}, sekme_sayısı={self.tabs.count()}")
            return

        # Bellekteki not sayısı ile sekme sayısı arasında senkronizasyon kontrolü
        if self.memory.note_count() != self.tabs.count():
            self.logger.error(f"Senkronizasyon hatası: Not sayısı ({self.memory.note_count()}) != Sekme sayısı ({self.tabs.count()}). Taşıma işlemi iptal edildi.")
            # İdeal olarak burada bir yeniden senkronizasyon mekanizması olabilir veya kullanıcıya bildirim gösterilebilir.
            # Şimdilik, çökmemesi için işlemi iptal ediyoruz.
            return

        current_note_count = self.memory.note_count() # Bu noktada self.tabs.count() ile aynı olmalı

        # 1. self.memory.notes listesini yeniden sırala
        try:
            note_to_move = self.memory.notes.pop(eski_idx)
            self.memory.notes.insert(yeni_idx, note_to_move)
        except IndexError:
            # Yukarıdaki senkronizasyon kontrolü bu hatayı önlemeli.
            self.logger.exception(f"self.memory.notes üzerinde pop/insert sırasında beklenmedik Index Hatası: eski_idx={eski_idx}, yeni_idx={yeni_idx}, not sayısı={current_note_count}")
            return        # 2. _tab_widgets sözlüğünü self.memory.notes'un yeni sırasına uyacak şekilde yeniden sırala
        if hasattr(self, '_tab_widgets') and self._tab_widgets:
            if current_note_count > 0:
                # Eski sıraya göre widget'ların bir listesini oluştur
                widgets_in_old_order = [self._tab_widgets.get(i) for i in range(current_note_count)]

                try:
                    moved_widget_item = widgets_in_old_order.pop(eski_idx)
                    widgets_in_old_order.insert(yeni_idx, moved_widget_item) # widgets_in_old_order şimdi YENİ sırada
                except IndexError:
                    self.logger.exception(f"_tab_widgets için widget listesi yeniden sıralanırken Index Hatası: eski_idx={eski_idx}, yeni_idx={yeni_idx}")
                    self._tab_widgets.clear() # Kritik hata, _tab_widgets temizlenerek "kopya" sorunları önlenmeye çalışılır.
                    self.logger.warning("_tab_widgets temizlendi çünkü yeniden sıralama sırasında hata oluştu.")
                else:
                    self._tab_widgets.clear()
                    for i, widget in enumerate(widgets_in_old_order):
                        if widget is not None:
                            self._tab_widgets[i] = widget
            else: # Not/sekme yoksa _tab_widgets boş olmalı
                self._tab_widgets.clear()
        
        # Dosya yollarını da taşı
        if hasattr(self, '_file_paths') and self._file_paths:
            updated_paths = {}
            for idx, path in self._file_paths.items():
                if idx == eski_idx:
                    updated_paths[yeni_idx] = path
                elif eski_idx < yeni_idx and eski_idx < idx <= yeni_idx:
                    updated_paths[idx - 1] = path
                elif yeni_idx < eski_idx and yeni_idx <= idx < eski_idx:
                    updated_paths[idx + 1] = path
                else:
                    updated_paths[idx] = path
            self._file_paths = updated_paths
        
        # 3. Değişiklikleri kaydet (yeni sıra ve potansiyel olarak değişen aktif sekme)
        self._otomatik_kaydet()
        
        self.logger.info(f"Sekme başarıyla taşındı: {eski_idx} -> {yeni_idx}. Yeni not sırası ve ayarlar kaydedildi.")

    def _export_all_notes_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", "tum_notlar.pdf", "PDF Dosyası (*.pdf)")
        if not path:
            return
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        from PyQt6.QtGui import QTextDocument
        doc = QTextDocument()
        html = ""
        for note in self.memory.notes:
            html += f"<h2>{note['title']}</h2>"
            html += note['content']
            html += "<hr>"
        doc.setHtml(html)
        doc.print(printer)
        QMessageBox.information(self, "PDF'e Aktarıldı", f"Tüm notlar PDF olarak kaydedildi:\n{path}")

    def _import_notes(self):
        path, _ = QFileDialog.getOpenFileName(self, "Notları İçe Aktar", "", "JSON Dosyası (*.json)")
        if not path:
            return
        yanit = QMessageBox.question(
            self,
            "Notları İçe Aktar",
            "Bu işlem mevcut tüm notları silecek ve sadece içe aktardığınız notları kalacak. Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if yanit != QMessageBox.StandardButton.Yes:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                imported_notes = json.load(f)
            if isinstance(imported_notes, list):
                self.memory.notes = imported_notes
                self.memory.save_to_file(self.notes_path)
                self._notlari_yukle()
                QMessageBox.information(self, "İçe Aktarıldı", f"{len(imported_notes)} not başarıyla içe aktarıldı. Mevcut notlar silindi.")
            else:
                QMessageBox.warning(self, "Hata", "Seçilen dosya geçerli bir not listesi içermiyor.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"İçe aktarma sırasında hata oluştu:\n{e}")

    def _open_file(self):
        """Python, Text, HTML ve CSS dosyalarını açar ve yeni bir sekme olarak ekler"""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Dosya Aç", 
            "", 
            "Web/Code Dosyaları (*.py *.txt *.html *.htm *.css);;Python Dosyaları (*.py);;HTML Dosyaları (*.html *.htm);;CSS Dosyaları (*.css);;Text Dosyaları (*.txt);;Tüm Dosyalar (*)"
        )
        if not path:
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Dosya adını başlık olarak kullan
            file_name = os.path.basename(path)
            
            # Aynı dosya zaten açık mı kontrol et
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == file_name:
                    self.tabs.setCurrentIndex(i)
                    QMessageBox.information(self, "Dosya Zaten Açık", f"'{file_name}' dosyası zaten açık.")
                    return
            
            # Yeni not olarak ekle
            yeni_not_bellek_idx = self.memory.add_note(title=file_name, content=content)
            
            # Sekme widget'ı oluştur
            widget_icin_sekme = QWidget()
            layout = QVBoxLayout(widget_icin_sekme)
              # Dosya yolu bilgisini göster
            etiket = QLabel(f"Dosya: {path}")
            etiket.setStyleSheet("color: gray; font-size: 10pt;")
            layout.addWidget(etiket)
            
            not_duzenle = PlainTextEdit()
            not_duzenle.setPlainText(content)  # HTML yerine plain text kullan
            not_duzenle.textChanged.connect(self._not_guncelle)            # Dosya tipine göre syntax highlighting ekle
            file_ext = path.lower()
            if file_ext.endswith('.py'):
                highlighter = PythonSyntaxHighlighter(not_duzenle.document())
                not_duzenle.highlighter = highlighter
            elif file_ext.endswith(('.html', '.htm')):
                highlighter = HtmlSyntaxHighlighter(not_duzenle.document())
                not_duzenle.highlighter = highlighter
            elif file_ext.endswith('.css'):
                highlighter = CssSyntaxHighlighter(not_duzenle.document())
                not_duzenle.highlighter = highlighter
            
            layout.addWidget(not_duzenle)
            
            # Sekmeyi ekle
            gercek_sekme_idx = self.tabs.addTab(widget_icin_sekme, file_name)
            self._tab_widgets[gercek_sekme_idx] = widget_icin_sekme
            
            # Dosya yolunu sekme ile ilişkilendir (kaydetme için)
            if not hasattr(self, '_file_paths'):
                self._file_paths = {}
            self._file_paths[gercek_sekme_idx] = path
            
            # Yeni sekmeyi aktif yap
            self.tabs.setCurrentIndex(gercek_sekme_idx)
            
            self.logger.info(f"Dosya açıldı: {path}")
            QMessageBox.information(self, "Dosya Açıldı", f"'{file_name}' başarıyla açıldı.")
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya açılırken hata oluştu:\n{e}")
            self.logger.error(f"Dosya açma hatası: {e}")

    def _save_current_file(self):
        """Mevcut sekmedeki içeriği dosyaya kaydet"""
        current_idx = self.tabs.currentIndex()
        if current_idx < 0:
            return
        
        widget = self.tabs.currentWidget()
        if not widget:
            return
        
        not_edit = widget.findChild(QTextEdit)
        if not not_edit:
            return
        
        content = not_edit.toPlainText()
        
        # Eğer bu sekme bir dosyadan açılmışsa, aynı dosyaya kaydet
        if hasattr(self, '_file_paths') and current_idx in self._file_paths:
            file_path = self._file_paths[current_idx]
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Kaydedildi", f"Dosya kaydedildi: {file_path}")
                self.logger.info(f"Dosya kaydedildi: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dosya kaydedilirken hata oluştu:\n{e}")
                self.logger.error(f"Dosya kaydetme hatası: {e}")
        else:
            # Yeni dosya olarak kaydet
            path, _ = QFileDialog.getSaveFileName(
                self, 
                "Dosyayı Kaydet", 
                "", 
                "Python Dosyası (*.py);;HTML Dosyası (*.html);;CSS Dosyası (*.css);;Text Dosyası (*.txt);;Tüm Dosyalar (*)"
            )
            if path:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Dosya yolunu kaydet
                    if not hasattr(self, '_file_paths'):
                        self._file_paths = {}
                    self._file_paths[current_idx] = path
                      # Sekme başlığını güncelle
                    file_name = os.path.basename(path)
                    self.tabs.setTabText(current_idx, file_name)                    # Dosya tipine göre syntax highlighting ekle
                    file_ext = path.lower()
                    if file_ext.endswith('.py') and not hasattr(not_edit, 'highlighter'):
                        highlighter = PythonSyntaxHighlighter(not_edit.document())
                        not_edit.highlighter = highlighter
                    elif file_ext.endswith(('.html', '.htm')) and not hasattr(not_edit, 'highlighter'):
                        highlighter = HtmlSyntaxHighlighter(not_edit.document())
                        not_edit.highlighter = highlighter
                    elif file_ext.endswith('.css') and not hasattr(not_edit, 'highlighter'):
                        highlighter = CssSyntaxHighlighter(not_edit.document())
                        not_edit.highlighter = highlighter
                    
                    QMessageBox.information(self, "Kaydedildi", f"Dosya kaydedildi: {path}")
                    self.logger.info(f"Yeni dosya kaydedildi: {path}")
                except Exception as e:
                    QMessageBox.warning(self, "Hata", f"Dosya kaydedilirken hata oluştu:\n{e}")
                    self.logger.error(f"Dosya kaydetme hatası: {e}")

    def _otomatik_kaydet(self):
        self.memory.save_to_file(self.notes_path)
        self.logger.info("Değişiklikler otomatik kaydedildi.")
        # Son aktif sekmeyi de kaydet
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception:
            settings = {}
        settings['last_tab_index'] = self.tabs.currentIndex()
        
        # Dosya yollarını kaydet
        if hasattr(self, '_file_paths'):
            settings['file_paths'] = self._file_paths
        else:
            settings['file_paths'] = {}
            
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Ayarlar kaydedildi, son aktif sekme: {self.tabs.currentIndex()}")
        except Exception as e:
            self.logger.error(f"Ayarlar kaydedilemedi: {e}")

def main():
    app = QApplication(sys.argv)
    pencere = NotDefteriGUI()
    pencere.show()
    sys.exit(app.exec())