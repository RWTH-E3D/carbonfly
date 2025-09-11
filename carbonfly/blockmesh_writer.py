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

# carbonfly/blockmesh_writer.py
from math import ceil
from pathlib import Path
from typing import Optional, Tuple

from .utils import foam_header

def _cells_from_size(Lx: float, Ly: float, Lz: float, cell_size: float) -> Tuple[int,int,int]:
    """Compute (nx,ny,nz) from target cell size (meters)."""
    if cell_size <= 0:
        raise ValueError("cell_size must be > 0.")
    nx = max(1, int(ceil(Lx / cell_size)))
    ny = max(1, int(ceil(Ly / cell_size)))
    nz = max(1, int(ceil(Lz / cell_size)))
    return nx, ny, nz

def write_blockmesh_dict(
    case_root: Path,
    *,
    min_xyz: Tuple[float,float,float],
    max_xyz: Tuple[float,float,float],
    cells: Optional[Tuple[int,int,int]] = None,
    cell_size: Optional[float] = None,
    grading: Tuple[float,float,float] = (1.0, 1.0, 1.0),
    convert_to_meters: float = 1.0,
) -> Path:
    """
    Write a minimal system/blockMeshDict with a single hex block.

    Args:
        min_xyz/max_xyz: domain bounds in meters (since STL is already scaled to meters).
        cells:           (nx,ny,nz). If None and cell_size provided, cells will be computed.
        cell_size:       target cell size (m). Used only when cells is None.
        grading:         simpleGrading (gx,gy,gz).
        convert_to_meters: OpenFOAM convertToMeters (default 1.0).

    Returns:
        Path to system/blockMeshDict.
    """
    (xmin, ymin, zmin) = min_xyz
    (xmax, ymax, zmax) = max_xyz
    Lx, Ly, Lz = (xmax - xmin, ymax - ymin, zmax - zmin)
    if Lx <= 0 or Ly <= 0 or Lz <= 0:
        raise ValueError("Block dimensions must be positive (check bounds).")

    if cells is None:
        if cell_size is None:
            # fallback: ~20 cells per shortest edge
            s = max(min(Lx, Ly, Lz) / 20.0, 1e-3)
            cells = _cells_from_size(Lx, Ly, Lz, s)
        else:
            cells = _cells_from_size(Lx, Ly, Lz, cell_size)
    nx, ny, nz = map(int, cells)

    gx, gy, gz = grading

    # OpenFOAM vertex order for a hex (0..7)
    # bottom: 0(xmin,ymin,zmin) 1(xmax,ymin,zmin) 2(xmax,ymax,zmin) 3(xmin,ymax,zmin)
    # top:    4(xmin,ymin,zmax) 5(xmax,ymin,zmax) 6(xmax,ymax,zmax) 7(xmin,ymax,zmax)
    V = [
        (xmin, ymin, zmin),
        (xmax, ymin, zmin),
        (xmax, ymax, zmin),
        (xmin, ymax, zmin),
        (xmin, ymin, zmax),
        (xmax, ymin, zmax),
        (xmax, ymax, zmax),
        (xmin, ymax, zmax),
    ]

    lines = []
    lines.append(foam_header("blockMeshDict", location="system"))
    lines.append(f"convertToMeters {convert_to_meters};\n")

    # vertices
    lines.append("vertices")
    lines.append("(")
    for (x,y,z) in V:
        lines.append(f"    ({x:.6g} {y:.6g} {z:.6g})")
    lines.append(");\n")

    # single block
    lines.append("blocks")
    lines.append("(")
    lines.append(f"    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading ({gx} {gy} {gz})")
    lines.append(");\n")

    # edges (none)
    lines.append("edges")
    lines.append("(")
    lines.append(");\n")

    # boundary patches
    lines.append("boundary")
    lines.append("(")
    lines.append("    boundingbox")
    lines.append("    {")
    lines.append("        type wall;")
    lines.append("        faces")
    lines.append("        (")
    lines.append("            (0 3 2 1)")
    lines.append("            (4 5 6 7)")
    lines.append("            (1 2 6 5)")
    lines.append("            (3 0 4 7)")
    lines.append("            (0 1 5 4)")
    lines.append("            (2 3 7 6)")
    lines.append("        );")
    lines.append("    }")
    lines.append(");\n")

    # mergePatchPairs (empty)
    lines.append("mergePatchPairs")
    lines.append("(")
    lines.append(");\n")

    out = case_root / "system" / "blockMeshDict"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    return out
