"""Conversao de segmentos EEG em espectrogramas STFT RGB."""

import sys
from pathlib import Path
import numpy as np
import matplotlib
if "ipykernel" not in sys.modules:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import spectrogram as scipy_spectrogram
from PIL import Image

FRONTAL_IDX  = [0, 1, 5, 12, 13, 16, 17, 21, 28]
CENTRAL_IDX  = [2, 6, 7, 8, 9, 10, 11, 14, 18, 22, 23, 24, 25, 26, 27]
PARIETAL_IDX = [3, 4, 15, 19, 20]

CLASS_COLORS = {
    "pre_ictal": "#3498db",
    "ictal": "#e74c3c",
    "pos_ictal": "#2ecc71",
    "normal": "#95a5a6",
}


def _group_spectrogram_uint8(data: np.ndarray, indices: list, fs: int, nperseg: int, noverlap: int) -> np.ndarray:
    valid = [i for i in indices if i < data.shape[0]]
    spectros = []
    for i in valid:
        _, _, Sxx = scipy_spectrogram(data[i], fs=fs, nperseg=nperseg, noverlap=noverlap)
        spectros.append(10.0 * np.log10(Sxx + 1e-10))
    arr = np.mean(spectros, axis=0)
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return np.zeros_like(arr, dtype=np.uint8)
    return ((arr - mn) / (mx - mn) * 255).astype(np.uint8)


def segment_to_spectrogram(
    segment: np.ndarray,
    fs: int = 512,
    nperseg: int = 256,
    noverlap: int = 128,
) -> np.ndarray:
    """Converte um segmento EEG (n_channels, n_samples) em imagem RGB uint8."""
    r = _group_spectrogram_uint8(segment, FRONTAL_IDX, fs, nperseg, noverlap)
    g = _group_spectrogram_uint8(segment, CENTRAL_IDX, fs, nperseg, noverlap)
    b = _group_spectrogram_uint8(segment, PARIETAL_IDX, fs, nperseg, noverlap)
    return np.stack([r, g, b], axis=-1)


def save_spectrogram(img_array: np.ndarray, output_path: str) -> None:
    """Salva o espectrograma RGB como PNG."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img_array).save(str(out))


def plot_class_grid(spectrograms: dict, patient_id: str, seizure_n: int, edf_file: str):
    """Plota um grid 2x2 com os 4 espectrogramas de uma crise."""
    classes = ["pre_ictal", "ictal", "pos_ictal", "normal"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    fig.suptitle(f"{patient_id} | Crise {seizure_n} | {edf_file}", fontweight="bold")

    for ax, cls in zip(axes.flat, classes):
        img = spectrograms.get(cls)
        if img is not None:
            ax.imshow(img, aspect="auto", origin="lower")
        ax.set_title(cls, fontweight="bold", color=CLASS_COLORS.get(cls, "#333"))
        ax.set_xlabel("Frames STFT")
        ax.set_ylabel("Freq (bins)")

    plt.tight_layout()
    return fig
