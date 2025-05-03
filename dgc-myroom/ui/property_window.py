from __future__ import annotations
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QFormLayout, QDoubleSpinBox, QSpinBox
)
from PySide6.QtCore import Qt


class PropertyWindow(QDockWidget):
    def __init__(self, scene, preview, parent=None):
        super().__init__("Room", parent)
        self._scene = scene
        self._preview = preview
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self._size_x = QDoubleSpinBox(decimals=2, minimum=1, maximum=50, singleStep=0.5)
        self._size_y = QDoubleSpinBox(decimals=2, minimum=1, maximum=50, singleStep=0.5)
        self._size_z = QDoubleSpinBox(decimals=2, minimum=1, maximum=20, singleStep=0.5)

        self._absorpt = QDoubleSpinBox(decimals=2, minimum=0, maximum=1, singleStep=0.05)
        self._mic_cnt = QSpinBox(minimum=2, maximum=32)
        self._mic_rad = QDoubleSpinBox(decimals=2, minimum=0.1, maximum=10, singleStep=0.1)

        form = QFormLayout()
        form.addRow("Room X [m]", self._size_x)
        form.addRow("Room Y [m]", self._size_y)
        form.addRow("Room Z [m]", self._size_z)
        form.addRow("Absorption", self._absorpt)
        form.addRow("Mic count (Number of channels after output)", self._mic_cnt)
        form.addRow("Mic radius [m]", self._mic_rad)

        cont = QWidget()
        cont.setLayout(form)
        self.setWidget(cont)

        for w in (self._size_x, self._size_y, self._size_z,
                  self._absorpt, self._mic_cnt, self._mic_rad):
            w.editingFinished.connect(self._commit)

        self.refresh()

    def refresh(self):
        rc = self._scene.room_cfg
        self._size_x.setValue(rc.size[0])
        self._size_y.setValue(rc.size[1])
        self._size_z.setValue(rc.size[2])
        self._absorpt.setValue(rc.absorption)
        self._mic_cnt.setValue(self._scene.mic_count)
        self._mic_rad.setValue(self._scene.mic_radius)

    def _commit(self):
        rc = self._scene.room_cfg
        rc.size[0] = self._size_x.value()
        rc.size[1] = self._size_y.value()
        rc.size[2] = self._size_z.value()
        rc.absorption = self._absorpt.value()
        self._scene.mic_count = self._mic_cnt.value()
        self._scene.mic_radius = self._mic_rad.value()
        self._preview.redraw()
