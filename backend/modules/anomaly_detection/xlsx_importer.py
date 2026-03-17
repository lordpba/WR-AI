from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


@dataclass(frozen=True)
class ImportSummary:
    rows_total: int
    rows_imported: int
    timestamp_min: Optional[float]
    timestamp_max: Optional[float]
    detected_columns: Dict[str, str]


def _normalize_col(col: Any) -> str:
    return str(col).strip().lower()


def _first_present(mapping: Dict[str, List[str]], normalized_cols: Dict[str, str]) -> Tuple[Optional[str], Dict[str, str]]:
    """
    Returns:
      - first_key: the first mapping key that matched any candidate column (or None)
      - detected: dict of mapping key -> original dataframe column name
    """
    detected: Dict[str, str] = {}
    first_key: Optional[str] = None
    for key, candidates in mapping.items():
        found = None
        for c in candidates:
            if c in normalized_cols:
                found = normalized_cols[c]
                break
        if found:
            detected[key] = found
            if first_key is None:
                first_key = key
    return first_key, detected


def _to_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        if isinstance(val, str):
            v = val.strip().replace(",", ".")
            if v == "":
                return None
            return float(v)
        return float(val)
    except Exception:
        return None


def _build_timestamp(df: pd.DataFrame, date_col: str, time_col: str) -> pd.Series:
    date_series = df[date_col]
    time_series = df[time_col]

    dt = pd.to_datetime(date_series, errors="coerce")
    t = pd.to_datetime(time_series, errors="coerce").dt.time
    combined = pd.to_datetime(
        dt.dt.date.astype(str) + " " + t.astype(str),
        errors="coerce",
    )

    if combined.isna().all():
        combined = pd.to_datetime(date_series.astype(str) + " " + time_series.astype(str), errors="coerce")

    return combined


def import_termoformatrice_xlsx(
    file_path: str,
    max_rows: int = 200_000,
    electrical_mode: str = "three_phase",
) -> Tuple[List[Dict[str, Any]], ImportSummary]:
    df = pd.read_excel(file_path)
    rows_total = int(len(df))
    if rows_total == 0:
        return [], ImportSummary(0, 0, None, None, {})

    if rows_total > max_rows:
        df = df.iloc[-max_rows:].copy()

    normalized_cols = {_normalize_col(c): c for c in df.columns}

    col_map = {
        "date": ["data", "date", "giorno"],
        "time": ["ora", "time"],
        "energy_total_kwh": ["energia consumata totale (kwh)", "energia consumata totale", "energia totale (kwh)", "energia totale"],
        "energy_grid_kwh": ["energia prelevata dalla rete (kwh)", "energia prelevata dalla rete"],
        "energy_self_kwh": ["energia autoconsumata (kwh)", "energia autoconsumata"],
        "reactive_varh": ["energia reattiva (varh)", "energia reattiva"],
        "power_factor": ["fattore di potenza (units)", "fattore di potenza", "cosφ", "cosfi", "cosphi"],
        "voltage_v": ["tensione (v)", "tensione", "voltage (v)", "voltage"],
        "current_a": ["corrente (a)", "corrente", "current (a)", "current"],
        "power_kw": ["potenza (kw)", "power (kw)", "power_kw", "power"],
    }

    _, detected = _first_present(col_map, normalized_cols)

    if "date" not in detected or "time" not in detected:
        raise ValueError("Missing required columns: Data/Ora (date/time).")

    ts = _build_timestamp(df, detected["date"], detected["time"])
    df = df.assign(_timestamp=ts)
    df = df.dropna(subset=["_timestamp"]).copy()
    if df.empty:
        return [], ImportSummary(rows_total, 0, None, None, detected)

    df["_timestamp_epoch"] = (df["_timestamp"].astype("int64") / 1e9).astype(float)
    df = df.sort_values("_timestamp_epoch", ascending=True)

    mode = electrical_mode
    if mode not in ("single_phase", "three_phase"):
        mode = "three_phase"

    out: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        timestamp = _to_float(row["_timestamp_epoch"])
        if timestamp is None:
            continue

        voltage_v = _to_float(row.get(detected.get("voltage_v"))) if detected.get("voltage_v") else None
        current_a = _to_float(row.get(detected.get("current_a"))) if detected.get("current_a") else None
        power_factor = _to_float(row.get(detected.get("power_factor"))) if detected.get("power_factor") else None

        power_kw = _to_float(row.get(detected.get("power_kw"))) if detected.get("power_kw") else None
        if power_kw is None and voltage_v is not None and current_a is not None and power_factor is not None:
            scale = math.sqrt(3.0) if mode == "three_phase" else 1.0
            power_kw = (scale * voltage_v * current_a * power_factor) / 1000.0

        record: Dict[str, Any] = {
            "timestamp": timestamp,
            "voltage_v": voltage_v,
            "current_a": current_a,
            "power_factor": power_factor,
            "power_kw": power_kw,
            "power": power_kw,  # compatibility with existing dashboards/baseline
            "energy_total_kwh": _to_float(row.get(detected.get("energy_total_kwh"))) if detected.get("energy_total_kwh") else None,
            "energy_grid_kwh": _to_float(row.get(detected.get("energy_grid_kwh"))) if detected.get("energy_grid_kwh") else None,
            "energy_self_kwh": _to_float(row.get(detected.get("energy_self_kwh"))) if detected.get("energy_self_kwh") else None,
            "reactive_varh": _to_float(row.get(detected.get("reactive_varh"))) if detected.get("reactive_varh") else None,
        }

        out.append(record)

    ts_min = float(out[0]["timestamp"]) if out else None
    ts_max = float(out[-1]["timestamp"]) if out else None
    return out, ImportSummary(rows_total=rows_total, rows_imported=len(out), timestamp_min=ts_min, timestamp_max=ts_max, detected_columns=detected)

