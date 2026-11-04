"""Extracao das janelas temporais (pre_ictal, ictal, pos_ictal, normal) do EEG."""

import random

WINDOW_S = 90
FS = 512


def compute_windows(
    sz_start_rel_s: float,
    sz_end_rel_s: float,
    total_s: float,
    all_sz_starts: list = None,
    all_sz_ends: list = None,
    window_s: int = WINDOW_S,
) -> dict:
    """Calcula os intervalos [start_s, end_s) de cada classe."""
    half = window_s / 2.0
    sz_center_s = (sz_start_rel_s + sz_end_rel_s) / 2.0

    ic_start_s, ic_end_s = sz_center_s - half, sz_center_s + half
    pre_start_s, pre_end_s = ic_start_s - window_s, ic_start_s
    pos_start_s, pos_end_s = ic_end_s, ic_end_s + window_s

    windows = {
        "ictal": (ic_start_s, ic_end_s) if (ic_start_s >= 0 and ic_end_s <= total_s) else None,
        "pre_ictal": (pre_start_s, pre_end_s) if (pre_start_s >= 0 and pre_end_s <= total_s) else None,
        "pos_ictal": (pos_start_s, pos_end_s) if (pos_start_s >= 0 and pos_end_s <= total_s) else None,
        "normal": None,
    }

    if all_sz_starts is None or all_sz_ends is None:
        all_sz_starts, all_sz_ends = [sz_start_rel_s], [sz_end_rel_s]

    forbidden = sorted(
        (max(0.0, (s + e) / 2.0 - 135.0), min(total_s, (s + e) / 2.0 + 135.0))
        for s, e in zip(all_sz_starts, all_sz_ends)
    )
    merged = []
    for z in forbidden:
        if not merged or z[0] > merged[-1][1]:
            merged.append(list(z))
        else:
            merged[-1][1] = max(merged[-1][1], z[1])

    free_zones, cursor = [], 0.0
    for z in merged:
        if z[0] - cursor >= window_s:
            free_zones.append((cursor, z[0]))
        cursor = max(cursor, z[1])
    if total_s - cursor >= window_s:
        free_zones.append((cursor, total_s))

    if free_zones:
        rng = random.Random(int(sz_center_s * 100))
        chosen = rng.choices(free_zones, weights=[fz[1] - fz[0] for fz in free_zones], k=1)[0]
        norm_start_s = rng.uniform(chosen[0], chosen[1] - window_s)
        windows["normal"] = (norm_start_s, norm_start_s + window_s)

    return windows


def extract_segments(
    raw,
    sz_start_rel_s: float,
    sz_end_rel_s: float,
    all_sz_starts: list = None,
    all_sz_ends: list = None,
    window_s: int = WINDOW_S,
    fs: int = FS,
) -> dict:
    """Extrai os 4 segmentos de `window_s` segundos a partir do objeto MNE Raw."""
    windows = compute_windows(
        sz_start_rel_s, sz_end_rel_s, float(raw.times[-1]),
        all_sz_starts, all_sz_ends, window_s,
    )
    win = int(round(window_s * fs))
    segments = {}

    for cls, interval in windows.items():
        if interval is None:
            segments[cls] = None
        else:
            start_samp = max(0, int(round(interval[0] * fs)))
            end_samp = min(raw.n_times, start_samp + win)
            segments[cls], _ = raw[:, start_samp:end_samp]

    return segments
