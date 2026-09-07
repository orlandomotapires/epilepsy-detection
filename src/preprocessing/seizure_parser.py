"""
seizure_parser.py
-----------------
Parseia o arquivo Seizures-list-PNxx.txt da base Siena Scalp EEG.

Formato de entrada:
    Seizure n 1
    File name: PN00-1.edf
    Registration start time: 19.39.33
    Registration end time:  20.22.58
    Seizure start time: 19.58.36
    Seizure end time: 19.59.46
"""

import re
from pathlib import Path


def _hms_to_seconds(hms: str) -> float:
    """Converte 'HH.MM.SS' para segundos totais."""
    parts = re.split(r"[.:\s]+", hms.strip())
    if len(parts) < 3:
        raise ValueError(f"Formato de tempo invalido: '{hms}'")
    return float(int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]))


def parse_seizure_list(txt_path: str) -> list:
    """
    Le e parseia o arquivo Seizures-list-PNxx.txt.

    Parameters
    ----------
    txt_path : str
        Caminho para o arquivo .txt de anotacoes.

    Returns
    -------
    list of dict com campos:
        seizure_n, edf_file,
        reg_start_s, reg_end_s, reg_duration_s,
        sz_start_s, sz_end_s, sz_duration_s,
        sz_start_rel_s, sz_end_rel_s   (relativos ao inicio do EDF)

    Raises
    ------
    FileNotFoundError se o arquivo nao existir.
    """
    p = Path(txt_path)
    if not p.exists():
        raise FileNotFoundError(
            f"Arquivo de anotacoes nao encontrado: {p}\n"
            "Verifique se os dados foram baixados."
        )

    lines    = p.read_text(encoding="utf-8", errors="replace").splitlines()
    seizures = []
    current  = {}

    for raw_line in lines:
        line  = raw_line.strip()
        lower = line.lower()

        if re.match(r"seizure\s+n\s*\d+", lower):
            if current and "edf_file" in current:
                seizures.append(current)
            m       = re.search(r"(\d+)", line)
            current = {"seizure_n": int(m.group(1)) if m else len(seizures) + 1}

        elif lower.startswith("file name:"):
            current["edf_file"] = line.split(":", 1)[1].strip()

        elif lower.startswith("registration start time:"):
            current["reg_start_s"] = _hms_to_seconds(line.split(":", 1)[1])

        elif lower.startswith("registration end time:"):
            current["reg_end_s"] = _hms_to_seconds(line.split(":", 1)[1])

        elif lower.startswith("seizure start time:"):
            current["sz_start_s"] = _hms_to_seconds(line.split(":", 1)[1])

        elif lower.startswith("seizure end time:"):
            current["sz_end_s"] = _hms_to_seconds(line.split(":", 1)[1])

    if current and "edf_file" in current:
        seizures.append(current)

    # Calcula campos derivados
    for sz in seizures:
        rs = sz.get("reg_start_s", 0.0)
        re_ = sz.get("reg_end_s",   0.0)
        ss = sz.get("sz_start_s",  0.0)
        se = sz.get("sz_end_s",    0.0)
        sz["reg_duration_s"] = re_ - rs
        sz["sz_start_rel_s"] = ss - rs
        sz["sz_end_rel_s"]   = se - rs
        sz["sz_duration_s"]  = se - ss

    return seizures
