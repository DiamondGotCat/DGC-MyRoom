from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import numpy as np
import soundfile as sf
import pyroomacoustics as pra
from scipy.signal import resample_poly
from pathlib import Path

FS_DEFAULT = 48_000


@dataclass
class Speaker:
    path: str
    pos: np.ndarray
    volume: float = 1.0
    start_sec: float = 0.0
    enabled: bool = True


@dataclass
class RoomConfig:
    size: np.ndarray = field(
        default_factory=lambda: np.array([6., 6., 3.], dtype=float)
    )
    absorption: float = 0.4


class AcousticScene:
    def __init__(self, mic_count: int = 2, mic_radius: float = 1.0):
        self.room_cfg = RoomConfig()
        self.speakers: List[Speaker] = []
        self.mic_count = mic_count
        self.mic_radius = mic_radius

    def _mic_positions(self) -> np.ndarray:
        theta = np.linspace(0, 2 * np.pi, self.mic_count, endpoint=False)
        xyz = np.vstack([
            self.mic_radius * np.cos(theta),
            self.mic_radius * np.sin(theta),
            np.zeros_like(theta),
        ])
        return xyz

    def microphones_for_plot(self) -> np.ndarray:
        return self._mic_positions().T

    def add_speaker(self, speaker: Speaker):
        self.speakers.append(speaker)

    def remove_speaker(self, idx: int):
        if 0 <= idx < len(self.speakers):
            del self.speakers[idx]

    def render(self, out_path: str | Path):
        fs = FS_DEFAULT
        rc = self.room_cfg

        room = pra.ShoeBox(
            rc.size,
            fs=fs,
            max_order=12,
            absorption=rc.absorption,
        )

        shift = np.array([rc.size[0] / 2, rc.size[1] / 2, 0.0])

        mic_xyz = self._mic_positions() + shift[:, None]
        room.add_microphone_array(pra.MicrophoneArray(mic_xyz, fs))

        prepared: list[tuple[np.ndarray, np.ndarray]] = []
        max_len = 0

        for spk in self.speakers:
            if not spk.enabled or not spk.path:
                continue

            sig, sig_fs = sf.read(spk.path)
            if sig_fs != fs:
                sig = resample_poly(sig, fs, sig_fs)

            if sig.ndim > 1:
                sig = sig.mean(axis=1)
            sig *= spk.volume

            pre_silence = np.zeros(int(spk.start_sec * fs))
            sig = np.concatenate([pre_silence, sig])

            max_len = max(max_len, sig.size)

            prepared.append((spk.pos + shift, sig))

        if not prepared:
            raise RuntimeError("No Enabled Speaker")

        for pos, sig in prepared:
            pad = np.zeros(max_len - sig.size)
            room.add_source(pos, signal=np.concatenate([sig, pad]))

        room.simulate()
        wav = room.mic_array.signals.T
        sf.write(str(out_path), wav, fs)
