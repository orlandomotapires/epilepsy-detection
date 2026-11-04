"""Leitura dos arquivos Seizures-list-PNxx.txt da base Siena Scalp EEG."""

import re
from pathlib import Path


def _hms_to_seconds(hms: str) -> float:
    parts = re.split(r"[.:\s]+", hms.strip())
    return float(int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]))


def _normalize_edf_name(name: str) -> str:
    name = name.strip()
    m = re.match(r"^PN[O0]?(\d)(\d)?-([\w.]*)\.edf$", name, flags=re.IGNORECASE)
    if not m:
        return name
    pid = (m.group(1) + (m.group(2) or "")).zfill(2)
    suffix = m.group(3) or "1"
    return f"PN{pid}-{suffix}.edf"


def parse_seizure_list(txt_path: str) -> list:
    """Parseia o arquivo Seizures-list-PNxx.txt e retorna uma lista de crises."""
    lines = Path(txt_path).read_text(encoding="utf-8", errors="replace").splitlines()
    seizures = []
    current = None
    ctx_edf, ctx_reg_start, ctx_reg_end = None, None, None

    for raw_line in lines:
        line = raw_line.strip()
        lower = line.lower()
        if not lower:
            continue

        if lower.startswith("file name:"):
            ctx_edf = _normalize_edf_name(line.split(":", 1)[1])
            if current is not None:
                current["edf_file"] = ctx_edf
        elif lower.startswith("registration start time:"):
            ctx_reg_start = _hms_to_seconds(line.split(":", 1)[1])
            if current is not None:
                current["reg_start_s"] = ctx_reg_start
        elif lower.startswith("registration end time:"):
            ctx_reg_end = _hms_to_seconds(line.split(":", 1)[1])
            if current is not None:
                current["reg_end_s"] = ctx_reg_end
        elif re.match(r"seizure\s+n\s*\d+", lower):
            if current is not None and "edf_file" in current:
                seizures.append(current)
            m = re.search(r"(\d+)", line)
            current = {"seizure_n": int(m.group(1)) if m else len(seizures) + 1}
            if ctx_edf:
                current["edf_file"] = ctx_edf
            if ctx_reg_start is not None:
                current["reg_start_s"] = ctx_reg_start
            if ctx_reg_end is not None:
                current["reg_end_s"] = ctx_reg_end
        elif lower.startswith(("seizure start time:", "start time:")):
            if current is not None:
                current["sz_start_s"] = _hms_to_seconds(line.split(":", 1)[1])
        elif lower.startswith(("seizure end time:", "end time:")):
            if current is not None:
                current["sz_end_s"] = _hms_to_seconds(line.split(":", 1)[1])

    if current and "edf_file" in current:
        seizures.append(current)

    for sz in seizures:
        rs = sz.get("reg_start_s", 0.0)
        re_ = sz.get("reg_end_s", 0.0)
        ss = sz.get("sz_start_s", 0.0)
        se = sz.get("sz_end_s", 0.0)

        if re_ < rs:
            re_ += 86400.0
        if ss < rs:
            ss += 86400.0
        if se < ss:
            se += 86400.0

        sz["reg_duration_s"] = re_ - rs
        sz["sz_start_rel_s"] = ss - rs
        sz["sz_end_rel_s"] = se - rs
        sz["sz_duration_s"] = se - ss

    return seizures
