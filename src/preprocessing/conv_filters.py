"""Implementacao manual de convolucao 2D e filtros de suavizacao, bordas e Sobel."""

import numpy as np

KERNEL_SMOOTHING = (1.0 / 9.0) * np.array(
    [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]], dtype=np.float32
)

KERNEL_EDGE_DETECTION = np.array(
    [[-1.0, -1.0, -1.0], [-1.0, 8.0, -1.0], [-1.0, -1.0, -1.0]], dtype=np.float32
)

KERNEL_SOBEL = np.array(
    [[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]], dtype=np.float32
)


def convolve2d_manual(img: np.ndarray, kernel: np.ndarray, padding: str = "edge") -> np.ndarray:
    """Aplica manualmente convolucao espacial 2D por janela deslizante."""
    k = np.asarray(kernel, dtype=np.float32)
    kh, kw = k.shape
    ph, pw = kh // 2, kw // 2
    img_f = np.asarray(img, dtype=np.float32)

    if img_f.ndim == 2:
        H, W = img_f.shape
        padded = np.pad(img_f, ((ph, ph), (pw, pw)), mode=padding)
        out = np.zeros((H, W), dtype=np.float32)
        for i in range(H):
            for j in range(W):
                out[i, j] = np.sum(padded[i : i + kh, j : j + kw] * k)
        return out

    H, W, C = img_f.shape
    padded = np.pad(img_f, ((ph, ph), (pw, pw), (0, 0)), mode=padding)
    out = np.zeros((H, W, C), dtype=np.float32)
    k3 = k[:, :, None]
    for i in range(H):
        for j in range(W):
            out[i, j, :] = np.sum(padded[i : i + kh, j : j + kw, :] * k3, axis=(0, 1))
    return out


def apply_smoothing_filter(img: np.ndarray, padding: str = "edge") -> np.ndarray:
    """Aplica o Kernel de Suavizacao (1/9 Box Blur 3x3)."""
    raw = convolve2d_manual(img, KERNEL_SMOOTHING, padding=padding)
    return np.clip(np.round(raw), 0, 255).astype(np.uint8)


def _format_edge_output(img: np.ndarray, raw: np.ndarray, mode: str) -> np.ndarray:
    if mode == "abs":
        res = np.abs(raw)
    elif mode == "clip":
        res = raw
    elif mode == "sharpen":
        res = img.astype(np.float32) + np.abs(raw)
    else:
        raise ValueError(f"Modo invalido '{mode}'.")
    return np.clip(np.round(res), 0, 255).astype(np.uint8)


def apply_edge_detector_filter(img: np.ndarray, mode: str = "abs", padding: str = "edge") -> np.ndarray:
    """Aplica o Kernel Detector de Bordas 3x3."""
    return _format_edge_output(img, convolve2d_manual(img, KERNEL_EDGE_DETECTION, padding=padding), mode)


def apply_sobel_filter(img: np.ndarray, mode: str = "abs", padding: str = "edge") -> np.ndarray:
    """Aplica o Filtro Sobel 3x3."""
    return _format_edge_output(img, convolve2d_manual(img, KERNEL_SOBEL, padding=padding), mode)
