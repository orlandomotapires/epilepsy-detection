"""
segmentor.py
------------
Extrai segmentos temporais de 90 s para cada uma das 4 classes:
    - ictal: 90 s centralizados no ponto medio da crise (centro - 45 s ate centro + 45 s)
    - pre_ictal: 90 s imediatamente anteriores ao ictal (centro - 135 s ate centro - 45 s)
    - pos_ictal: 90 s imediatamente posteriores ao ictal (centro + 45 s ate centro + 135 s)
    - normal: 90 s em regiao livre que nao colida com as zonas de crise de nenhuma ocorrencia
"""

import random
import warnings
import numpy as np

WINDOW_S = 90    # janela fixa em segundos
FS       = 512   # taxa de amostragem padrao


def extract_segments(
    raw_data:       np.ndarray,
    sz_start_rel_s: float,
    sz_end_rel_s:   float,
    all_sz_starts:  list = None,
    all_sz_ends:    list = None,
    window_s:       int  = WINDOW_S,
    fs:             int  = FS,
) -> dict:
    """
    Extrai 4 segmentos de `window_s` segundos de um sinal EEG.

    Parameters
    ----------
    raw_data : np.ndarray
        Shape (n_channels, n_samples). Dados brutos do EDF.
    sz_start_rel_s : float
        Inicio da crise em segundos relativos ao inicio do EDF.
    sz_end_rel_s : float
        Fim da crise em segundos relativos ao inicio do EDF.
    all_sz_starts : list of float, optional
        Lista com inicios de TODAS as crises do arquivo EDF.
    all_sz_ends : list of float, optional
        Lista com fins de TODAS as crises do arquivo EDF.
    window_s : int
        Tamanho da janela em segundos (padrao: 90).
    fs : int
        Taxa de amostragem em Hz (padrao: 512).

    Returns
    -------
    dict com chaves: 'pre_ictal', 'ictal', 'pos_ictal', 'normal'
    Cada valor e np.ndarray shape (n_channels, window_s*fs) ou None se inviavel.
    """
    n_samples = raw_data.shape[1]
    total_s   = n_samples / fs
    win       = int(round(window_s * fs))
    segments  = {}

    # Ponto medio da crise atual
    sz_center_s = (sz_start_rel_s + sz_end_rel_s) / 2.0

    # ── ictal ─────────────────────────────────────────────────────────────────
    # Centralizado no ponto medio da crise: [centro - 45s, centro + 45s]
    ic_start_s = sz_center_s - 45.0
    ic_start   = int(round(ic_start_s * fs))
    ic_end     = ic_start + win

    if ic_start >= 0 and ic_end <= n_samples:
        segments["ictal"] = raw_data[:, ic_start:ic_end].copy()
    else:
        warnings.warn(
            f"[segmentor] ictal inviavel: janela [{ic_start}, {ic_end}] "
            f"fora dos limites [0, {n_samples}]"
        )
        segments["ictal"] = None

    # ── pre_ictal ─────────────────────────────────────────────────────────────
    # 90 s imediatamente anteriores ao inicio do ictal: [ic_start - 90s, ic_start]
    pre_start = ic_start - win
    pre_end   = ic_start

    if pre_start >= 0 and pre_end <= n_samples:
        segments["pre_ictal"] = raw_data[:, pre_start:pre_end].copy()
    else:
        warnings.warn(
            f"[segmentor] pre_ictal inviavel: janela [{pre_start}, {pre_end}] "
            f"fora dos limites [0, {n_samples}]"
        )
        segments["pre_ictal"] = None

    # ── pos_ictal ─────────────────────────────────────────────────────────────
    # 90 s imediatamente posteriores ao fim do ictal: [ic_end, ic_end + 90s]
    pos_start = ic_end
    pos_end   = pos_start + win

    if pos_start >= 0 and pos_end <= n_samples:
        segments["pos_ictal"] = raw_data[:, pos_start:pos_end].copy()
    else:
        warnings.warn(
            f"[segmentor] pos_ictal inviavel: janela [{pos_start}, {pos_end}] "
            f"fora dos limites [0, {n_samples}]"
        )
        segments["pos_ictal"] = None

    # ── normal ────────────────────────────────────────────────────────────────
    # Segmento de 90 s em regiao livre de crises.
    # Para cada crise, o intervalo de exclusao abrange [centro - 135s, centro + 135s]
    # (ou seja, a uniao exata de pre_ictal, ictal e pos_ictal).
    if all_sz_starts is None or all_sz_ends is None:
        all_sz_starts = [sz_start_rel_s]
        all_sz_ends   = [sz_end_rel_s]

    forbidden_zones = []
    for s, e in zip(all_sz_starts, all_sz_ends):
        c = (s + e) / 2.0
        f_start = max(0.0, c - 135.0)
        f_end   = min(total_s, c + 135.0)
        forbidden_zones.append((f_start, f_end))

    # Unifica zonas de exclusao sobrepostas
    forbidden_zones.sort(key=lambda x: x[0])
    merged_zones = []
    for z in forbidden_zones:
        if not merged_zones:
            merged_zones.append(list(z))
        else:
            last = merged_zones[-1]
            if z[0] <= last[1]:
                last[1] = max(last[1], z[1])
            else:
                merged_zones.append(list(z))

    # Identifica intervalos livres com duracao >= window_s
    free_zones = []
    current = 0.0
    for z in merged_zones:
        if z[0] - current >= window_s:
            free_zones.append((current, z[0]))
        current = max(current, z[1])
    if total_s - current >= window_s:
        free_zones.append((current, total_s))

    if free_zones:
        # Seed deterministico baseado no centro da crise para reprodutibilidade
        rng = random.Random(int(sz_center_s * 100))

        # Seleciona uma zona livre ponderada pelo tamanho
        weights = [max(0.1, fz[1] - fz[0]) for fz in free_zones]
        chosen_zone = rng.choices(free_zones, weights=weights, k=1)[0]

        # Ponto de inicio aleatorio dentro da zona selecionada
        max_start = chosen_zone[1] - window_s
        norm_start_s = rng.uniform(chosen_zone[0], max_start)

        norm_start = int(round(norm_start_s * fs))
        norm_end   = norm_start + win

        if norm_start >= 0 and norm_end <= n_samples:
            segments["normal"] = raw_data[:, norm_start:norm_end].copy()
        else:
            segments["normal"] = None
    else:
        warnings.warn(
            f"[segmentor] normal inviavel: Nenhuma zona livre de {window_s}s encontrada."
        )
        segments["normal"] = None

    return segments
