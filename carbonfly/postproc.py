from __future__ import annotations
"""
carbonfly
    a lightweight, easy-to-use Python API and 
    toolbox for indoor CO2 CFD simulations in Grasshopper
    based on OpenFOAM and WSL

- Author: Qirui Huang
- License: LGPL-3.0
- Website: https://github.com/RWTH-E3D/carbonfly
"""

# carbonfly/postproc.py
from pathlib import Path
from typing import Iterable, List, Dict, Any, Optional, Tuple, Union

from .utils import foam_header
from .wsl import win_to_wsl_path, run_wsl_console

def write_internal_probes_dict(
    case_root: str | Path,
    *,
    points: Iterable[Iterable[float]],
    fields: Iterable[str],
    ordered: bool = True,
    filename: str = "internalProbes",
) -> Path:
    """
    Create/overwrite system/internalProbes for post-processing.

    Args:
        case_root: case folder on Windows, e.g. r"C:\Data\Carbonfly\case_name"
        points: iterable of (x, y, z)
        fields: iterable of field names, e.g. ("CO2", "T", "U")
        ordered: set to True so output order == input order (for Grasshopper)
        filename: normally 'internalProbes', but you can change it

    Returns:
        Path to the created dict (Windows path).
    """
    case_root = Path(case_root)
    system_dir = case_root / "system"
    system_dir.mkdir(parents=True, exist_ok=True)

    # build the OpenFOAM dictionary body
    header = foam_header(filename, of_class="dictionary", location="system")

    # Points
    pts_lines = ["points", "("]
    for p in points:
        x, y, z = p
        pts_lines.append(f"    ({x:g} {y:g} {z:g})")
    pts_lines.append(");")

    # Fields
    fld_lines = ["fields", "("]
    for f in fields:
        fld_lines.append(f"    {f}")
    fld_lines.append(");")

    ordered_line = f"ordered {'yes' if ordered else 'no'};"

    include_line = '#includeEtc "caseDicts/postProcessing/probes/internalProbes.cfg"'

    content_lines = [header] + pts_lines + [""] + fld_lines + ["", ordered_line, "", include_line, ""]
    content = "\n".join(content_lines)

    out_path = system_dir / filename
    out_path.write_text(content, encoding="utf-8")

    return out_path



def run_internal_probes_postprocess(
    case_root: str | Path,
    *,
    foam_bashrc: str = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,
    time_selector: Optional[str] = None,
    log_rel: str = "system/internalProbes.run.log",
) -> int:
    """
    Call `postProcess -func internalProbes` in WSL for an existing case.

    Args:
        case_root: Windows path to the case directory
        foam_bashrc: OpenFOAM bashrc
        distro: WSL distro name if needed
        time_selector:
            None          -> no time option (process all)
            "latestTime" or "latest" or "last"  -> -latestTime
            "100"         -> -time 100
            "0:100"       -> -time 0:100
        log_rel: WSL-side log path (relative to case)

    Returns:
        process return code
    """
    case_root = Path(case_root)
    cwd_wsl = win_to_wsl_path(str(case_root))

    cmd = "postProcess -func internalProbes"
    if time_selector:
        ts = time_selector.strip()
        if ts in ("latestTime", "latest", "last"):
            cmd += " -latestTime"
        else:
            cmd += f" -time {time_selector}"

    return run_wsl_console(
        cmd,
        cwd_wsl=cwd_wsl,
        foam_bashrc=foam_bashrc,
        distro=distro,
        log_rel=log_rel,
    )



def _read_points_xy(fp: Path) -> Dict[str, Any]:
    """
    Parse OpenFOAM postProcessing/internalProbes/<time>/points.xy

    File format example:
    # distance x y z CO2 T U_x U_y U_z p
    0      1.2    0.9  1.1  0.00075  293.6  0.06  -0.05  0.05  99987.6
    0.4    1.6    0.9  1.1  ...
    ...

    Args:
        fp (Path): Full path to the 'points.xy' file under 'postProcessing/internalProbes/<time>/'

    Returns:
        Dict[str, Any]: Parsed data structure with the following keys:
            - columns (List[str]): All column names from the header line.
            - points (List[Tuple[float, float, float]]): (x, y, z) coordinates.
            - distance (List[float]): Distance values from the first column.
            - scalars (Dict[str, List[float]]): Scalar fields such as CO2, T, p.
            - vectors (Dict[str, List[Tuple[float, float, float]]]):
                Vector fields reconstructed from *_x, *_y, *_z triplets, such as U.
            - raw_rows (List[Dict[str, float]]): Each data row as a mapping from column name to value.

        Example:
        {
          "columns": ["distance", "x", "y", "z", "CO2", "T", "U_x", "U_y", "U_z", "p"],
          "points":  [(x,y,z), ...],
          "distance": [..., ..., ...],
          "scalars": {
              "CO2": [...],
              "T":   [...],
              "p":   [...],
              # any other scalar columns
          },
          "vectors": {
              "U": [(Ux,Uy,Uz), ...],
              # other vector triplets if present
          },
          "raw_rows": [
              {"distance": ..., "x": ..., ...},   # one dict per row, in order
              ...
          ],
        }
    """
    lines = fp.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"{fp} is empty")

    # header
    header_line = lines[0].lstrip("#").strip()
    columns = header_line.split()
    ncols = len(columns)

    # data rows
    raw_rows: List[Dict[str, float]] = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != ncols:
            # Skip unaligned lines
            continue
        row = {col: float(val) for col, val in zip(columns, parts)}
        raw_rows.append(row)

    # distance
    distance = [row.get("distance", 0.0) for row in raw_rows]

    # points
    points: List[Tuple[float, float, float]] = []
    for row in raw_rows:
        x = row.get("x", 0.0)
        y = row.get("y", 0.0)
        z = row.get("z", 0.0)
        points.append((x, y, z))

    # Identify scalars / vectors
    # scalar -> the column name is not among these base columns, nor is it *_x/y/z.
    base_cols = {"distance", "x", "y", "z"}

    # All column names
    scalars: Dict[str, List[float]] = {}
    vectors: Dict[str, List[Tuple[float, float, float]]] = {}

    # Find all columns ending with "_x"
    vector_bases = []
    for col in columns:
        if col.endswith("_x"):
            base = col[:-2]   # remove "_x"
            # Check if it also has "_y" and "_z", if so -> vector
            if f"{base}_y" in columns and f"{base}_z" in columns:
                vector_bases.append(base)

    # Vectors
    for base in vector_bases:
        vec_list: List[Tuple[float, float, float]] = []
        for row in raw_rows:
            vx = row[f"{base}_x"]
            vy = row[f"{base}_y"]
            vz = row[f"{base}_z"]
            vec_list.append((vx, vy, vz))
        vectors[base] = vec_list

    # Scalars
    skip_cols = set(base_cols)
    for base in vector_bases:
        skip_cols.add(f"{base}_x")
        skip_cols.add(f"{base}_y")
        skip_cols.add(f"{base}_z")

    for col in columns:
        if col in skip_cols:
            continue
        scalars[col] = [row[col] for row in raw_rows]

    return {
        "columns": columns,
        "points": points,
        "distance": distance,
        "scalars": scalars,
        "vectors": vectors,
        "raw_rows": raw_rows,
    }


def collect_internal_probes_results(
    case_root: str | Path,
    which: Union[str, int] = "latest",
) -> Dict[str, Any]:
    """
    Read one sampled result from postProcessing/internalProbes/<time>/points.xy.

    Args:
        case_root (str | Path): OpenFOAM case root directory.
        which (str | int): Select which time-folder to read.
            - "latest" or "last": read the last (usually largest) time directory
            - int >= 0: read the N-th directory in sorted order (0 = first)
            - int < 0: read from the end (-1 = last, -2 = second last, ...)

    Returns:
        Dict[str, Any]: {
            "time_dir": "<time directory name, e.g. '2000'>",
            "data": {
                "columns": [...],
                "points": [...],
                "distance": [...],
                "scalars": {...},
                "vectors": {...},
                "raw_rows": [...],
            }
        }
    """
    case_root = Path(case_root)
    base = case_root / "postProcessing" / "internalProbes"
    if not base.exists():
        raise FileNotFoundError(
            f"{base} not found. Please check your input."
        )

    # collect all time dirs
    dirs: List[Path] = [d for d in base.iterdir() if d.is_dir()]
    if not dirs:
        raise FileNotFoundError(f"No time dirs under {base}")

    # sort by name
    dirs = sorted(dirs, key=lambda p: float(p.name))

    # pick which one
    if isinstance(which, str):
        w = which.lower()
        if w in ("latest", "last"):
            selected_dir = dirs[-1]
        else:
            raise ValueError(f"Unsupported selector string: {which!r}")
    else:
        idx = int(which)
        try:
            selected_dir = dirs[idx]
        except IndexError:
            raise IndexError(
                f"Selector {idx} out of range. There are only {len(dirs)} result dirs."
            )

    points_file = selected_dir / "points.xy"
    if not points_file.exists():
        raise FileNotFoundError(f"{points_file} not found")

    parsed = _read_points_xy(points_file)

    return {
        "time_dir": selected_dir.name,
        "data": parsed,
    }