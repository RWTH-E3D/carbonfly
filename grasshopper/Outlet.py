# GH outputs:
#   boundary

import carbonfly.boundary as cfbc

try:
    fields = {
        "U":        cfbc.FieldZG(),
        "T":        cfbc.FieldZG(),
        "CO2":      cfbc.FieldZG(),
        "p":        cfbc.FieldZG(),
        "p_rgh":    cfbc.FieldFV("$internalField"),
        "alphat":   cfbc.FieldZG(),
        "epsilon":  cfbc.FieldZG(),
        "G":        cfbc.FieldZG(),
        "k":        cfbc.FieldZG(),
        "nut":      cfbc.FieldZG(),
        "Ydefault": cfbc.FieldFV("$internalField"),
    }

    boundary = cfbc.Boundary(
        region_name="",
        btype="zeroGradientOutlet",
        fields=fields
    )
except Exception as e:
    boundary = None
