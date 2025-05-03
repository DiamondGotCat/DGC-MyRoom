from __future__ import annotations
import sys
import numpy as np
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar
from PySide6.QtGui     import QAction
from PySide6.QtCore    import Qt

from .acoustic_model import AcousticScene, Speaker
from .visualizer      import SpacePreview
from .ui.sound_window     import SoundWindow
from .ui.property_window  import PropertyWindow
from .ui.export_window    import ExportWindow


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DGC-MyRoom")

        self.scene = AcousticScene(mic_count=2, mic_radius=1.0)

        self.scene.add_speaker(Speaker(path="", pos=np.array([0.5, -2, 0])))
        self.scene.add_speaker(Speaker(path="", pos=np.array([-0.5, -2, 0])))

        self.preview = SpacePreview(self.scene)
        self.setCentralWidget(self.preview)

        # ----- Dock -----
        self.sound_win  = SoundWindow(self.scene, self.preview)
        self.prop_win   = PropertyWindow(self.scene, self.preview)
        self.export_win = ExportWindow(self.scene)

        self.addDockWidget(Qt.LeftDockWidgetArea,   self.sound_win)
        self.addDockWidget(Qt.RightDockWidgetArea,  self.prop_win)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.export_win)

        tb = QToolBar()
        self.addToolBar(tb)
        tb.addAction(QAction("Redraw", self, triggered=self.preview.redraw))


def main():
    app = QApplication(sys.argv)
    win = Main()
    win.resize(1400, 900)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
