"""
edf_reader.py
-------------
Carrega e valida arquivos EDF da base Siena Scalp EEG.

Nota: Os canais no EDF da base Siena aparecem com prefixo "EEG "
(ex: "EEG Fp1"). Este modulo normaliza os nomes removendo o prefixo
antes de fazer o matching com STANDARD_CHANNELS.
"""

import mne
from pathlib import Path

# 29 canais EEG padrao
# 29 canais EEG padrao (sem prefixo)
STANDARD_CHANNELS = [
    "Fp1", "F3",  "C3",  "P3",  "O1",  "F7",  "T3",  "T5",
    "Fc1", "Fc5", "Cp1", "Cp5", "F9",  "Fz",  "Cz",  "Pz",
    "Fp2", "F4",  "C4",  "P4",  "O2",  "F8",  "T4",  "T6",
    "Fc2", "Fc6", "Cp2", "Cp6", "F10",
]

EKG_PATTERNS = ["ekg", "ecg"]
# Padroes de canais a ignorar (nao sao EEG cerebral)
IGNORE_PATTERNS = ["ekg", "ecg", "spo2", "hr", "mk"]


def _is_ekg(name: str) -> bool:
    return any(p in name.lower() for p in EKG_PATTERNS)
def _should_ignore(name: str) -> bool:
    """Retorna True se o canal deve ser ignorado (EKG, SPO2, HR, etc.)."""
    lower = name.lower().strip()
    return any(p == lower or lower.startswith(p) for p in IGNORE_PATTERNS)


def _normalize_channel_name(name: str) -> str:
    """
    Normaliza o nome do canal removendo prefixos comuns.

    Exemplos:
        'EEG Fp1'  -> 'Fp1'
        'EEG EKG'  -> 'EKG'
        'EMG EMG1' -> 'EMG1'
        'Fp1'      -> 'Fp1'   (sem alteracao)
    """
    name = name.strip()
    for prefix in ("EEG ", "EMG ", "EOG "):
        if name.upper().startswith(prefix):
            return name[len(prefix):].strip()
    return name


def load_edf(path: str) -> tuple:
    """
    Carrega um arquivo EDF e seleciona os 29 canais EEG padrao.

    Trata automaticamente o prefixo "EEG " nos nomes dos canais da base Siena.

    Parameters
    ----------
    path : str
        Caminho para o arquivo .edf.

    Returns
    -------
    raw : mne.io.Raw
        Objeto MNE com apenas os canais EEG disponiveis (EKG excluido).
        Objeto MNE com os canais EEG renomeados (sem prefixo "EEG ").
    meta : dict
        fs, n_channels, duration_s, channel_names, missing_channels, path.
    """
    raw = mne.io.read_raw_edf(str(path), preload=True, verbose=False)
    raw.rename_channels({ch: ch.strip() for ch in raw.ch_names})

    eeg_present = [ch for ch in raw.ch_names if not _is_ekg(ch)]
    available   = [ch for ch in STANDARD_CHANNELS if ch in eeg_present]
    missing     = [ch for ch in STANDARD_CHANNELS if ch not in eeg_present]
    # Passo 1: Remove prefixo "EEG " / "EMG " / "EOG " dos nomes
    rename_map = {ch: _normalize_channel_name(ch) for ch in raw.ch_names}
    raw.rename_channels(rename_map)

    # Passo 2: Filtra canais nao-EEG (EKG, SPO2, HR, MK, etc.)
    eeg_present = [ch for ch in raw.ch_names if not _should_ignore(ch)]

    # Passo 3: Seleciona apenas canais do padrao de 29
    available = [ch for ch in STANDARD_CHANNELS if ch in eeg_present]
    missing   = [ch for ch in STANDARD_CHANNELS if ch not in eeg_present]

    if not available:
        raise ValueError(f"Nenhum canal EEG padrao encontrado em: {path}")
        raise ValueError(
            f"Nenhum canal EEG padrao encontrado em: {path}\n"
            f"Canais presentes apos normalizacao: {raw.ch_names}"
        )

    raw.pick_channels(available)

    meta = {
        "fs":               int(raw.info["sfreq"]),
        "n_channels":       len(available),
        "duration_s":       float(raw.times[-1]),
        "channel_names":    available,
        "missing_channels": missing,
        "path":             str(path),
    }
    return raw, meta
