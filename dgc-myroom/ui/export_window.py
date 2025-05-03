from __future__ import annotations
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
)
from PySide6.QtCore import Qt
from pathlib import Path


class ExportWindow(QDockWidget):
    def __init__(self, scene, parent=None):
        super().__init__("Exported", parent)
        self._scene = scene
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)

        self._path_label = QLabel("Export Path: Not Selected")
        self._choose_btn = QPushButton("Select Path")
        self._export_btn = QPushButton("Export - Ready")
        self._export_btn.setEnabled(False)

        lay = QVBoxLayout()
        lay.addWidget(self._path_label)
        lay.addWidget(self._choose_btn)
        lay.addWidget(self._export_btn)
        cont = QWidget()
        cont.setLayout(lay)
        self.setWidget(cont)

        self._choose_btn.clicked.connect(self._choose_path)
        self._export_btn.clicked.connect(self._do_export)

        self._path: Path | None = None

    def _choose_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Select Path", filter="Wave (*.wav)"
        )
        if path:
            self._path = Path(path)
            self._path_label.setText(f"Export Path: {self._path}")
            self._export_btn.setEnabled(True)

    def _do_export(self):
        assert self._path is not None
        self._scene.render(self._path)
        self._export_btn.setText("Export - Completed")
        self._export_btn.setEnabled(True)
