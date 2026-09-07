"""
stft_converter.py
-----------------
Converte segmentos EEG em espectogramas STFT salvos como PNG.

Composicao RGB:
    Canal R -> media dos canais frontais (Fp1, F3, F7, Fz, Fp2, F4, F8, F9, F10)
    Canal G -> media dos canais centrais/temporais (C3, Cz, C4, T3, T4, T5, T6, Fc*, Cp*)
    Canal B -> media dos canais parietais/occipitais (P3, Pz, P4, O1, O2)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import spectrogram as scipy_spectrogram
from pathlib import Path
from PIL import Image

# Indices dos canais por regiao cerebral (0-indexed, baseado em STANDARD_CHANNELS)
# STANDARD_CHANNELS = [Fp1,F3,C3,P3,O1,F7,T3,T5,Fc1,Fc5,Cp1,Cp5,F9,Fz,Cz,Pz,
#                      Fp2,F4,C4,P4,O2,F8,T4,T6,Fc2,Fc6,Cp2,Cp6,F10]
#  idx:                  0   1  2  3  4  5  6  7   8   9  10  11 12 13 14 15
#                       16  17 18 19 20 21 22 23  24  25  26  27 28

FRONTAL_IDX  = [0,  1,  5, 12, 13, 16, 17, 21, 28]  # Fp1,F3,F7,F9,Fz,Fp2,F4,F8,F10
CENTRAL_IDX  = [2,  6,  7,  8,  9, 10, 11, 14, 18, 22, 23, 24, 25, 26, 27]  # C*,T*,Fc*,Cp*,Cz
PARIETAL_IDX = [3,  4, 15, 19, 20]  # P3,O1,Pz,P4,O2

CLASS_COLORS = {
    "pre_ictal":  "#3498db",
    "ictal":      "#e74c3c",
    "pos_ictal":  "#2ecc71",
    "normal":     "#95a5a6",
}


def _channel_spectrogram(signal: np.ndarray, fs: int = 512,
                          nperseg: int = 256, noverlap: int = 128) -> np.ndarray:
    """Calcula espectograma de um canal em escala log (dB)."""
    _, _, Sxx = scipy_spectrogram(signal, fs=fs, nperseg=nperseg, noverlap=noverlap)
    return 10.0 * np.log10(Sxx + 1e-10)


def _group_mean_spectrogram(data: np.ndarray, indices: list, fs: int,
                             nperseg: int, noverlap: int) -> np.ndarray:
    """Media dos espectogramas de um grupo de canais."""
    n_ch = data.shape[0]
    valid = [i for i in indices if i < n_ch]
    if not valid:
        return None
    spectros = [_channel_spectrogram(data[i], fs, nperseg, noverlap) for i in valid]
    return np.mean(spectros, axis=0)


def _normalize_to_uint8(arr: np.ndarray) -> np.ndarray:
    """Normaliza array para [0, 255] uint8."""
    if arr is None:
        return None
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return np.zeros_like(arr, dtype=np.uint8)
    return ((arr - mn) / (mx - mn) * 255).astype(np.uint8)


def segment_to_spectrogram(
    segment: np.ndarray,
    fs:      int = 512,
    nperseg: int = 256,
    noverlap:int = 128,
) -> np.ndarray:
    """
    Converte um segmento EEG (n_channels, n_samples) em imagem RGB (H, W, 3).

    Parameters
    ----------
    segment : np.ndarray   shape (n_channels, n_samples)
    fs      : int          taxa de amostragem (padrao 512 Hz)
    nperseg : int          tamanho da janela STFT (padrao 256)
    noverlap: int          sobreposicao (padrao 128)

    Returns
    -------
    np.ndarray shape (H, W, 3) dtype uint8
    """
    r = _group_mean_spectrogram(segment, FRONTAL_IDX,  fs, nperseg, noverlap)
    g = _group_mean_spectrogram(segment, CENTRAL_IDX,  fs, nperseg, noverlap)
    b = _group_mean_spectrogram(segment, PARIETAL_IDX, fs, nperseg, noverlap)

    r_n = _normalize_to_uint8(r)
    g_n = _normalize_to_uint8(g)
    b_n = _normalize_to_uint8(b)

    # Resolve shape de referencia
    ref = next(x for x in [r_n, g_n, b_n] if x is not None)
    h, w = ref.shape
    r_f = r_n if r_n is not None else np.zeros((h, w), dtype=np.uint8)
    g_f = g_n if g_n is not None else np.zeros((h, w), dtype=np.uint8)
    b_f = b_n if b_n is not None else np.zeros((h, w), dtype=np.uint8)

    return np.stack([r_f, g_f, b_f], axis=-1)


def save_spectrogram(
    img_array:   np.ndarray,
    output_path: str,
    title:       str  = None,
    show_axes:   bool = False,
) -> None:
    """
    Salva um array RGB como arquivo PNG.

    Parameters
    ----------
    img_array   : np.ndarray  shape (H, W, 3) uint8
    output_path : str         caminho de saida (incluindo .png)
    title       : str         titulo exibido se show_axes=True
    show_axes   : bool        se True, salva com eixos e colorbar; se False, imagem pura
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if show_axes:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(img_array, aspect="auto", origin="lower")
        if title:
            ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Tempo (frames STFT)", fontsize=10)
        ax.set_ylabel("Frequencia (bins)", fontsize=10)
        ax.text(0.01, 0.97, "R=Frontal | G=Central/Temporal | B=Parietal/Occipital",
                transform=ax.transAxes, fontsize=7, va="top",
                color="white", bbox=dict(facecolor="black", alpha=0.4, pad=2))
        plt.tight_layout()
        fig.savefig(str(output_path), dpi=100, bbox_inches="tight")
        plt.close(fig)
    else:
        Image.fromarray(img_array).save(str(output_path))


def plot_class_grid(spectrograms: dict, patient_id: str, seizure_n: int,
                    edf_file: str) -> plt.Figure:
    """
    Plota um grid 2x2 com os 4 espectogramas de uma crise para inspecao visual.

    Parameters
    ----------
    spectrograms : dict  {classe: np.ndarray (H,W,3) ou None}
    patient_id   : str   ex: 'PN00'
    seizure_n    : int   numero da crise
    edf_file     : str   ex: 'PN00-1.edf'

    Returns
    -------
    matplotlib.figure.Figure
    """
    classes = ["pre_ictal", "ictal", "pos_ictal", "normal"]
    labels  = ["Pre-Ictal", "Ictal", "Pos-Ictal", "Normal"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    fig.suptitle(f"{patient_id} | Crise {seizure_n} | {edf_file}",
                 fontsize=14, fontweight="bold")

    for ax, cls, label in zip(axes.flat, classes, labels):
        img = spectrograms.get(cls)
        color = CLASS_COLORS.get(cls, "#333")
        if img is not None:
            ax.imshow(img, aspect="auto", origin="lower")
        else:
            ax.set_facecolor("#f5f5f5")
            ax.text(0.5, 0.5, "Segmento Inviavel",
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=12, color="gray")
        ax.set_title(label, fontsize=12, fontweight="bold", color=color)
        ax.set_xlabel("Frames STFT")
        ax.set_ylabel("Freq (bins)")

    plt.tight_layout()
    return fig
