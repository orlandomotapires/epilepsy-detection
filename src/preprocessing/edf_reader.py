"""Carregamento de arquivos EDF da base Siena Scalp EEG."""

import mne

STANDARD_CHANNELS = [
    "Fp1", "F3",  "C3",  "P3",  "O1",  "F7",  "T3",  "T5",
    "Fc1", "Fc5", "Cp1", "Cp5", "F9",  "Fz",  "Cz",  "Pz",
    "Fp2", "F4",  "C4",  "P4",  "O2",  "F8",  "T4",  "T6",
    "Fc2", "Fc6", "Cp2", "Cp6", "F10",
]

IGNORE_PATTERNS = ("ekg", "ecg", "spo2", "hr", "mk")


def _normalize_channel_name(name: str) -> str:
    name = name.strip()
    for prefix in ("EEG ", "EMG ", "EOG "):
        if name.upper().startswith(prefix):
            return name[len(prefix):].strip()
    return name


def load_edf(path: str, preload: bool = False) -> tuple:
    """Carrega um arquivo EDF e seleciona os canais EEG padrao disponiveis."""
    raw = mne.io.read_raw_edf(str(path), preload=preload, verbose=False)
    raw.rename_channels({ch: _normalize_channel_name(ch) for ch in raw.ch_names})

    eeg_present = [
        ch for ch in raw.ch_names
        if not ch.lower().strip().startswith(IGNORE_PATTERNS)
    ]
    available = [ch for ch in STANDARD_CHANNELS if ch in eeg_present]
    if not available:
        raise ValueError(f"Nenhum canal EEG padrao encontrado em: {path}")

    raw.pick(available)
    raw.reorder_channels(available)

    meta = {
        "fs": int(raw.info["sfreq"]),
        "n_channels": len(available),
        "duration_s": float(raw.times[-1]),
        "channel_names": available,
        "path": str(path),
    }
    return raw, meta
