# GH inputs:
#   U_internal (Vector)    # optional, m/s
#   T_internal (Number)    # optional, K
#   CO2_internal (Number)  # optional, volume fraction (e.g. 0.00045)
#   p_internal (Number)    # optional, Pa
# GH outputs:
#   log
#   internalFields

from math import isfinite
import json

def _vec3_or_none(v):
    if v is None:
        return None
    try:
        return (float(v.X), float(v.Y), float(v.Z))
    except Exception:
        raise ValueError("U_internal must be a Rhino Vector (X,Y,Z).")

def _finite_or_none(x, label):
    if x is None:
        return None
    try:
        val = float(x)
    except Exception:
        raise ValueError("{} must be a number.".format(label))
    if not isfinite(val):
        raise ValueError("{} must be finite.".format(label))
    return val

logs = []
try:
    Ui = _vec3_or_none(U_internal)
    Ti = _finite_or_none(T_internal, "T_internal")
    Ci = _finite_or_none(CO2_internal, "CO2_internal")
    Pi = _finite_or_none(p_internal, "p_internal")

    internalFields = {
        "U":        Ui,
        "T":        Ti,
        "CO2":      Ci,
        "p":        Pi,
        "p_rgh":    0,
        "alphat":   0,
        "epsilon":  0.01,
        "G":        0,
        "k":        0.1,
        "nut":      0,
        "Ydefault": 0,
    }
    internalFields = json.dumps(internalFields)

    # Brief log
    logs.append("[internalFields] packaged:")
    logs.append("  U:   {} m/s".format(Ui if Ui is not None else "None"))
    logs.append("  T:   {} K".format(Ti if Ti is not None else "None"))
    logs.append("  CO2: {} ppm".format(Ci*1e6 if Ci is not None else "None"))
    logs.append("  p:   {} hPa".format(Pi/100 if Pi is not None else "None"))
    logs.append("  ...")

    log = "\n".join(logs)

except Exception as e:
    internalFields = None
    log = "[Error] {}".format(e)
