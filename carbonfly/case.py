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

# carbonfly/case.py
from pathlib import Path
from collections import defaultdict
import math
from typing import Iterable, Dict, List, Tuple, Optional

from .mesh import brep_to_mesh, write_multi_solid_ascii_stl
from .field_writer import write_0_field
from .snappy_writer import write_snappy_geometry, write_surface_features_dict
from .blockmesh_writer import write_blockmesh_dict
from .constant_writer import write_constant_files, write_residuals_file
from .fv_writer import copy_fv_templates_to_case
from .boundary import Boundary
from .utils import unit_scale_to_m

# import CFGeo for type hints only (avoids circular imports at runtime)
try:
    from .geo import CFGeo
except Exception:
    CFGeo = object


# helpers
def ensure_case_dirs(case_root: Path) -> None:
    """Ensure standard OpenFOAM case subfolders exist: 0/, system/, constant/triSurface/."""
    (case_root / "0").mkdir(parents=True, exist_ok=True)
    (case_root / "system").mkdir(exist_ok=True)
    (case_root / "constant" / "triSurface").mkdir(parents=True, exist_ok=True)


def _unique_ordered(items: Iterable[str]) -> List[str]:
    """Return items with original order preserved and duplicates removed."""
    seen = set()
    out: List[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out

def _union_bbox_in_m(cfgeos, unit: str):
    """Return (min_xyz_m, max_xyz_m) in meters, using the same scale as STL export."""
    sf = unit_scale_to_m(unit)
    first = True
    bbox = None
    for g in cfgeos:
        bb = g.brep.GetBoundingBox(True)
        if first:
            bbox = bb
            first = False
        else:
            bbox.Union(bb)
    if bbox is None:
        raise ValueError("Cannot compute bounding box.")
    # scale to m
    min_m = (bbox.Min.X * sf, bbox.Min.Y * sf, bbox.Min.Z * sf)
    max_m = (bbox.Max.X * sf, bbox.Max.Y * sf, bbox.Max.Z * sf)
    return min_m, max_m


def _write_paraview_marker(case_root: Path, filename: str = None) -> Path:
    """
    Create an empty <caseName>.foam file at the case root for ParaView.
    If filename is None, use case_root.name + '.foam'.
    """
    case_root = Path(case_root)
    foam_name = filename or (case_root.name + ".foam")
    p = case_root / foam_name
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("// carbonfly ParaView marker\n", encoding="utf-8")
    return p

# orchestrator
def build_case(
    case_root: Path,
    cfgeos: Iterable["CFGeo"],
    stl_file_name: str = "model.stl",
    unit: str = "mm",
    internal_U=None,      # tuple (Ux,Uy,Uz) or None
    internal_T=None,      # float (K) or None
    internal_CO2=None,    # float (volume fraction) or None
    internal_P=None,      # float (Pa) or None
    internal_P_rgh=None,
    internal_alphat=None,
    internal_epsilon=None,
    internal_k=None,
    internal_nut=None,
    internal_G=None,
    internal_Ydefault=None,
    write_blockmesh: bool = True,
    padding_m: float = 1.0,
    cell_size_m: float = 0.25,
    write_snappy: bool = True,
    snap: bool = True,
    inside_point: Tuple[float, float, float] = (0.5, 0.5, 0.5),
    write_constant: bool = True,
    write_fv: bool = True,
    fvSchemes_path: Optional[Path] = None,
    fvSolution_path: Optional[Path] = None,
    write_residuals: bool = True
):
    """
    Main orchestrator:
      1) Mesh each CFGeo.brep and export a multi-solid ASCII STL (scaled to meters by 'unit').
      2) Optionally write system/snappyHexMeshDict (geometry{...regions{...}} + refinementSurfaces).
      3) Aggregate boundary specs by patch and write 0/U, 0/T, 0/CO2.

    Args:
        case_root:  Path to the case root directory (e.g. /path/to/case_dir/case_name).
        cfgeos:     Iterable of CFGeo objects (name, brep, boundary, refine).
        stl_file_name:  Output STL file name under constant/triSurface/.
        unit:           Input geometry unit: "mm" (default), "cm", or "m".
        internal_U:     Optional internalField for U (tuple).
        internal_T:     Optional internalField for T.
        internal_CO2:   Optional internalField for CO2.
        internal_P:     Optional internalField for p.
        internal_P_rgh: Optional internalField for p_rgh.
        internal_alphat:    Optional internalField for alphat.
        internal_epsilon:   Optional internalField for epsilon.
        internal_k:     Optional internalField for k.
        internal_nut:   Optional internalField for nut.
        internal_G:     Optional internalField for G.
        internal_Ydefault:  Optional internalField for Ydefault.
        write_blockmesh:    If True, write blockMeshDict.
        padding_m:      Extra margin (in meters) added around the union of all CFGeo bounding boxes when computing the blockMesh domain extents.
        cell_size_m:    Target approximate cell size (in meters) used to derive (nx,ny,nz) for blockMesh.
        write_snappy:   If True, write snappyHexMeshDict.
        snap:           snap setting in snappyHexMeshDict.
        inside_piont:   Reference point inside model.
        write_constant: If True, write constant/ files.
        write_fv:       If True, write fvSolution & fvSchemes.
        fvSchemes_path: fvSchemes template path.
        fvSolution_path:fvSolution template path.
        write_residuals:If True, write system/residuals.

    Returns:
        (logs, paths) where:
            logs  -> list[str] describing what was written/warned,
            paths -> dict with keys like "stl", "snappy", "U", "T", "CO2" mapping to written file Paths.
    """
    # Materialize input list and basic validation
    cfgeos = list(cfgeos or [])
    if not cfgeos:
        raise ValueError("build_case: empty CFGeo list.")

    # 0) Ensure case folder structure exists only when we actually write
    ensure_case_dirs(case_root)

    # 1) Mesh all geometries and collect region names + refine levels
    named_meshes: List[Tuple[str, "Rhino.Geometry.Mesh"]] = []
    regions: List[str] = []
    region_levels: Dict[str, Tuple[int, int]] = {}

    for g in cfgeos:
        # Mesh the Brep
        m = brep_to_mesh(g.brep)
        if m is None or m.Vertices.Count == 0 or m.Faces.Count == 0:
            raise RuntimeError(f"Meshing failed for region '{getattr(g, 'name', '?')}'")

        named_meshes.append((g.name, m))

        # Collect region names (unique) and per-region refine levels
        if g.name not in regions:
            regions.append(g.name)
        region_levels[g.name] = (int(g.refine.min_level), int(g.refine.max_level))

    # Export STL
    stl_path = case_root / "constant" / "triSurface" / stl_file_name
    write_multi_solid_ascii_stl(stl_path, named_meshes, unit)

    logs = [f"carbonfly - STL written: {stl_path} (unit={unit} -> meters)"]
    paths = {"stl": stl_path, "snappy": None}

    # 2) OpenFOAM settings
    # 2a) blockMeshDict
    blockmesh_path = None
    if write_blockmesh:
        (xmin, ymin, zmin), (xmax, ymax, zmax) = _union_bbox_in_m(cfgeos, unit)
        # add padding around the geometry
        xmin -= padding_m; ymin -= padding_m; zmin -= padding_m
        xmax += padding_m; ymax += padding_m; zmax += padding_m
        blockmesh_path = write_blockmesh_dict(
            case_root,
            min_xyz=(xmin,ymin,zmin),
            max_xyz=(xmax,ymax,zmax),
            cells=None,                 # compute from cell_size
            cell_size=cell_size_m,      # meters
            grading=(1.0,1.0,1.0),
            convert_to_meters=1.0,      # STL is already in meters
        )
        logs.append(f"carbonfly - blockMeshDict written: {blockmesh_path}")
        paths["blockMesh"] = blockmesh_path

    # 2b) surfaceFeaturesDict + snappyHexMeshDict
    snappy_path = None
    if write_snappy:
        # i) Write system/surfaceFeaturesDict (for the `surfaceFeatures` utility)
        sfx_path = write_surface_features_dict(
            case_root=case_root,
            stl_file_name=stl_file_name,
            included_angle_deg=150.0  # expose later if needed
        )
        logs.append(f"carbonfly - surfaceFeaturesDict written: {sfx_path}")
        paths["surfaceFeaturesDict"] = sfx_path

        # Tell the caller where the eMesh will appear after running `surfaceFeatures`
        emesh_path = case_root / "constant" / "triSurface" / f"{stl_file_name}.eMesh"
        paths["eMesh"] = emesh_path  # created by OpenFOAM, not by us

        # ii) Write system/snappyHexMeshDict (includes features -> <stl>.eMesh)
        regions = list(dict.fromkeys(regions))  # keep order & unique
        feat_lvl = max((mx for mx in (lv[1] for lv in region_levels.values())), default=3)
        feat_lvl = max(1, min(3, feat_lvl))

        snappy_path = write_snappy_geometry(
            case_root, stl_file_name, regions, region_levels,
            castellated_mesh=True, snap=snap, add_layers=False,
            feature_level=feat_lvl,
            inside_point= inside_point,
        )
        paths["snappy"] = snappy_path
        logs.append(f"carbonfly - snappyHexMeshDict written: {snappy_path}")

    # 2c) constant/ dicts
    if write_constant:
        write_constant_files(case_root)
        logs.append(f"carbonfly - constant/ dicts written")

    # 2d) system/fvSolution & fvSchemes
    if write_fv:
        fv_written = copy_fv_templates_to_case(
            case_root,
            fvSchemes_src=fvSchemes_path,
            fvSolution_src=fvSolution_path,
            overwrite=True,
        )
        paths["fvSchemes"] = fv_written["fvSchemes"]
        paths["fvSolution"] = fv_written["fvSolution"]
        logs.append(f"carbonfly - fvSolution & fvSchemes written")

    # 2e) system/residuals
    if write_residuals:
        write_residuals_file(case_root)
        logs.append(f"carbonfly - system/residuals written")

    # 3) Aggregate patch field specs (U/T/CO2/p) and write 0/ files
    #    Patch name resolution priority:
    #       boundary.patch_name  or  boundary.region_name  or  CFGeo.name
    patch_specs = defaultdict(lambda: {
        "U": None, 
        "T": None, 
        "CO2": None,
        "air": None, 
        "p": None,
        "p_rgh": None,
        "alphat": None,
        "epsilon": None,
        "k": None,
        "nut": None,
        "G": None,
        "Ydefault": None,
    })
    conflict_notes: List[str] = []

    for g in cfgeos:
        b: Boundary = g.boundary
        patch = (getattr(b, "patch_name", None) or getattr(b, "region_name", None) or g.name)

        # Merge U/T/CO2/p specs per patch; if conflicts, keep the first and log a warning
        for fld in ("U", "T", "CO2", "air", "p", "p_rgh", "alphat", "epsilon", "k", "nut", "G", "Ydefault"):
            spec = (b.fields or {}).get(fld)
            if spec is None:
                continue
            if patch_specs[patch][fld] is None:
                patch_specs[patch][fld] = spec
            else:
                if patch_specs[patch][fld].to_dict() != spec.to_dict():
                    conflict_notes.append(
                        f"[Warn] Patch '{patch}' field '{fld}' has conflicting specs; keeping the first."
                    )

    need_U  = any(v["U"]   is not None for v in patch_specs.values()) or (internal_U  is not None)
    need_T  = any(v["T"]   is not None for v in patch_specs.values()) or (internal_T  is not None)
    need_CO2 = any(v["CO2"] is not None for v in patch_specs.values()) or (internal_CO2 is not None)
    need_p = any(v["p"] is not None for v in patch_specs.values()) or (internal_P is not None)
    need_p_rgh = any(v["p_rgh"] is not None for v in patch_specs.values()) or (internal_P_rgh is not None)
    need_alphat = any(v["alphat"] is not None for v in patch_specs.values()) or (internal_alphat is not None)
    need_epsilon = any(v["epsilon"] is not None for v in patch_specs.values()) or (internal_epsilon is not None)
    need_k = any(v["k"] is not None for v in patch_specs.values()) or (internal_k is not None)
    need_nut = any(v["nut"] is not None for v in patch_specs.values()) or (internal_nut is not None)
    need_G = any(v["G"] is not None for v in patch_specs.values()) or (internal_G is not None)
    need_Ydefault = any(v["Ydefault"] is not None for v in patch_specs.values()) or (internal_Ydefault is not None)

    # Write 0/ fields (optionally infer internal when None to help stability)
    if need_U:
        paths["U"] = write_0_field(
            case_root=case_root,
            field_name="U",
            internal_value=internal_U,
            patch_specs={p: v["U"] for p, v in patch_specs.items()},
            dimensions="[0 1 -1 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/U written: {paths['U']}")

    if need_T:
        tval = float(internal_T) if (internal_T is not None and math.isfinite(internal_T)) else None
        paths["T"] = write_0_field(
            case_root=case_root,
            field_name="T",
            internal_value=tval,
            patch_specs={p: v["T"] for p, v in patch_specs.items()},
            dimensions="[0 0 0 1 0 0 0]"
        )
        logs.append(f"carbonfly - 0/T written: {paths['T']}")

    if need_CO2:
        # CO2
        cval = float(internal_CO2) if (internal_CO2 is not None and math.isfinite(internal_CO2)) else None
        paths["CO2"] = write_0_field(
            case_root=case_root,
            field_name="CO2",
            internal_value=cval,
            patch_specs={p: v["CO2"] for p, v in patch_specs.items()},
            dimensions="[0 0 0 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/CO2 written: {paths['CO2']}")

        # Air, based on CO2: Air + CO2 = 1
        airval = 1- cval if cval is not None else None
        paths["air"] = write_0_field(
            case_root=case_root,
            field_name="air",
            internal_value=airval,
            patch_specs={p: v["air"] for p, v in patch_specs.items()},
            dimensions="[0 0 0 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/air written: {paths['air']}")

    if need_p:
        pval = float(internal_P) if (internal_P is not None and math.isfinite(internal_P)) else None
        paths["p"] = write_0_field(
            case_root=case_root,
            field_name="p",
            internal_value=pval,
            patch_specs={p: v["p"] for p, v in patch_specs.items()},
            dimensions="[1 -1 -2 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/p written: {paths['p']}")

    if need_p_rgh:
        prghval = float(internal_P_rgh) if (internal_P_rgh is not None and math.isfinite(internal_P_rgh)) else None
        paths["p_rgh"] = write_0_field(
            case_root=case_root,
            field_name="p_rgh",
            internal_value=prghval,
            patch_specs={p: v["p_rgh"] for p, v in patch_specs.items()},
            dimensions="[1 -1 -2 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/p_rgh written: {paths['p_rgh']}")
    
    if need_alphat:
        alphatval = float(internal_alphat) if (internal_alphat is not None and math.isfinite(internal_alphat)) else None
        paths["alphat"] = write_0_field(
            case_root=case_root,
            field_name="alphat",
            internal_value=alphatval,
            patch_specs={p: v["alphat"] for p, v in patch_specs.items()},
            dimensions="[1 -1 -1 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/alphat written: {paths['alphat']}")

    if need_epsilon:
        epsilonval = float(internal_epsilon) if (internal_epsilon is not None and math.isfinite(internal_epsilon)) else None
        paths["epsilon"] = write_0_field(
            case_root=case_root,
            field_name="epsilon",
            internal_value=epsilonval,
            patch_specs={p: v["epsilon"] for p, v in patch_specs.items()},
            dimensions="[0 2 -3 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/epsilon written: {paths['epsilon']}")

    if need_k:
        kval = float(internal_k) if (internal_k is not None and math.isfinite(internal_k)) else None
        paths["k"] = write_0_field(
            case_root=case_root,
            field_name="k",
            internal_value=kval,
            patch_specs={p: v["k"] for p, v in patch_specs.items()},
            dimensions="[0 2 -2 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/k written: {paths['k']}")

    if need_nut:
        nutval = float(internal_nut) if (internal_nut is not None and math.isfinite(internal_nut)) else None
        paths["nut"] = write_0_field(
            case_root=case_root,
            field_name="nut",
            internal_value=nutval,
            patch_specs={p: v["nut"] for p, v in patch_specs.items()},
            dimensions="[0 2 -1 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/nut written: {paths['nut']}")

    if need_G:
        gval = float(internal_G) if (internal_G is not None and math.isfinite(internal_G)) else None
        paths["G"] = write_0_field(
            case_root=case_root,
            field_name="G",
            internal_value=gval,
            patch_specs={p: v["G"] for p, v in patch_specs.items()},
            dimensions="[1 0 -3 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/G written: {paths['G']}")

    if need_Ydefault:
        ydval = float(internal_Ydefault) if (internal_Ydefault is not None and math.isfinite(internal_Ydefault)) else None
        paths["Ydefault"] = write_0_field(
            case_root=case_root,
            field_name="Ydefault",
            internal_value=ydval,
            patch_specs={p: v["Ydefault"] for p, v in patch_specs.items()},
            dimensions="[0 0 0 0 0 0 0]"
        )
        logs.append(f"carbonfly - 0/Ydefault written: {paths['Ydefault']}")

    # 4) Add <caseName>.foam
    foam_marker = _write_paraview_marker(case_root)
    paths["foam"] = foam_marker
    logs.append(f"carbonfly - ParaView marker written: {foam_marker}")

    # Append any conflict warnings at the end
    logs += conflict_notes
    return logs, paths
