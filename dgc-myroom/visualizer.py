from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

ORANGE = "#ff8c00"
RED = "#c91e1e"


class SpacePreview(QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self._scene = scene

        fig = plt.figure()
        self._ax: Axes3D = fig.add_subplot(111, projection="3d")
        self._ax.set_xlabel("X [m]")
        self._ax.set_ylabel("Y [m]")
        self._ax.set_zlabel("Z [m]")

        canvas = FigureCanvasQTAgg(fig)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(canvas)

        self.redraw()

    def redraw(self):
        ax = self._ax
        ax.cla()
        ax.set_box_aspect([1, 1, 0.5])

        ax.scatter(0, 0, 0, marker="x", color="k")

        mic_xyz = self._scene.microphones_for_plot()
        if mic_xyz.size:
            ax.scatter(mic_xyz[:, 0], mic_xyz[:, 1], mic_xyz[:, 2],
                       s=60, color=ORANGE, depthshade=False)
            for i, p in enumerate(mic_xyz, 1):
                ax.text(*p, f"Mic {str(i).zfill(2)}")

        for idx, spk in enumerate(self._scene.speakers, 1):
            if not spk.enabled:
                continue
            x, y, z = spk.pos
            ax.scatter([x], [y], [z], s=60, color=RED, depthshade=False)
            ax.text(x, y, z, f"Speaker {str(idx).zfill(2)}")

        sx, sy, sz = self._scene.room_cfg.size
        ax.set_xlim(-sx / 2, sx / 2)
        ax.set_ylim(-sy / 2, sy / 2)
        ax.set_zlim(0, sz)

        ax.figure.canvas.draw_idle()
