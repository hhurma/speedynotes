from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class FirstRunWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İlk Kurulum Sihirbazı")
        self.setMinimumWidth(500)
        self.selected_dir = None

        ana_layout = QHBoxLayout(self)

        # Sol: İkon
        icon_label = QLabel()
        icon_path = os.path.join('resources', 'icon.png')
        icon_size = 120
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(icon_size, icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("[icon]")
        icon_label.setFixedSize(icon_size + 10, icon_size + 10)
        ana_layout.addWidget(icon_label)

        # Sağ: Metinler ve butonlar
        sag_layout = QVBoxLayout()
        label = QLabel("Notlarınızın ve ayarlarınızın kaydedileceği klasörü seçin:")
        sag_layout.addWidget(label)

        
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Klasör Seç")
        self.select_btn.clicked.connect(self._select_dir)
        btn_layout.addWidget(self.select_btn)
        sag_layout.addLayout(btn_layout)
        
        self.dir_label = QLabel("Henüz klasör seçilmedi.")
        self.dir_label.setStyleSheet("color: gray;")
        sag_layout.addWidget(self.dir_label)

        # sag_layout.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.finish_btn = QPushButton("Bitir ve Başlat")
        self.finish_btn.setEnabled(False)
        self.finish_btn.clicked.connect(self.accept)
        sag_layout.addWidget(self.finish_btn)

        ana_layout.addLayout(sag_layout)

    def _select_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Klasör Seç", os.getcwd())
        if dir_path:
            self.selected_dir = dir_path
            self.dir_label.setText(f"Seçilen klasör: {dir_path}")
            self.finish_btn.setEnabled(True)

    def get_selected_dir(self):
        return self.selected_dir 