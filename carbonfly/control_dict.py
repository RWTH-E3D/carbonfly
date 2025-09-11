from __future__ import annotations
"""
carbonfly
    a lightweight, easy-to-use Python API and 
    toolbox for indoor CO2 CFD simulations in Grasshopper
    based on OpenFOAM and WSL

- Author: Qirui Huang
- License: AGPL-3.0
- Website: https://github.com/RWTH-E3D/carbonfly
"""

# carbonfly/control_dict.py
from pathlib import Path
from typing import Dict, Any, Optional
import json

from .utils import foam_header

# Defaults
STEADY_DEFAULT: Dict[str, Any] = {
    "application": "buoyantReactingFoam",
    "startFrom": "latestTime",
    "startTime": 0,
    "stopAt": "endTime",
    "endTime": 1000,        # 1000 iterations
    "deltaT": 1,
    "writeControl": "timeStep",
    "writeInterval": 100,   # 100 iterations
    "purgeWrite": 0,
    "writeFormat": "ascii",
    "writePrecision": 8,
    "writeCompression": "off",
    "timeFormat": "general",
    "timePrecision": 6,
    "runTimeModifiable": True,
    "functions": {
        "residuals": {"include": "#includeFunc residuals"}
    }
}

TRANSIENT_DEFAULT: Dict[str, Any] = {
    "application": "buoyantReactingFoam",
    "startFrom": "latestTime",
    "startTime": 0,
    "stopAt": "endTime",
    "endTime": 120,         # 120s = 2min
    "deltaT": 0.01,
    "writeControl": "runTime",
    "writeInterval": 10,    # 10s
    "purgeWrite": 0,
    "writeFormat": "ascii",
    "writePrecision": 8,
    "writeCompression": "off",
    "timeFormat": "general",
    "timePrecision": 6,
    "runTimeModifiable": True,
    "adjustTimeStep": "yes",    # yes/no
    "maxCo": 1,
    "maxDeltaT": 0.2,
    "functions": {
        "residuals": {"include": "#includeFunc residuals"},
        "CoNum": {
            "type": "CourantNo",
            "libs": "(\"libfieldFunctionObjects.so\")",
            "writeControl": "runTime",
            "writeInterval": 10
        }
    }
}

# Helpers
def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shallow merge dict b into a (a is copied). For nested 'functions', merge per key.
    """
    out = dict(a)
    for k, v in (b or {}).items():
        if k == "functions" and isinstance(v, dict) and isinstance(out.get("functions"), dict):
            f = dict(out["functions"])
            f.update(v)
            out["functions"] = f
        else:
            out[k] = v
    return out

def _fmt_bool_or_token(key: str, val: Any) -> str:
    """
    Format booleans/tokens per OpenFOAM style:
      - adjustTimeStep uses yes/no when value is bool-like
      - runTimeModifiable uses true/false
      - other tokens usually raw (no quotes)
    """
    if key == "adjustTimeStep":
        if isinstance(val, bool):
            return "yes" if val else "no"
        if isinstance(val, str):
            return val
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)

def _render_kv(lines, key: str, val: Any):
    lines.append(f"{key}\t\t{_fmt_bool_or_token(key, val)};")

def _render_functions_block(lines, funcs: Dict[str, Any]):
    if not funcs:
        return
    lines.append("")
    lines.append("functions")
    lines.append("{")
    # support:
    # 1) {"name": {"include": "#includeFunc residuals"}}
    # 2) {"CoNum": {"type":"CourantNo", "libs":"(...)", "writeControl":"runTime", "writeInterval":10}}
    for name, spec in funcs.items():
        if isinstance(spec, dict) and "include" in spec:
            lines.append(f"  {spec['include']}")
            continue
        lines.append(f"  {name}")
        lines.append("  {")
        if isinstance(spec, dict):
            for k, v in spec.items():
                if k == "include":
                    lines.append(f"    {v}")
                else:
                    lines.append(f"    {k}\t\t{_fmt_bool_or_token(k, v)};")
        lines.append("  }")
    lines.append("}")

# API
def make_default(mode: str = "transient", application: Optional[str] = None) -> Dict[str, Any]:
    """
    Return a default controlDict config dict for 'steady' or 'transient'.
    """
    mode = (mode or "transient").strip().lower()
    base = TRANSIENT_DEFAULT if mode in ("transient", "unsteady") else STEADY_DEFAULT
    cfg = dict(base)
    if application:
        cfg["application"] = application
    return cfg

def write_control_dict_from_json(case_root: Path, cfg_json: str) -> Path:
    """
    Parse a JSON string to dict and write system/controlDict.
    """
    cfg = json.loads(cfg_json) if cfg_json else {}
    if not isinstance(cfg, dict):
        raise ValueError("controlDict JSON must be a JSON object.")
    return write_control_dict(case_root, cfg)

def write_control_dict(case_root: Path, cfg: Dict[str, Any]) -> Path:
    """
    Write 'system/controlDict' using a config dict.
    """
    case_root = Path(case_root)
    out = case_root / "system" / "controlDict"
    out.parent.mkdir(parents=True, exist_ok=True)

    # header
    lines = [foam_header("controlDict", location="system")]

    # scalar/token entries
    ordered_keys = [
        "application",
        "startFrom", "startTime",
        "stopAt", "endTime",
        "deltaT",
        "writeControl", "writeInterval",
        "purgeWrite",
        "writeFormat", "writePrecision", "writeCompression",
        "timeFormat", "timePrecision",
        "runTimeModifiable",
        "adjustTimeStep", "maxCo", "maxDeltaT"
    ]
    for k in ordered_keys:
        if k in cfg:
            _render_kv(lines, k, cfg[k])

    # functions
    funcs = cfg.get("functions")
    _render_functions_block(lines, funcs if isinstance(funcs, dict) else {})

    # write
    text = "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8")
    return out
