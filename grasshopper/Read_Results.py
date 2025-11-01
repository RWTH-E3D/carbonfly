# GH inputs:
#   case_path (Text)
#   which (Text)    # optional:
                    # "latest" or "last": read the last (usually largest) time directory
                    # int >= 0: read the N-th directory in sorted order (0 = first)
                    # int < 0: read from the end (-1 = last, -2 = second last, ...)
#   field (Text)
#   unit (Text)
# GH outputs:
#   time_dir
#   points
#   values

import Rhino
from pathlib import Path
import carbonfly.postproc as cfpost
from carbonfly.utils import unit_scale_to_m

def _norm_unit(u):
    u = (u or "mm").strip().lower()
    if u not in ("mm", "cm", "m"):
        raise ValueError("unit must be 'mm', 'cm', or 'm'")
    return u

results = None
points_m = None
values = None

if which is None or which == "":
    which = "latest"
else:
    if isinstance(which, str):
        s = which.strip()
        try:
            which = int(s)
        except ValueError:
            which = s
    elif isinstance(which, float) and which.is_integer():
        which = int(which)


results = cfpost.collect_internal_probes_results(
    Path(case_path),
    which=which,
)
time_dir = results["time_dir"]
data = results["data"]
points_m = data["points"]
# convert back to Rhino unit
unit_in  = _norm_unit(unit)
scale_to_m = unit_scale_to_m(unit_in)
points = [
    Rhino.Geometry.Vector3d(
        x_m / scale_to_m, 
        y_m / scale_to_m, 
        z_m / scale_to_m
    )
    for (x_m, y_m, z_m) in points_m
]

# read data
if field == "U":
    u_list = data["vectors"].get("U", [])
    values = [
        Rhino.Geometry.Vector3d(ux, uy, uz)
        for (ux, uy, uz) in u_list
    ]
else:
    values = data["scalars"][field]
