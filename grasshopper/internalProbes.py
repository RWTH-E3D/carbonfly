# GH inputs:
#   case_path (Text)
#   points (Point3d or List of Point3d)
#   unit (Text)     # optional, m / cm / mm
#   fields (Text or List of Text)
#   run (Boolean)
# GH outputs:
#   log (Text)

from pathlib import Path
import carbonfly.postproc as cfpost
from carbonfly.utils import unit_scale_to_m

def _norm_unit(u):
    u = (u or "mm").strip().lower()
    if u not in ("mm", "cm", "m"):
        raise ValueError("unit must be 'mm', 'cm', or 'm'")
    return u

unit_in  = _norm_unit(unit)
scale_to_m = unit_scale_to_m(unit_in)
points_m = tuple(pt * scale_to_m for pt in points)
probe_points = [(pt.X, pt.Y, pt.Z) for pt in points_m]

if run and case_path:
    try:
        path = cfpost.write_internal_probes_dict(
            Path(case_path),
            points=probe_points,
            fields=fields,
        )
        log = f"[OK] internalProbes has been created in: {path}"
    except Exception as e:
        log = str(e)
else:
    log = f"Fields: {fields}\n"
    log += f"Points [m]: {probe_points}\n\n"
    log += "=== Click RUN to write internalProbes dict for post-processing ==="