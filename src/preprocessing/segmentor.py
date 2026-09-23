"""
segmentor.py
------------
Calcula as janelas temporais para cada uma das 4 classes e extrai
os segmentos correspondentes de um objeto MNE Raw usando leitura lazy.

Classes:
    - ictal     : 90 s centralizados no ponto medio da crise
    - pre_ictal : 90 s imediatamente anteriores ao inicio do ictal
    - pos_ictal : 90 s imediatamente posteriores ao fim do ictal
    - normal    : 90 s em regiao livre de qualquer zona de crise
"""

import random
import warnings
import numpy as np


WINDOW_S = 90    # janela fixa em segundos
FS       = 512   # taxa de amostragem padrao


def compute_windows(
    sz_start_rel_s: float,
    sz_end_rel_s:   float,
    total_s:        float,
    all_sz_starts:  list = None,
    all_sz_ends:    list = None,
    window_s:       int  = WINDOW_S,
) -> dict:
    """
    Calcula os intervalos [start_s, end_s) de cada classe sem tocar em dados.

    Parameters
    ----------
    sz_start_rel_s : float
        Inicio da crise em segundos relativos ao inicio do EDF.
    sz_end_rel_s : float
        Fim da crise em segundos relativos ao inicio do EDF.
    total_s : float
        Duracao total do EDF em segundos.
    all_sz_starts : list of float, optional
        Inicios de todas as crises do arquivo (para computar zonas proibidas
        do segmento normal). Se None, usa apenas a crise atual.
    all_sz_ends : list of float, optional
        Fins de todas as crises do arquivo. Deve ter o mesmo comprimento de
        all_sz_starts.
    window_s : int
        Tamanho da janela em segundos (padrao: 90).

    Returns
    -------
    dict
        Chaves: 'ictal', 'pre_ictal', 'pos_ictal', 'normal'.
        Cada valor e (start_s, end_s) ou None se inviavel.
    """
    half = window_s / 2.0  # 45 s
    sz_center_s = (sz_start_rel_s + sz_end_rel_s) / 2.0

    windows = {}

    # ── ictal ────────────────────────────────────────────────────────────────
    ic_start_s = sz_center_s - half
    ic_end_s   = sz_center_s + half

    if ic_start_s >= 0 and ic_end_s <= total_s:
        windows["ictal"] = (ic_start_s, ic_end_s)
    else:
        warnings.warn(
            f"[segmentor] ictal inviavel: [{ic_start_s:.1f}, {ic_end_s:.1f}] "
            f"fora de [0, {total_s:.1f}]"
        )
        windows["ictal"] = None

    # ── pre_ictal ────────────────────────────────────────────────────────────
    pre_start_s = ic_start_s - window_s
    pre_end_s   = ic_start_s

    if pre_start_s >= 0 and pre_end_s <= total_s:
        windows["pre_ictal"] = (pre_start_s, pre_end_s)
    else:
        warnings.warn(
            f"[segmentor] pre_ictal inviavel: [{pre_start_s:.1f}, {pre_end_s:.1f}]"
        )
        windows["pre_ictal"] = None

    # ── pos_ictal ────────────────────────────────────────────────────────────
    pos_start_s = ic_end_s
    pos_end_s   = ic_end_s + window_s

    if pos_start_s >= 0 and pos_end_s <= total_s:
        windows["pos_ictal"] = (pos_start_s, pos_end_s)
    else:
        warnings.warn(
            f"[segmentor] pos_ictal inviavel: [{pos_start_s:.1f}, {pos_end_s:.1f}]"
        )
        windows["pos_ictal"] = None

    # ── normal ───────────────────────────────────────────────────────────────
    if all_sz_starts is None or all_sz_ends is None:
        all_sz_starts = [sz_start_rel_s]
        all_sz_ends   = [sz_end_rel_s]

    forbidden_zones = []
    for s, e in zip(all_sz_starts, all_sz_ends):
        c = (s + e) / 2.0
        f_start = max(0.0, c - 135.0)
        f_end   = min(total_s, c + 135.0)
        forbidden_zones.append((f_start, f_end))

    # Unifica zonas sobrepostas
    forbidden_zones.sort(key=lambda x: x[0])
    merged = []
    for z in forbidden_zones:
        if not merged:
            merged.append(list(z))
        elif z[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], z[1])
        else:
            merged.append(list(z))

    # Identifica intervalos livres com duracao >= window_s
    free_zones = []
    cursor = 0.0
    for z in merged:
        if z[0] - cursor >= window_s:
            free_zones.append((cursor, z[0]))
        cursor = max(cursor, z[1])
    if total_s - cursor >= window_s:
        free_zones.append((cursor, total_s))

    if free_zones:
        rng = random.Random(int(sz_center_s * 100))
        weights = [max(0.1, fz[1] - fz[0]) for fz in free_zones]
        chosen  = rng.choices(free_zones, weights=weights, k=1)[0]
        max_start = chosen[1] - window_s
        norm_start_s = rng.uniform(chosen[0], max_start)
        windows["normal"] = (norm_start_s, norm_start_s + window_s)
    else:
        warnings.warn("[segmentor] normal inviavel: nenhuma zona livre encontrada.")
        windows["normal"] = None

    return windows


def extract_segments(
    raw,
    sz_start_rel_s: float,
    sz_end_rel_s:   float,
    all_sz_starts:  list = None,
    all_sz_ends:    list = None,
    window_s:       int  = WINDOW_S,
    fs:             int  = FS,
) -> dict:
    """
    Extrai 4 segmentos de `window_s` segundos usando leitura lazy do MNE Raw.

    Apenas os samples de cada janela sao lidos do disco, sem carregar o
    arquivo EDF completo em memoria.

    Parameters
    ----------
    raw : mne.io.Raw
        Objeto retornado por load_edf() com preload=False.
    sz_start_rel_s : float
        Inicio da crise em segundos relativos ao inicio do EDF.
    sz_end_rel_s : float
        Fim da crise em segundos relativos ao inicio do EDF.
    all_sz_starts : list of float, optional
        Inicios de todas as crises do arquivo EDF (para segmento normal).
    all_sz_ends : list of float, optional
        Fins de todas as crises do arquivo EDF.
    window_s : int
        Tamanho da janela em segundos (padrao: 90).
    fs : int
        Taxa de amostragem em Hz (padrao: 512).

    Returns
    -------
    dict com chaves: 'pre_ictal', 'ictal', 'pos_ictal', 'normal'.
    Cada valor e np.ndarray shape (n_channels, window_s*fs) ou None.
    """
    total_s  = float(raw.times[-1])
    n_total  = raw.n_times
    win      = int(round(window_s * fs))
    segments = {}

    windows = compute_windows(
        sz_start_rel_s=sz_start_rel_s,
        sz_end_rel_s=sz_end_rel_s,
        total_s=total_s,
        all_sz_starts=all_sz_starts,
        all_sz_ends=all_sz_ends,
        window_s=window_s,
    )

    for cls, interval in windows.items():
        if interval is None:
            segments[cls] = None
            continue

        start_s, end_s = interval
        start_samp = max(0, int(round(start_s * fs)))
        end_samp   = min(n_total, start_samp + win)

        # Leitura lazy: so este trecho e lido do disco
        data, _ = raw[:, start_samp:end_samp]
        segments[cls] = data

    return segments
