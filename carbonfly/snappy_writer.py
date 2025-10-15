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

# carbonfly/snappy_writer.py
from pathlib import Path
from typing import Dict, List, Tuple, Iterable, Optional
from .utils import foam_header

# Utilities
def _unique_ordered(items: Iterable[str]) -> List[str]:
    """
    Keep items unique while preserving order.
    """
    seen = set()
    out: List[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)

    return out

# surfaceFeatureExtract
def write_surface_features_dict(
    case_root: Path,
    stl_file_name: str,
    *,
    included_angle_deg: float = 150.0
) -> Path:
    """
    Write system/surfaceFeaturesDict for OpenFOAM.
    """
    lines: List[str] = []
    lines.append(foam_header("surfaceFeaturesDict"))
    lines.append(f'surfaces ("{stl_file_name}");')
    lines.append("")
    lines.append("// Identify a feature when angle between faces < includedAngle")
    lines.append(f"includedAngle   {float(included_angle_deg):.0f};")
    lines.append("")

    out_path = case_root / "system" / "surfaceFeaturesDict"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")

    return out_path

# Main writer
def write_snappy_geometry(
    case_root: Path,
    stl_file_name: str,
    regions: List[str],
    region_levels: Dict[str, Tuple[int, int]],
    *,
    castellated_mesh: bool = True,
    snap: bool = False,
    add_layers: bool = False,
    feature_level: int = 3,                 # refinement level for eMesh features
    resolve_feature_angle_deg: float = 30.0,   # castellatedMeshControls.resolveFeatureAngle
    n_cells_between_levels: int = 3,
    max_local_cells: int = 1_000_000,
    max_global_cells: int = 20_000_000,
    min_refinement_cells: int = 2,
    snap_n_smooth_patch: int = 5,
    snap_tolerance: float = 1.0,
    snap_n_solve_iter: int = 200,
    snap_n_relax_iter: int = 10,
    mesh_quality_block: Optional[str] = None,   # allow caller to override meshQualityControls
    extra_blocks: Optional[List[str]] = None,   # some optional extra blocks
    merge_tolerance: float = 1e-6,
    allow_free_standing_zone_faces: bool = True,
    inside_point: Tuple[float, float, float] = (0.5, 0.5, 0.5),
) -> Path:
    """
    Write snappyHexMeshDict
    The <stl>.eMesh is produced by the `surfaceFeatures` utility (system/surfaceFeaturesDict).
    """
    # Ensure unique region list with stable order
    regions = _unique_ordered(regions or [])

    # Compute global min/max level from per-region levels
    if region_levels:
        gmin = min(v[0] for v in region_levels.values())
        gmax = max(v[1] for v in region_levels.values())
    else:
        gmin = gmax = 0

    # Expected location of the feature edges used by snappy
    stem = Path(stl_file_name).stem
    features_file_rel = f"{stem}.eMesh"

    lines: List[str] = []
    lines.append(foam_header("snappyHexMeshDict", location="system"))
    lines.append(f"castellatedMesh {str(castellated_mesh).lower()};")
    lines.append(f"snap            {str(snap).lower()};")
    lines.append(f"addLayers       {str(add_layers).lower()};")
    lines.append("")

    # geometry
    lines.append("geometry")
    lines.append("{")
    lines.append(f"    {stl_file_name}")
    lines.append("    {")
    lines.append("        type triSurfaceMesh;")
    lines.append(f"        name {stem};")
    lines.append("        regions")
    lines.append("        {")
    for r in regions:
        lines.append(f"            {r}")
        lines.append("            {")
        lines.append(f"                name {r};")
        lines.append("            }")
    lines.append("        }")
    lines.append("    }")
    lines.append("}")
    lines.append("")

    # castellatedMeshControls
    ix, iy, iz = inside_point
    lines.append("castellatedMeshControls")
    lines.append("{")
    lines.append(f"    maxLocalCells        {max_local_cells};")
    lines.append(f"    maxGlobalCells       {max_global_cells};")
    lines.append(f"    minRefinementCells   {min_refinement_cells};")
    lines.append(f"    nCellsBetweenLevels  {n_cells_between_levels};")
    lines.append(f"    resolveFeatureAngle  {float(resolve_feature_angle_deg):.1f};")
    lines.append("")
    lines.append(f"    locationInMesh       ({ix} {iy} {iz});")
    lines.append(f"    allowFreeStandingZoneFaces {str(allow_free_standing_zone_faces).lower()};")
    lines.append("")
    lines.append("    features")
    lines.append("    (")
    lines.append("        {")
    lines.append(f"            file  \"{features_file_rel}\";")
    lines.append(f"            level {int(feature_level)};")
    lines.append("        }")
    lines.append("    );")
    lines.append("")

    # refinementSurfaces
    lines.append("    refinementSurfaces")
    lines.append("    {")
    lines.append(f"        {stem}")
    lines.append("        {")
    lines.append(f"            level ({gmin} {gmax});")
    lines.append("            regions")
    lines.append("            {")
    for r in regions:
        mn, mx = region_levels.get(r, (0, 0))
        lines.append(f"                {r}")
        lines.append("                {")
        lines.append(f"                    level ({mn} {mx});")
        lines.append("                }")
    lines.append("            }")
    lines.append("        }")
    lines.append("    }")
    lines.append("}")
    lines.append("")

    # snapControls
    lines.append("snapControls")
    lines.append("{")
    lines.append(f"    nSmoothPatch  {int(snap_n_smooth_patch)};")
    lines.append(f"    tolerance     {float(snap_tolerance):.3g};")
    lines.append(f"    nSolveIter    {int(snap_n_solve_iter)};")
    lines.append(f"    nRelaxIter    {int(snap_n_relax_iter)};")
    lines.append("    nFeatureSnapIter        10;")
    lines.append("    implicitFeatureSnap     false;")
    lines.append("    multiRegionFeatureSnap  true;")
    lines.append("}")
    lines.append("")

    # addLayersControls: not needed in carbonfly, leave empty
    lines.append("addLayersControls")
    lines.append("{")
    lines.append("}")
    lines.append("")

    # meshQualityControls: override-able
    if mesh_quality_block is not None:
        lines.append(mesh_quality_block.rstrip())
        lines.append("")
    else:
        lines.append("meshQualityControls")
        lines.append("{")
        lines.append("    maxNonOrtho          65;")
        lines.append("    maxBoundarySkewness  20;")
        lines.append("    maxInternalSkewness  4;")
        lines.append("    maxConcave           80;")
        lines.append("    minFlatness          0.5;")
        lines.append("    minVol               1e-13;")
        lines.append("    minTetQuality        1e-15;")
        lines.append("    minArea              -1;")
        lines.append("    minTwist             0.02;")
        lines.append("    minDeterminant       0.001;")
        lines.append("    minFaceWeight        0.05;")
        lines.append("    minVolRatio          0.01;")
        lines.append("    minTriangleTwist     -1;")
        lines.append("    nSmoothScale         4;")
        lines.append("    errorReduction       0.75;")
        lines.append("    relaxed")
        lines.append("    {")
        lines.append(f"        maxNonOrtho     75;")
        lines.append("    }")
        lines.append("}")
        lines.append("")

    lines.append(f"debug 0;")
    lines.append(f"mergeTolerance {merge_tolerance:.1e};")  # e.g., 1.0e-06
    lines.append("")

    if extra_blocks:
        for blk in extra_blocks:
            lines.append(blk.rstrip())
            lines.append("")

    out_path = case_root / "system" / "snappyHexMeshDict"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")

    return out_path
