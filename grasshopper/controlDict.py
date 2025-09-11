# GH inputs:
#   mode (Text)      # "steady" or "transient"
#   endTime (Number) # transient: seconds; steady: iterations
# GH outputs:
#   controlDict (Text)
#   log (Text)

import json
import importlib
import carbonfly.control_dict as cfdict
importlib.reload(cfdict)

def _norm_mode(m):
    m = (m or "transient").strip().lower()
    return "steady" if m in ("steady", "steady-state", "steadystate") else "transient"

def _norm_endtime(val, is_transient):
    # transient -> float seconds / steady state -> int interations
    if val is None:
        return 120.0 if is_transient else 1000
    try:
        v = float(val)
    except:
        return 120.0 if is_transient else 1000
    return float(v) if is_transient else max(1, int(round(v)))

logs = []
try:
    mode_norm = _norm_mode(mode)
    is_transient = (mode_norm == "transient")
    et = _norm_endtime(endTime, is_transient)

    if is_transient:
        base = cfdict.make_default("transient", application="buoyantReactingFoam")
        base["endTime"] = float(et)   # seconds
    else:
        base = cfdict.make_default("steady", application="buoyantReactingFoam")
        base["endTime"] = int(et)     # iterations

    if writeInterval is not None:
        base["writeInterval"] = float(writeInterval)

    controlDict = json.dumps(base, ensure_ascii=False, indent=2)
    logs.append(f"[ok] controlDict configured. mode={mode_norm}, endTime={et}, writeInterval={writeInterval}, app={base.get('application')}")
    log = "\n".join(logs)

except Exception as e:
    controlDict = ""
    log = f"[Error] {e}"
