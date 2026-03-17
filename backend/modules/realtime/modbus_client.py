from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pymodbus.client import AsyncModbusTcpClient

logger = logging.getLogger(__name__)
from .config_store import get_config


@dataclass(frozen=True)
class RegisterSpec:
    name: str
    address: int
    count: int = 1
    scale: float = 1.0
    signed: bool = False


def _parse_reg_map(raw: str) -> List[RegisterSpec]:
    """
    Expect JSON like:
      [
        {"name":"voltage_v","address":0,"count":1,"scale":0.1},
        {"name":"current_a","address":1,"count":1,"scale":0.01}
      ]
    """
    if not raw:
        return []
    try:
        data = json.loads(raw)
        out: List[RegisterSpec] = []
        for item in data:
            out.append(
                RegisterSpec(
                    name=str(item["name"]),
                    address=int(item["address"]),
                    count=int(item.get("count", 1)),
                    scale=float(item.get("scale", 1.0)),
                    signed=bool(item.get("signed", False)),
                )
            )
        return out
    except Exception as e:
        raise ValueError(f"Invalid MODBUS_REG_MAP_JSON: {e}")


def _default_reg_map() -> List[RegisterSpec]:
    # Placeholder defaults (must be overridden in production)
    return [
        RegisterSpec(name="voltage_v", address=0, count=1, scale=0.1),
        RegisterSpec(name="current_a", address=1, count=1, scale=0.01),
        RegisterSpec(name="power_factor", address=2, count=1, scale=0.001),
        RegisterSpec(name="energy_total_kwh", address=10, count=2, scale=0.01),  # 32-bit at 10-11
    ]


def _decode_u16(reg: int) -> int:
    return int(reg) & 0xFFFF


def _decode_s16(reg: int) -> int:
    v = int(reg) & 0xFFFF
    return v - 0x10000 if v & 0x8000 else v


def _decode_u32(regs: List[int]) -> int:
    hi = _decode_u16(regs[0])
    lo = _decode_u16(regs[1])
    return (hi << 16) | lo


def _decode_s32(regs: List[int]) -> int:
    v = _decode_u32(regs)
    return v - 0x100000000 if v & 0x80000000 else v


class ModbusTCPSource:
    def __init__(self):
        self.host = os.getenv("MODBUS_HOST", "").strip()
        self.port = int(os.getenv("MODBUS_PORT", "502"))
        self.unit_id = int(os.getenv("MODBUS_UNIT_ID", "1"))
        self.timeout_s = float(os.getenv("MODBUS_TIMEOUT_S", "2.0"))
        self._client: Optional[AsyncModbusTcpClient] = None
        self._connected: bool = False

        raw_map = os.getenv("MODBUS_REG_MAP_JSON", "").strip()
        self.reg_map = _parse_reg_map(raw_map) if raw_map else _default_reg_map()

    def _refresh_from_config(self):
        try:
            cfg = get_config()
        except Exception:
            cfg = {}

        host = str(cfg.get("modbus_host") or self.host or "").strip()
        port = int(cfg.get("modbus_port") or self.port or 502)
        unit_id = int(cfg.get("modbus_unit_id") or self.unit_id or 1)
        raw_map = str(cfg.get("modbus_reg_map_json") or "").strip()
        reg_map = _parse_reg_map(raw_map) if raw_map else self.reg_map

        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.reg_map = reg_map

    @property
    def is_configured(self) -> bool:
        return bool(self.host)

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        self._refresh_from_config()
        if not self.is_configured:
            self._connected = False
            return False

        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass

        self._client = AsyncModbusTcpClient(self.host, port=self.port, timeout=self.timeout_s)
        try:
            await self._client.connect()
            self._connected = bool(self._client.connected)
            if self._connected:
                logger.info(f"✅ Modbus TCP connected to {self.host}:{self.port} unit={self.unit_id}")
            else:
                logger.warning(f"❌ Modbus TCP not connected to {self.host}:{self.port}")
            return self._connected
        except Exception as e:
            self._connected = False
            logger.error(f"Modbus connect error: {e}")
            return False

    async def disconnect(self):
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass
        self._client = None
        self._connected = False

    async def read_point(self) -> Dict[str, Any]:
        """
        Returns dict with signals. Raises on unrecoverable errors.
        """
        if not self._client or not self._client.connected:
            ok = await self.connect()
            if not ok:
                raise ConnectionError("Modbus TCP not connected")

        assert self._client is not None

        out: Dict[str, Any] = {}
        for spec in self.reg_map:
            rr = await self._client.read_holding_registers(address=spec.address, count=spec.count, slave=self.unit_id)
            if rr.isError():
                raise RuntimeError(f"Modbus read error at {spec.address} (count={spec.count})")
            regs = list(getattr(rr, "registers", []) or [])
            if len(regs) < spec.count:
                raise RuntimeError(
                    f"Modbus short read at {spec.address}: expected {spec.count} registers, got {len(regs)}"
                )
            if spec.count == 1:
                raw_val = _decode_s16(regs[0]) if spec.signed else _decode_u16(regs[0])
            elif spec.count == 2:
                raw_val = _decode_s32(regs) if spec.signed else _decode_u32(regs)
            else:
                # For larger blocks, just return the raw list
                raw_val = regs

            if isinstance(raw_val, (int, float)):
                out[spec.name] = float(raw_val) * float(spec.scale)
            else:
                out[spec.name] = raw_val

        return out


modbus_source = ModbusTCPSource()

