from __future__ import annotations
from PySide6.QtWidgets import (
    QDockWidget, QListWidget, QWidget, QFormLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QDoubleSpinBox, QSpinBox, QFileDialog, QMessageBox, QCheckBox,
)
from PySide6.QtCore import Qt
import numpy as np
from pathlib import Path
from ..acoustic_model import Speaker


class SoundWindow(QDockWidget):

    def __init__(self, scene, preview, parent=None):
        super().__init__("Sound", parent)
        self._scene = scene
        self._preview = preview
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._select_row)

        add_btn = QPushButton("+")
        add_btn.clicked.connect(self._add_speaker)
        del_btn = QPushButton("–")
        del_btn.clicked.connect(self._delete_speaker)

        btn_bar = QHBoxLayout()
        btn_bar.addWidget(add_btn)
        btn_bar.addWidget(del_btn)

        list_box = QVBoxLayout()
        list_box.addWidget(self._list)
        list_box.addLayout(btn_bar)
        list_wrap = QWidget()
        list_wrap.setLayout(list_box)

        self._enable = QCheckBox("Enabled")
        self._path_btn = QPushButton("Sound File...")
        self._gain = QDoubleSpinBox(decimals=2, minimum=0, maximum=4, singleStep=0.1)
        self._x = QDoubleSpinBox(decimals=2, minimum=-20, maximum=20, singleStep=0.1)
        self._y = QDoubleSpinBox(decimals=2, minimum=-20, maximum=20, singleStep=0.1)
        self._z = QDoubleSpinBox(decimals=2, minimum=0, maximum=20, singleStep=0.1)
        self._start = QDoubleSpinBox(
            decimals=2, suffix=" s", minimum=0, maximum=600, singleStep=0.1
        )

        form = QFormLayout()
        form.addRow(self._enable)
        form.addRow(self._path_btn)
        form.addRow("Gain", self._gain)
        form.addRow("X", self._x)
        form.addRow("Y", self._y)
        form.addRow("Z", self._z)
        form.addRow("Start", self._start)
        prop_wrap = QWidget()
        prop_wrap.setLayout(form)

        cont = QWidget()
        layout = QHBoxLayout(cont)
        layout.addWidget(list_wrap, 1)
        layout.addWidget(prop_wrap, 2)
        self.setWidget(cont)

        self._path_btn.clicked.connect(self._choose_file)

        self._enable.stateChanged.connect(self._commit)
        for w in (self._gain, self._x, self._y, self._z, self._start):
            w.editingFinished.connect(self._commit)

        self.refresh()

    def _commit(self):
        row = self._list.currentRow()
        if row < 0:
            return
        spk = self._scene.speakers[row]
        spk.enabled = self._enable.isChecked()
        spk.volume = self._gain.value()
        spk.pos = np.array([self._x.value(), self._y.value(), self._z.value()])
        spk.start_sec = self._start.value()
        self._preview.redraw()

    def _choose_file(self):
        row = self._list.currentRow()
        if row < 0:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select Audio File")
        if path:
            self._scene.speakers[row].path = path
            self._list.item(row).setText(self._make_label(row))
            self._commit()

    def refresh(self):
        self._list.clear()
        for i, _ in enumerate(self._scene.speakers):
            self._list.addItem(self._make_label(i))
        self._select_row(0)

    def _select_row(self, row: int):
        widgets = (
            self._enable, self._path_btn, self._gain,
            self._x, self._y, self._z, self._start
        )
        if row < 0 or row >= len(self._scene.speakers):
            for w in widgets:
                w.setEnabled(False)
            return

        spk = self._scene.speakers[row]
        self._enable.setChecked(spk.enabled)
        self._gain.setValue(spk.volume)
        self._x.setValue(spk.pos[0])
        self._y.setValue(spk.pos[1])
        self._z.setValue(spk.pos[2])
        self._start.setValue(spk.start_sec)
        for w in widgets:
            w.setEnabled(True)

    def _add_speaker(self):
        self._scene.add_speaker(
            Speaker(path="", pos=np.array([0., 0., 1.5]))
        )
        self.refresh()
        self._preview.redraw()

    def _delete_speaker(self):
        row = self._list.currentRow()
        if row < 0:
            return
        self._scene.remove_speaker(row)
        self.refresh()
        self._preview.redraw()

    def _make_label(self, idx: int) -> str:
        spk = self._scene.speakers[idx]
        base = f"Speaker {str(idx + 1).zfill(2)}"
        return f"{base} ({Path(spk.path).name})" if spk.path else base
