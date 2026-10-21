"""
image_enhancer.py
-----------------
Tecnicas de melhoria visual para os espectrogramas STFT RGB:
    1. Equalizacao de Histograma Global (apply_histogram_equalization)
    2. CLAHE - Contrast Limited Adaptive Histogram Equalization (apply_clahe)
    3. Ajuste de Brilho (apply_brightness)
    4. Ajuste de Contraste (apply_contrast)
    5. Pipeline combinado selecionado: CLAHE + Ajuste de Contraste (enhance_spectrogram)
"""

import numpy as np


def _hist_eq_channel(ch: np.ndarray) -> np.ndarray:
    """Equalizacao de histograma global em um canal 2D uint8."""
    hist = np.bincount(ch.ravel(), minlength=256).astype(np.float64)
    cdf = np.cumsum(hist)
    cdf_nonzero = cdf[cdf > 0]
    if len(cdf_nonzero) <= 1 or cdf[-1] == cdf_nonzero[0]:
        return ch.copy()
    cdf_min = cdf_nonzero[0]
    lut = np.round((cdf - cdf_min) / (cdf[-1] - cdf_min) * 255.0)
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    return lut[ch]


def apply_histogram_equalization(img: np.ndarray) -> np.ndarray:
    """Aplica equalizacao de histograma global independentemente em cada canal RGB."""
    return np.stack([_hist_eq_channel(img[:, :, c]) for c in range(img.shape[2])], axis=-1)


def _clahe_channel(
    ch: np.ndarray,
    clip_limit: float = 2.5,
    tile_grid_size: tuple = (8, 8),
) -> np.ndarray:
    """CLAHE vetorizado em NumPy para um canal 2D uint8."""
    H, W = ch.shape
    ny, nx = tile_grid_size
    y_edges = np.linspace(0, H, ny + 1, dtype=int)
    x_edges = np.linspace(0, W, nx + 1, dtype=int)
    luts = np.zeros((ny, nx, 256), dtype=np.float32)

    for iy in range(ny):
        y0, y1 = y_edges[iy], y_edges[iy + 1]
        for ix in range(nx):
            x0, x1 = x_edges[ix], x_edges[ix + 1]
            tile = ch[y0:y1, x0:x1]
            hist = np.bincount(tile.ravel(), minlength=256).astype(np.float64)
            limit = max(1.0, clip_limit * (tile.size / 256.0))
            excess = np.maximum(0.0, hist - limit).sum()
            hist = np.minimum(hist, limit) + (excess / 256.0)
            cdf = np.cumsum(hist)
            denom = cdf[-1] - cdf[0]
            if denom > 0:
                luts[iy, ix] = np.clip((cdf - cdf[0]) / denom * 255.0, 0.0, 255.0)
            else:
                luts[iy, ix] = np.arange(256, dtype=np.float32)

    y_centers = 0.5 * (y_edges[:-1] + y_edges[1:] - 1)
    x_centers = 0.5 * (x_edges[:-1] + x_edges[1:] - 1)
    gy = np.interp(np.arange(H, dtype=np.float32), y_centers, np.arange(ny, dtype=np.float32))
    gx = np.interp(np.arange(W, dtype=np.float32), x_centers, np.arange(nx, dtype=np.float32))

    iy0 = np.clip(np.floor(gy).astype(int), 0, ny - 1)
    iy1 = np.clip(iy0 + 1, 0, ny - 1)
    wy = (gy - iy0)[:, None]

    ix0 = np.clip(np.floor(gx).astype(int), 0, nx - 1)
    ix1 = np.clip(ix0 + 1, 0, nx - 1)
    wx = (gx - ix0)[None, :]

    v00 = luts[iy0[:, None], ix0[None, :], ch]
    v01 = luts[iy0[:, None], ix1[None, :], ch]
    v10 = luts[iy1[:, None], ix0[None, :], ch]
    v11 = luts[iy1[:, None], ix1[None, :], ch]

    out = (1 - wy) * ((1 - wx) * v00 + wx * v01) + wy * ((1 - wx) * v10 + wx * v11)
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def apply_clahe(
    img: np.ndarray,
    clip_limit: float = 2.5,
    tile_grid_size: tuple = (8, 8),
) -> np.ndarray:
    """Aplica CLAHE em cada canal RGB."""
    return np.stack(
        [_clahe_channel(img[:, :, c], clip_limit=clip_limit, tile_grid_size=tile_grid_size) for c in range(img.shape[2])],
        axis=-1,
    )


def apply_brightness(img: np.ndarray, beta: float = 35.0) -> np.ndarray:
    """Ajuste linear aditivo de brilho: I_out = clip(I + beta, 0, 255)."""
    return np.clip(img.astype(np.float32) + beta, 0, 255).astype(np.uint8)


def apply_contrast(img: np.ndarray, alpha: float = 1.35, gamma: float = 0.85) -> np.ndarray:
    """
    Ajuste de contraste ancorado em zero:
        I_out = clip(alpha * 255 * (I / 255)^gamma, 0, 255)
    Preserva integralmente os pixels nulos (fundo sem energia espectral).
    """
    norm = img.astype(np.float32) / 255.0
    out = np.power(norm, gamma) * 255.0 * alpha
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def enhance_spectrogram(
    img: np.ndarray,
    clahe_clip_limit: float = 2.5,
    clahe_grid: tuple = (8, 8),
    contrast_alpha: float = 1.35,
    contrast_gamma: float = 0.85,
) -> np.ndarray:
    """
    Pipeline final selecionado para melhoria dos espectrogramas:
        1. CLAHE por canal RGB
        2. Ajuste de Contraste ancorado em zero
    """
    step1 = apply_clahe(img, clip_limit=clahe_clip_limit, tile_grid_size=clahe_grid)
    step2 = apply_contrast(step1, alpha=contrast_alpha, gamma=contrast_gamma)
    return step2

