# GH inputs:
#   temperature (Number)  # K
# GH outputs:
#   boundary

from math import isfinite
import carbonfly.boundary as cfbc

try:
    # check T input
    T = float(temperature)
    if not isfinite(T):
        raise ValueError("Temperature (T) must be a finite number (K).")

    fields = {
        "U":        cfbc.FieldNoSlip(),
        "T":        cfbc.FieldFV(T),
        "CO2":      cfbc.FieldZG(),
        "p":        cfbc.FieldZG(),
        "p_rgh":    cfbc.FieldFixedFluxPressure("$internalField"),
        "alphat":   cfbc.FieldAlphatJayatillekeWF(value="$internalField", Prt=0.85),
        "epsilon":  cfbc.FieldEpsilonWallFunction("$internalField"),
        "G":        cfbc.FieldMarshakRadiation(emissivity=0.98, value="$internalField"),
        "k":        cfbc.FieldKqRWallFunction("$internalField"),
        "nut":      cfbc.FieldNutkWallFunction("$internalField"),
        "Ydefault": cfbc.FieldFV("$internalField"),
    }

    boundary = cfbc.Boundary(
        region_name="",
        btype="wall",
        fields=fields
    )

except Exception as e:
    boundary = None
