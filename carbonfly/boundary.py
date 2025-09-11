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

# carbonfly/boundary.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Literal, Tuple

Vec3 = Tuple[float, float, float]

# Minimal representations of common field specifications
@dataclass
class FieldFV:
    """Fixed value boundary condition (fixedValue)."""
    value: Any  # scalar or vector (tuple)
    def to_dict(self):
        return {"type": "fixedValue", "value": self.value}

@dataclass
class FieldZG:
    """Zero gradient boundary condition (zeroGradient)."""
    def to_dict(self):
        return {"type": "zeroGradient"}

@dataclass
class FieldNoSlip:
    """No-slip boundary condition for velocity U (vector): U = 0."""
    def to_dict(self):
        return {"type": "noSlip"}

@dataclass
class FieldInletOutlet:
    """inletOutlet boundary condition."""
    inletValue: Any
    value: Any
    def to_dict(self):
        return {"type": "inletOutlet", "inletValue": self.inletValue, "value": self.value}

@dataclass
class FieldCalculated:
    """calculated"""
    value: Any
    def to_dict(self):
        return {"type": "calculated", "value": self.value}

@dataclass
class FieldAlphatJayatillekeWF:
    """compressible::alphatJayatillekeWallFunction"""
    value: Any
    Prt: float = 0.85
    def to_dict(self):
        return {"type": "compressible::alphatJayatillekeWallFunction", "value": self.value, "Prt": self.Prt}

@dataclass
class FieldEpsilonWallFunction:
    value: Any
    def to_dict(self):
        return {"type": "epsilonWallFunction", "value": self.value}

@dataclass
class FieldKqRWallFunction:
    value: Any
    def to_dict(self):
        return {"type": "kqRWallFunction", "value": self.value}

@dataclass
class FieldNutkWallFunction:
    value: Any
    def to_dict(self):
        return {"type": "nutkWallFunction", "value": self.value}

@dataclass
class FieldMixingLengthEpsilonInlet:
    """turbulentMixingLengthDissipationRateInlet"""
    value: Any
    mixingLength: Any = 0.0168
    def to_dict(self):
        return {"type": "turbulentMixingLengthDissipationRateInlet", "value": self.value, "mixingLength": self.mixingLength}

@dataclass
class FieldIntensityKInlet:
    """turbulentIntensityKineticEnergyInlet"""
    intensity: Any = 0.14
    value: Any = 0.0
    def to_dict(self):
        return {"type": "turbulentIntensityKineticEnergyInlet", "intensity": self.intensity, "value": self.value}

@dataclass
class FieldMarshakRadiation:
    emissivityMode: str = "lookup"   # or 'solidThermo'
    emissivity: Any = 0.98
    value: Any = 0.0
    def to_dict(self):
        return {"type": "MarshakRadiation", "emissivityMode": self.emissivityMode, "emissivity": self.emissivity, "value": self.value}

@dataclass
class FieldTotalPressure:
    p0: Any = "$internalField"
    value: Any = "$internalField"
    def to_dict(self):
        return {"type": "totalPressure", "p0": self.p0, "value": self.value}

@dataclass
class FieldFixedFluxPressure:
    value: Optional[Any] = None
    def to_dict(self):
        d = {"type": "fixedFluxPressure"}
        if self.value is not None:
            d["value"] = self.value
        return d

@dataclass
class FieldPressureInletOutletVelocity:
    inletValue: Any
    value: Any
    def to_dict(self):
        return {"type": "pressureInletOutletVelocity", "inletValue": self.inletValue, "value": self.value}

@dataclass
class FieldExternalWallHeatFluxTemperature:
    mode: str = "coefficient"
    h: Any = 0.0
    Ta: Any = 300.0
    value: Any = 300.0
    def to_dict(self):
        return {"type": "externalWallHeatFluxTemperature", "mode": self.mode, "h": self.h, "Ta": self.Ta, "value": self.value}

BoundaryType = Literal["inletVelocity", "outletPressure", "wall", "symmetry", "custom"]

@dataclass
class Boundary:
    region_name: str                   # e.g. "inlet_01" (from STL solid name)
    patch_name: Optional[str] = None   # Final patch name in OpenFOAM (defaults to region_name if None)
    btype: BoundaryType = "inletVelocity"
    # Field specifications as needed: U (velocity), T (temperature), CO2 (fraction)
    fields: Dict[str, Any] = field(default_factory=dict)

    def resolved_patch(self) -> str:
        """Return the effective patch name to be written in OpenFOAM (patch_name if set, else region_name)."""
        return self.patch_name or self.region_name

    def boundary_field_block(self) -> Dict[str, Dict]:
        """
        Generate the dictionary snippet for this boundary to be written into the 0/ field files.
        Each entry in `fields` should be an instance of FieldFV, FieldZG, FieldInletOutlet, etc.
        """
        out: Dict[str, Dict] = {}
        for fld, spec in self.fields.items():
            out[fld] = spec.to_dict()

        return out
