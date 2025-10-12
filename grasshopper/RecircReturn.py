# GH inputs: velocity (Rhino.Geometry.Vector3d)
# GH outputs: boundary
import carbonfly.boundary as cfbc

def vec3_to_tuple(v):
    return (float(v.X), float(v.Y), float(v.Z))

try:
    # check input
    if velocity is None:
        raise ValueError("velocity is required.")

    fields = {
        "U":        cfbc.FieldFV(vec3_to_tuple(velocity)),
        "T":        cfbc.FieldZG(),
        "CO2":      cfbc.FieldZG(),
        "air":      cfbc.FieldCalculated("$internalField"),
        "p":        cfbc.FieldZG(),
        "p_rgh":    cfbc.FieldFixedFluxPressure("$internalField"),
        "alphat":   cfbc.FieldInletOutlet(inletValue="$internalField",value="$internalField"),
        "epsilon":  cfbc.FieldInletOutlet(inletValue="$internalField",value="$internalField"),
        "G":        cfbc.FieldZG(),
        "k":        cfbc.FieldInletOutlet(inletValue="$internalField",value="$internalField"),
        "nut":      cfbc.FieldCalculated("$internalField"),
        "Ydefault": cfbc.FieldFV("$internalField"),
    }

    boundary = cfbc.Boundary(
        region_name="",
        btype="recircReturn",
        fields=fields
    )

except Exception as e:
    boundary = None
