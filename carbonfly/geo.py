from __future__ import annotations
"""
carbonfly
    a lightweight, easy-to-use Python API and 
    toolbox for indoor CO2 CFD simulations in Grasshopper
    based on OpenFOAM and WSL

- Author: Qirui Huang
- License: LGPL-3.0
- Website: https://github.com/RWTH-E3D/carbonfly
"""

# carbonfly/geo.py
from dataclasses import dataclass
from typing import Any, Optional
import Rhino

from .boundary import Boundary


# Data models
@dataclass
class Refine:
    """Surface refinement levels for snappyHexMesh: (min, max)."""
    min_level: int = 0
    max_level: int = 0


@dataclass
class CFGeo:
    """
    A single CFD surface entity:
      - name: region/solid name to be written into STL (and used in snappy regions{})
      - brep: normalized Brep geometry (created from Surface/BrepFace/Brep)
      - boundary: physical boundary description (Boundary), region_name will be bound to name
      - refine: surface refinement levels (min,max)
    """
    name: str
    brep: Rhino.Geometry.Brep
    boundary: Boundary
    refine: Refine


# Helpers
def _to_brep(obj) -> Optional[Rhino.Geometry.Brep]:
    """Normalize input geometry to a Rhino Brep."""
    if obj is None:
        return None
    if isinstance(obj, Rhino.Geometry.Brep):
        return obj
    if isinstance(obj, Rhino.Geometry.BrepFace):
        # Duplicate trimmed face as a Brep
        return obj.DuplicateFace(True)
    if isinstance(obj, Rhino.Geometry.Surface):
        return Rhino.Geometry.Brep.CreateFromSurface(obj)

    return None


def _norm_refine(refine: Any) -> Refine:
    """
    Normalize refine input to Refine(min,max).
    Supported forms:
      - int     -> (i, i)
      - (min, max) / [min, max]
      - dict {"min":3,"max":5}  -> (3,5)
      - dict {"levels":(3,5)}   -> (3,5)
      - Rhino.Geometry.Interval -> (int(T0), int(T1))
      - None    -> (0,0)
    """
    # int -> (i,i)
    if isinstance(refine, int):
        i = int(refine)
        return Refine(i, i)

    # tuple/list -> (min,max)
    if isinstance(refine, (tuple, list)) and len(refine) == 2:
        mn, mx = int(refine[0]), int(refine[1])
        if mn > mx:
            mn, mx = mx, mn
        return Refine(mn, mx)

    # dict
    if isinstance(refine, dict):
        if "levels" in refine and isinstance(refine["levels"], (tuple, list)) and len(refine["levels"]) == 2:
            mn, mx = int(refine["levels"][0]), int(refine["levels"][1])
            if mn > mx:
                mn, mx = mx, mn
            return Refine(mn, mx)
        if "min" in refine or "max" in refine:
            mn = int(refine.get("min", 0))
            mx = int(refine.get("max", mn))
            if mn > mx:
                mn, mx = mx, mn
            return Refine(mn, mx)

    # Rhino Interval
    if isinstance(refine, Rhino.Geometry.Interval):
        mn, mx = int(refine.T0), int(refine.T1)
        if mn > mx:
            mn, mx = mx, mn
        return Refine(mn, mx)

    # Default
    return Refine(0, 0)

def make_cfgeo(name: str, geometry, boundary: Boundary, refine_levels: Any = None) -> CFGeo:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    if boundary is None:
        raise ValueError("boundary is required")
    br = _to_brep(geometry)
    if br is None:
        raise ValueError("geometry must be a Rhino Surface/BrepFace/Brep")
    rf = _norm_refine(refine_levels)
    # bind region name for later use
    boundary.region_name = name.strip()

    return CFGeo(name=name.strip(), brep=br, boundary=boundary, refine=rf)
