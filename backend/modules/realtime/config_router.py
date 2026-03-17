import os
from fastapi import APIRouter, Body, HTTPException

from .config_store import get_config, set_config


router = APIRouter(prefix="/api/realtime", tags=["RealtimeConfig"])


@router.get("/config")
def read_config():
    cfg = get_config()
    # Defaults (env as fallback)
    cfg.setdefault("source_type", os.getenv("RT_SOURCE_TYPE", "none"))  # none|modbus_tcp|serial_raw
    cfg.setdefault("poll_interval_s", float(os.getenv("RT_POLL_INTERVAL_S", "1.0")))
    cfg.setdefault("modbus_host", os.getenv("MODBUS_HOST", ""))
    cfg.setdefault("modbus_port", int(os.getenv("MODBUS_PORT", "502")))
    cfg.setdefault("modbus_unit_id", int(os.getenv("MODBUS_UNIT_ID", "1")))
    cfg.setdefault("modbus_reg_map_json", os.getenv("MODBUS_REG_MAP_JSON", ""))
    return cfg


@router.post("/config")
def write_config(values: dict = Body(default={})):
    try:
        allowed = {}
        for k in (
            "source_type",
            "poll_interval_s",
            "modbus_host",
            "modbus_port",
            "modbus_unit_id",
            "modbus_reg_map_json",
        ):
            if k in values:
                allowed[k] = values[k]
        cfg = set_config(allowed)
        return {"status": "success", "config": cfg}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

