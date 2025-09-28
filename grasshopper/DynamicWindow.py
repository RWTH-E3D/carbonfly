# GH inputs: velocity (Rhino.Geometry.Vector3d), temperature (float), CO2 (float)
# GH outputs: boundary
from math import isfinite
import carbonfly.boundary as cfbc

def vec3_to_tuple(v):
    return (float(v.X), float(v.Y), float(v.Z))

try:
    # check input
    if velocity is None:
        raise ValueError("velocity is required.")
    if not isfinite(temperature):
        raise ValueError("Temperature (T) must be a finite number.")
    if not isfinite(CO2):
        raise ValueError("CO2 must be a finite number (fraction).")
    if not isfinite(pressure):
        raise ValueError("Pressure (p) must be a finite number.")

    fields = {
        "U":        cfbc.FieldPressureInletOutletVelocity(
                        inletValue=vec3_to_tuple(velocity), value=vec3_to_tuple(velocity)
                    ),
        "T":        cfbc.FieldInletOutlet(
                        inletValue=float(temperature), value=float(temperature)
                    ),
        "CO2":      cfbc.FieldInletOutlet(
                        inletValue=float(CO2), value=float(CO2)
                    ),
        "air":      cfbc.FieldInletOutlet(
                        inletValue=1-float(CO2), value=1-float(CO2)
                    ),
        "p":        cfbc.FieldTotalPressure(p0=float(pressure), value=float(pressure)),
        "p_rgh":    cfbc.FieldFixedFluxPressure("$internalField"),
        "alphat":   cfbc.FieldInletOutlet(inletValue="$internalField", value="$internalField"),
        "epsilon":  cfbc.FieldMixingLengthEpsilonInlet(value="$internalField", mixingLength=0.0168),
        "G":        cfbc.FieldMarshakRadiation(emissivity=0.98, value="$internalField"),
        "k":        cfbc.FieldIntensityKInlet(intensity=0.14, value="$internalField"),
        "nut":      cfbc.FieldCalculated("$internalField"),
        "Ydefault": cfbc.FieldFV("$internalField"),
    }

    boundary = cfbc.Boundary(
        region_name="",
        btype="pressureInletOutletVelocity",
        fields=fields
    )

except Exception as e:
    boundary = None
