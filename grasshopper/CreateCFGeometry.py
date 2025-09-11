# GH inputs:
#   name (str), 
#   geometry (list + flatten), 
#   boundary (carbonfly boundary or list), 
#   refine_levels (interval or list)
# GH outputs:
#   CF_geo, log

import carbonfly.geo as cfgeo

def as_list(x):
    return x if isinstance(x, (list, tuple)) else [x]

def broadcast_to_len(lst, n, fallback=None):
    """If length==1 -> broadcast to n; if length==0 -> use fallback (then broadcast); else length must equal n."""
    if lst is None:
        lst = [] if fallback is None else [fallback]
    if len(lst) == 0:
        lst = [] if fallback is None else [fallback]
    if len(lst) == 1 and n > 1:
        return lst * n
    return lst

CF_geo = []
logs = []
try:
    geos = as_list(geometry)
    if not geos:
        raise ValueError("Geometry list is empty. Please connect a flattened Surface/BrepFace/Brep list.")

    N = len(geos)

    # name
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Input 'name' must be a single non-empty string.")
    region_name = name.strip()
    names = [region_name] * N   # broadcast the same name to all geometries

    # boundary
    bnds = as_list(boundary) if boundary is not None else []
    bnds = broadcast_to_len(bnds, N, fallback=None)
    if len(bnds) != N:
        raise ValueError(f"The number of boundaries ({len(bnds)}) does not match the number of geometries ({N}) and cannot be broadcast.")

    # refine_levels
    refs = as_list(refine_levels) if refine_levels is not None else []
    refs = broadcast_to_len(refs, N, fallback=None)
    if len(refs) != N:
        raise ValueError(f"The number of refine_levels ({len(refs)}) does not match the number of geometries ({N}) and cannot be broadcast.")

    # build CFGeo items
    for i in range(N):
        cg = cfgeo.make_cfgeo(names[i], geos[i], bnds[i], refs[i])
        CF_geo.append(cg)

    logs.append(f"CF_geo created: {len(CF_geo)} item(s):\n{CF_geo[0].name} -> refine=({CF_geo[0].refine.min_level}, {CF_geo[0].refine.max_level})")
    log = "\n".join(logs)

except Exception as e:
    CF_geo = []
    log = f"[Error] {e}"
