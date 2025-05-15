from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QTextEdit, QVBoxLayout, QWidget, QInputDialog, QToolBar, QMessageBox, QLabel, QSplashScreen, QTabBar, QToolButton, QHBoxLayout, QDialog, QLineEdit, QListWidget, QListWidgetItem, QDialogButtonBox
from PyQt6.QtGui import QIcon, QAction, QClipboard, QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QSize, QMimeData, QObject, QEvent
import sys
import qtawesome as qta
import time
from helpers.note_memory_helper import NoteMemory
from utils.logger import get_logger

class PlainTextEdit(QTextEdit):
    def insertFromMimeData(self, source: QMimeData):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)

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
        self.tabs.tabCloseRequested.connect(self._sekme_kapat_indeksli)
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
        self.notes_path = "config/notes.json"
        self.memory.load_from_file(self.notes_path)
        self._setup_toolbar()
        self.tabs.currentChanged.connect(self._sekme_degisti)
        self.tabbar_filter = TabBarDoubleClickFilter(self.tabs.tabBar(), self._sekme_baslik_duzenle)
        self.tabs.tabBar().installEventFilter(self.tabbar_filter)
        self._notlari_yukle()
        self._center_window()

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

        sil_icon = qta.icon('fa5s.trash', color='orange')
        sil_aksiyon = QAction(sil_icon, "Notu Sil", self)
        sil_aksiyon.triggered.connect(self._notu_sil)
        toolbar.addAction(sil_aksiyon)

        kopyala_icon = qta.icon('fa5s.copy', color='blue')
        kopyala_aksiyon = QAction(kopyala_icon, "Notu Kopyala", self)
        kopyala_aksiyon.triggered.connect(self._notu_kopyala)
        toolbar.addAction(kopyala_aksiyon)
        
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
        undo_icon = qta.icon('fa5s.undo', color='#607D8B')  # Gri
        undo_action = QAction(undo_icon, "Geri Al (Ctrl+Z)", self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self._undo_text)
        toolbar.addAction(undo_action)
        self.addAction(undo_action)

        # Redo
        redo_icon = qta.icon('fa5s.redo', color='#43A047')  # Yeşil
        redo_action = QAction(redo_icon, "Yinele (Ctrl+Y)", self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self._redo_text)
        toolbar.addAction(redo_action)
        self.addAction(redo_action)

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
        toolbar.addAction(info_aksiyon)

        # Ctrl+N kısayolu ile yeni not
        yeni_shortcut = QAction(self)
        yeni_shortcut.setShortcut('Ctrl+N')
        yeni_shortcut.triggered.connect(self._yeni_not)
        self.addAction(yeni_shortcut)

        
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
        widget = QWidget()
        layout = QVBoxLayout(widget)
        now = self.memory.get_note(self.memory.add_note(title=yeni_baslik, content=""))["datetime"]
        label = QLabel(f"Oluşturulma: {now}")
        label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(label)
        not_edit = PlainTextEdit()
        not_edit.textChanged.connect(self._not_guncelle)
        layout.addWidget(not_edit)
        idx = self.tabs.addTab(widget, yeni_baslik)
        self.tabs.setCurrentIndex(idx)
        self.logger.info(f"Yeni not eklendi: Not {idx+1}")

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
        if self.tabs.count() == 1:
            self.tabs.removeTab(idx)
            self.memory.remove_note(idx)
            self.logger.info(f"Son sekme kapatıldı, uygulama kapanıyor.")
            self.close()
        else:
            self.tabs.removeTab(idx)
            self.memory.remove_note(idx)
            self.logger.info(f"Sekme kapatıldı: Not {idx+1}")

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
        if self.memory.note_count() == 0:
            self._yeni_not()
        else:
            for i, note in enumerate(self.memory.notes):
                self.tabs.addTab(QWidget(), note["title"])
            self.tabs.setCurrentIndex(0)
            self._sekme_widget_olustur(0)

    def _sekme_widget_olustur(self, idx):
        if idx in self._tab_widgets:
            self.tabs.setTabText(idx, self.memory.get_note(idx)["title"])
            self.tabs.setTabToolTip(idx, self.memory.get_note(idx)["title"])
            self.tabs.setTabEnabled(idx, True)
            self.tabs.setCurrentIndex(idx)
            return
        note = self.memory.get_note(idx)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"Oluşturulma: {note['datetime']}")
        label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(label)
        not_edit = PlainTextEdit()
        not_edit.setHtml(note["content"])
        not_edit.textChanged.connect(self._not_guncelle)
        layout.addWidget(not_edit)
        self.tabs.currentChanged.disconnect(self._sekme_degisti)
        self.tabs.removeTab(idx)
        self.tabs.insertTab(idx, widget, note["title"])
        self.tabs.setCurrentIndex(idx)
        self.tabs.currentChanged.connect(self._sekme_degisti)
        self._tab_widgets[idx] = widget

    def closeEvent(self, event):
        self.memory.save_to_file(self.notes_path)
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

def main():
    app = QApplication(sys.argv)
    pencere = NotDefteriGUI()
    pencere.show()
    sys.exit(app.exec()) 