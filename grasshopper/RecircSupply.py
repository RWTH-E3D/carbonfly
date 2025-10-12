# GH inputs: velocity (Rhino.Geometry.Vector3d), temperature (float), return_name (str)
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
    if return_name is None:
        raise ValueError("return_name is required.")

    fields = {
        "U":        cfbc.FieldFV(vec3_to_tuple(velocity)),
        "T":        cfbc.FieldFV(float(temperature)),
        "CO2":      cfbc.FieldCO2FromPatchAverage(source_patch=return_name),
        "air":      cfbc.FieldCalculated("$internalField"),
        "p":        cfbc.FieldTotalPressure(p0="$internalField",value="$internalField"),
        "p_rgh":    cfbc.FieldFixedFluxPressure("$internalField"),
        "alphat":   cfbc.FieldInletOutlet(inletValue="$internalField",value="$internalField"),
        "epsilon":  cfbc.FieldMixingLengthEpsilonInlet(value="$internalField", mixingLength=0.0168),
        "G":        cfbc.FieldZG(),
        "k":        cfbc.FieldIntensityKInlet(intensity=0.14, value="$internalField"),
        "nut":      cfbc.FieldCalculated("$internalField"),
        "Ydefault": cfbc.FieldFV("$internalField"),
    }

    boundary = cfbc.Boundary(
        region_name="",
        btype="recircSupply",
        fields=fields
    )

except Exception as e:
    boundary = None
