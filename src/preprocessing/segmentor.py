"""
segmentor.py
------------
Extrai segmentos temporais de 90 s para cada classe:
    pre_ictal, ictal, pos_ictal, normal.
"""

import numpy as np
import warnings
import random

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
        Lista com inicios de TODAS as crises do arquivo.
    all_sz_ends : list of float, optional
        Lista com fins de TODAS as crises do arquivo.
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
    win       = window_s * fs
    segments  = {}

    # ── pre_ictal ─────────────────────────────────────────────────────────────
    pre_end   = int(sz_start_rel_s * fs)
    pre_start = pre_end - win
    if pre_start >= 0 and pre_end <= n_samples:
        segments["pre_ictal"] = raw_data[:, pre_start:pre_end].copy()
    else:
        segments["pre_ictal"] = None

    # ── ictal ─────────────────────────────────────────────────────────────────
    ic_start = int(sz_start_rel_s * fs)
    ic_end   = ic_start + win
    if ic_start >= 0 and ic_end <= n_samples:
        segments["ictal"] = raw_data[:, ic_start:ic_end].copy()
    else:
        segments["ictal"] = None

    # ── pos_ictal ─────────────────────────────────────────────────────────────
    pos_start = int(sz_end_rel_s * fs)
    pos_end   = pos_start + win
    if pos_start >= 0 and pos_end <= n_samples:
        segments["pos_ictal"] = raw_data[:, pos_start:pos_end].copy()
    else:
        segments["pos_ictal"] = None

    # ── normal ────────────────────────────────────────────────────────────────
    # Para ser "normal", o segmento precisa estar TOTALMENTE fora de QUALQUER
    # periodo [sz_start - window_s, sz_end + window_s] de todas as crises do EDF.
    
    if all_sz_starts is None or all_sz_ends is None:
        all_sz_starts = [sz_start_rel_s]
        all_sz_ends   = [sz_end_rel_s]
        
    forbidden_zones = []
    for s, e in zip(all_sz_starts, all_sz_ends):
        forbidden_zones.append((max(0, s - window_s), min(total_s, e + window_s)))
        
    # Ordena e une zonas sobrepostas para facilitar a busca
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
                
    # Encontra intervalos livres (free_zones)
    free_zones = []
    current = 0.0
    for z in merged_zones:
        if z[0] - current >= window_s:
            free_zones.append((current, z[0]))
        current = max(current, z[1])
    if total_s - current >= window_s:
        free_zones.append((current, total_s))
        
    if free_zones:
        # Usa o timestamp de inicio como seed para ser deterministico por crise
        rng = random.Random(int(sz_start_rel_s * 100))
        
        # Escolhe aleatoriamente uma zona livre com base em pesos (tamanho da zona)
        weights = [max(0.1, fz[1] - fz[0]) for fz in free_zones]
        chosen_zone = rng.choices(free_zones, weights=weights, k=1)[0]
        
        # Escolhe um ponto de inicio aleatorio dentro da zona selecionada
        max_start = chosen_zone[1] - window_s
        norm_start_s = rng.uniform(chosen_zone[0], max_start)
        
        norm_start = int(norm_start_s * fs)
        norm_end   = norm_start + win
        
        if norm_start >= 0 and norm_end <= n_samples:
            segments["normal"] = raw_data[:, norm_start:norm_end].copy()
        else:
            segments["normal"] = None
    else:
        warnings.warn(f"[segmentor] normal inviavel: Nenhuma zona livre de {window_s}s encontrada.")
        segments["normal"] = None

    return segments
