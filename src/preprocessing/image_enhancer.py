"""Tecnicas de melhoria visual para espectrogramas STFT RGB."""

import numpy as np


def _hist_eq_channel(ch: np.ndarray) -> np.ndarray:
    hist = np.bincount(ch.ravel(), minlength=256).astype(np.float64)
    cdf = np.cumsum(hist)
    nz = cdf[cdf > 0]
    if len(nz) <= 1 or cdf[-1] == nz[0]:
        return ch.copy()
    lut = np.clip(np.round((cdf - nz[0]) / (cdf[-1] - nz[0]) * 255.0), 0, 255).astype(np.uint8)
    return lut[ch]


def apply_histogram_equalization(img: np.ndarray) -> np.ndarray:
    """Equalizacao de histograma global por canal RGB."""
    return np.stack([_hist_eq_channel(img[:, :, c]) for c in range(img.shape[2])], axis=-1)


def _clahe_channel(ch: np.ndarray, clip_limit: float = 2.5, tile_grid_size: tuple = (8, 8)) -> np.ndarray:
    H, W = ch.shape
    ny, nx = tile_grid_size
    y_edges = np.linspace(0, H, ny + 1, dtype=int)
    x_edges = np.linspace(0, W, nx + 1, dtype=int)
    luts = np.zeros((ny, nx, 256), dtype=np.float32)

    for iy in range(ny):
        for ix in range(nx):
            tile = ch[y_edges[iy]:y_edges[iy + 1], x_edges[ix]:x_edges[ix + 1]]
            hist = np.bincount(tile.ravel(), minlength=256).astype(np.float64)
            limit = max(1.0, clip_limit * (tile.size / 256.0))
            excess = np.maximum(0.0, hist - limit).sum()
            cdf = np.cumsum(np.minimum(hist, limit) + excess / 256.0)
            denom = cdf[-1] - cdf[0]
            luts[iy, ix] = np.clip((cdf - cdf[0]) / denom * 255.0, 0.0, 255.0) if denom > 0 else np.arange(256)

    yc = 0.5 * (y_edges[:-1] + y_edges[1:] - 1)
    xc = 0.5 * (x_edges[:-1] + x_edges[1:] - 1)
    gy = np.interp(np.arange(H, dtype=np.float32), yc, np.arange(ny, dtype=np.float32))
    gx = np.interp(np.arange(W, dtype=np.float32), xc, np.arange(nx, dtype=np.float32))

    iy0 = np.clip(np.floor(gy).astype(int), 0, ny - 1)
    iy1 = np.clip(iy0 + 1, 0, ny - 1)
    ix0 = np.clip(np.floor(gx).astype(int), 0, nx - 1)
    ix1 = np.clip(ix0 + 1, 0, nx - 1)
    wy, wx = (gy - iy0)[:, None], (gx - ix0)[None, :]

    v00, v01 = luts[iy0[:, None], ix0[None, :], ch], luts[iy0[:, None], ix1[None, :], ch]
    v10, v11 = luts[iy1[:, None], ix0[None, :], ch], luts[iy1[:, None], ix1[None, :], ch]
    out = (1 - wy) * ((1 - wx) * v00 + wx * v01) + wy * ((1 - wx) * v10 + wx * v11)
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def apply_clahe(img: np.ndarray, clip_limit: float = 2.5, tile_grid_size: tuple = (8, 8)) -> np.ndarray:
    """CLAHE aplicado em cada canal RGB."""
    return np.stack([_clahe_channel(img[:, :, c], clip_limit, tile_grid_size) for c in range(img.shape[2])], axis=-1)


def apply_brightness(img: np.ndarray, beta: float = 35.0) -> np.ndarray:
    """Ajuste linear de brilho."""
    return np.clip(img.astype(np.float32) + beta, 0, 255).astype(np.uint8)


def apply_contrast(img: np.ndarray, alpha: float = 1.35, gamma: float = 0.85) -> np.ndarray:
    """Ajuste de contraste ancorado em zero."""
    out = np.power(img.astype(np.float32) / 255.0, gamma) * 255.0 * alpha
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def enhance_spectrogram(img: np.ndarray) -> np.ndarray:
    """Pipeline selecionado: CLAHE + Ajuste de Contraste."""
    return apply_contrast(apply_clahe(img))
