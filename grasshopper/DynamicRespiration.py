# GH inputs: freq (float), breathing_flow_rate(float), temperature (float), CO2 (float)
# GH outputs: boundary
from math import isfinite
import carbonfly.boundary as cfbc

try:
    # check input
    if not isfinite(freq):
        raise ValueError("freq must be a finite number.")
    if not isfinite(breathing_flow_rate):
        raise ValueError("breathing_flow_rate must be a finite number.")
    if not isfinite(temperature):
        raise ValueError("Temperature (T) must be a finite number.")
    if not isfinite(CO2):
        raise ValueError("CO2 must be a finite number (fraction).")

    fields = {
        "U":        cfbc.FieldDynamicRespiration(
                        freq=freq or None,
                        minute_vent_L_min=breathing_flow_rate or None
                    ),
        "T":        cfbc.FieldInletOutlet(
                        inletValue=float(temperature),
                        value="$internalField"
                    ),
        "CO2":      cfbc.FieldInletOutlet(
                        inletValue=float(CO2),
                        value="$internalField"
                    ),
        "air":      cfbc.FieldInletOutlet(
                        inletValue=1-float(CO2),
                        value="$internalField"
                    ),
        "p":        cfbc.FieldFV("$internalField"),
        "p_rgh":    cfbc.FieldFixedFluxPressure("$internalField"),
        "alphat":   cfbc.FieldCalculated("$internalField"),
        "epsilon":  cfbc.FieldMixingLengthEpsilonInlet(value="$internalField", mixingLength=0.0168),
        "G":        cfbc.FieldMarshakRadiation(emissivity=0.98, value="$internalField"),
        "k":        cfbc.FieldIntensityKInlet(intensity=0.14, value="$internalField"),
        "nut":      cfbc.FieldCalculated("$internalField"),
        "Ydefault": cfbc.FieldFV("$internalField"),
    }

    boundary = cfbc.Boundary(
        region_name="",
        btype="DynamicRespiration",
        fields=fields
    )

except Exception as e:
    boundary = None
