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

# carbonfly/constant_writer.py
from pathlib import Path

def write_constant_files(case_root: Path):
    """
    Copy the standard constant/ dicts
    """
    const_dir = case_root / "constant"
    const_dir.mkdir(parents=True, exist_ok=True)

    resources = {
        "fvModels": "templates/constant/fvModels",
        "g": "templates/constant/g",
        "momentumTransport": "templates/constant/momentumTransport",
        "physicalProperties": "templates/constant/physicalProperties",
        "pRef": "templates/constant/pRef",
        "radiationProperties": "templates/constant/radiationProperties",
        "combustionProperties": "templates/constant/combustionProperties",
    }

    for name, rel_path in resources.items():
        src = Path(__file__).parent / rel_path
        dst = const_dir / name
        if not dst.exists():
            dst.write_text(src.read_text())

def write_residuals_file(case_root: Path):
    """
    Copy the standard system/residuals
    """
    sys_dir = case_root / "system"
    sys_dir.mkdir(parents=True, exist_ok=True)

    src = Path(__file__).parent / "templates" / "residuals" / "residuals"
    dst = sys_dir / "residuals"

    if not src.exists():
        raise FileNotFoundError(f"Residuals template not found: {src}")

    if not dst.exists():
        dst.write_text(src.read_text())