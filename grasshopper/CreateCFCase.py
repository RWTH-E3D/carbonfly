# GH inputs:
#   case_dir (Text)
#   case_name (Text)
#   CF_geo (List)
#   unit (Text)     # optional, m / cm / mm
#   controlDict
#   fvSchemes_path
#   fvSolution_path
#   residual
#   insidePoint     # optional, reference point inside mesh
#   internalFields
#   run (Boolean)
# GH outputs:
#   log (Text)
#   case_path (Text)

import re
import json
from collections.abc import Sequence
from pathlib import Path
import carbonfly.case as cfcase
import carbonfly.control_dict as cfdict
from carbonfly.utils import unit_scale_to_m
from carbonfly.fv_writer import copy_fv_templates_to_case, patch_fvSolution_pimple

def _safe_name(s):
    s = (s or "unnamed").strip()
    s = re.sub(r"[^\w\-]+", "_", s)
    return s or "unnamed"

def _norm_unit(u):
    u = (u or "mm").strip().lower()
    if u not in ("mm", "cm", "m"):
        raise ValueError("unit must be 'mm', 'cm', or 'm'")
    return u

def _norm_path(p):
    if not p:
        return None
    s = str(p).strip()
    return Path(s) if s else None


def _norm_residual(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s == "":
        return None
    return float(s)

def _parse_inside_point(p):
    """
    Accepts: Rhino Point3d / Vector3d / GH_Point(.Value) / [x, y, z] / (possibly [point]).
    Returns (x, y, z) or None if not parseable.
    """
    if p is None:
        return None

    # Unwrap singletons like [point]
    if isinstance(p, (list, tuple)) and len(p) == 1:
        p = p[0]

    # RhinoCommon Point3d / Vector3d or any object with X/Y/Z attrs
    if hasattr(p, "X") and hasattr(p, "Y") and hasattr(p, "Z"):
        try:
            return (float(p.X), float(p.Y), float(p.Z))
        except Exception:
            pass

    v = getattr(p, "Value", None) or getattr(p, "Location", None)
    if v is not None and hasattr(v, "X") and hasattr(v, "Y") and hasattr(v, "Z"):
        try:
            return (float(v.X), float(v.Y), float(v.Z))
        except Exception:
            pass

    # Generic sequence [x, y, z]
    if isinstance(p, Sequence) and not isinstance(p, (str, bytes)):
        if len(p) >= 3:
            try:
                return (float(p[0]), float(p[1]), float(p[2]))
            except Exception:
                pass

    return None

logs = []
try:
    # validations
    if not case_dir or not str(case_dir).strip():
        raise ValueError("case_dir is required.")
    if not CF_geo or len(CF_geo) == 0:
        raise ValueError("CF_geo is empty, please connect the output from CreateCFGeometry.")

    base_dir   = Path(str(case_dir)).expanduser()
    folder     = _safe_name(case_name)
    target_dir = base_dir / folder
    case_path  = str(target_dir)

    stl_name = "model.stl"
    unit_in  = _norm_unit(unit)
    scale_to_m = unit_scale_to_m(unit_in)

    # blockMesh settings
    pad_m = 1.0
    cell_m = 0.25

    # insidePoint
    inside_pt_model = _parse_inside_point(insidePoint)  # in model units
    inside_pt = tuple(c * scale_to_m for c in inside_pt_model) if inside_pt_model else None

    # default internalFields if not given
    U_internal      = [0.0, 0.0, 0.0]
    T_internal      = 295.15
    CO2_internal    = 0.000400
    P_internal      = 100_000.0
    P_rgh_internal  = 0
    alphat_internal = 0
    epsilon_internal= 0.01
    G_internal      = 0
    k_internal      = 0.1
    nut_internal    = 0
    Ydefault_internal   = 0

    fields = None
    if internalFields:
        fields = json.loads(internalFields)
                        
    if isinstance(fields, dict):
        U_internal      = fields.get("U",   U_internal)
        T_internal      = fields.get("T",   T_internal)
        CO2_internal    = fields.get("CO2", CO2_internal)
        P_internal      = fields.get("p",   P_internal)
        P_rgh_internal  = fields.get("p_rgh",   P_rgh_internal)
        alphat_internal = fields.get("alphat",   alphat_internal)
        epsilon_internal= fields.get("epsilon",   epsilon_internal)
        G_internal      = fields.get("G",   G_internal)
        k_internal      = fields.get("k",   k_internal)
        nut_internal    = fields.get("nut",   nut_internal)
        Ydefault_internal   = fields.get("Ydefault",   Ydefault_internal)

    # unpack controlDict
    cdict_json = None
    if controlDict:
        cdict_json = json.loads(controlDict)

    # fvSchemes & fvSolution
    fvSchemes_src = _norm_path(fvSchemes_path)
    fvSolution_src = _norm_path(fvSolution_path)

    # PIMPLE settings
    rv = _norm_residual(residual)

    if not run:
        # dry-run: no filesystem writes
        logs.append(f"Case will be created at: {target_dir}")
        logs.append(f"STL file: {stl_name}, unit: {unit_in}")
        logs.append(f"CF_geo count: {len(CF_geo)}")
        logs.append(f"blockMesh: padding_m={pad_m}, cell_size_m={cell_m}")
        logs.append("U_internal: " + (f"{U_internal} m/s" if U_internal else "None"))
        logs.append("T_internal: " + (f"{T_internal} K" if (T_internal is not None) else "None"))
        logs.append("CO2_internal: " + (f"{CO2_internal*1e6} ppm" if (CO2_internal is not None) else "None"))
        logs.append("P_internal: " + (f"{P_internal} Pa" if (P_internal is not None) else "None"))

        logs.append("P_rgh_internal: " + (f"{P_rgh_internal}" if (P_rgh_internal is not None) else "None"))
        logs.append("alphat_internal: " + (f"{alphat_internal}" if (alphat_internal is not None) else "None"))
        logs.append("epsilon_internal: " + (f"{epsilon_internal}" if (epsilon_internal is not None) else "None"))
        logs.append("G_internal: " + (f"{G_internal}" if (G_internal is not None) else "None"))
        logs.append("k_internal: " + (f"{k_internal}" if (k_internal is not None) else "None"))
        logs.append("nut_internal: " + (f"{nut_internal}" if (nut_internal is not None) else "None"))
        logs.append("Ydefault_internal: " + (f"{Ydefault_internal}" if (Ydefault_internal is not None) else "None"))
        if inside_pt is not None:
            logs.append(f"insidePoint (model units): {inside_pt_model}")
        else:
            logs.append("insidePoint: Default (Warning: may cause error))")
        if fvSchemes_src:
            logs.append(f"fvSchemes template: {fvSchemes_src}")
        else:
            logs.append("fvSchemes template not provided")
        if fvSolution_src:
            logs.append(f"fvSolution template: {fvSolution_src}")
        else:
            logs.append("fvSolution template not provided")
        logs.append(f"Residual: {rv if rv is not None else '(not provided)'}")

        logs.append("\n=== Click RUN to generate files ===")
        log = "\n".join(logs)
    else:
        # real writes
        logs.append(f"[Run] Creating case at: {target_dir}")
        # build case
        lgs, paths = cfcase.build_case(
            case_root=target_dir,
            cfgeos=CF_geo,
            stl_file_name=stl_name,
            unit=unit_in,
            internal_U=U_internal,
            internal_T=T_internal,
            internal_CO2=CO2_internal,
            internal_P=P_internal,
            internal_P_rgh=P_rgh_internal,
            internal_alphat=alphat_internal,
            internal_epsilon=epsilon_internal,
            internal_k=k_internal,
            internal_nut=nut_internal,
            internal_G=G_internal,
            internal_Ydefault=Ydefault_internal,
            write_blockmesh=True,
            padding_m=pad_m,
            cell_size_m=cell_m,
            write_snappy=True,
            inside_point=inside_pt,
            write_constant=True,
            write_fv=True,
            fvSchemes_path=fvSchemes_src,
            fvSolution_path=fvSolution_src
        )
        
        # controDict
        if cdict_json:
            cpath = cfdict.write_control_dict_from_json(target_dir, json.dumps(cdict_json))
            logs.append(f"controlDict written: {cpath}")
        
        # patch PIMPLE settings in fvSolution
        patched_path = patch_fvSolution_pimple(
            fvsolution_path=paths["fvSolution"],
            pRefPoint=inside_pt,
            residual_value=rv
        )
        logs.append(f"fvSolution patched: {patched_path}")

        # summary
        logs.append("\n==== summary ====\n")
        if 'stl' in paths:       logs.append(f"STL:               {paths.get('stl')}")
        if 'blockMesh' in paths: logs.append(f"blockMeshDict:     {paths.get('blockMesh')}")
        if 'snappy' in paths:    logs.append(f"snappyHexMeshDict: {paths.get('snappy')}")
        if 'U' in paths:         logs.append(f"0/U:               {paths['U']}")
        if 'T' in paths:         logs.append(f"0/T:               {paths['T']}")
        if 'CO2' in paths:       logs.append(f"0/CO2:             {paths['CO2']}")
        if 'p' in paths:         logs.append(f"0/p:               {paths['p']}")
        if 'p_rgh' in paths:     logs.append(f"0/p_rgh:           {paths['p_rgh']}")
        if 'alphat' in paths:    logs.append(f"0/alphat:          {paths['alphat']}")
        if 'epsilon' in paths:   logs.append(f"0/epsilon:         {paths['epsilon']}")
        if 'k' in paths:         logs.append(f"0/k:               {paths['k']}")
        if 'nut' in paths:       logs.append(f"0/nut:             {paths['nut']}")
        if 'G' in paths:         logs.append(f"0/G:               {paths['G']}")
        if 'Ydefault' in paths:  logs.append(f"0/Ydefault:        {paths['Ydefault']}")

        if inside_pt is not None:
            logs.append(f"insidePoint used: {inside_pt}")
        if 'fvSchemes' in paths:  logs.append(f"fvSchemes:         {paths['fvSchemes']}")
        if 'fvSolution' in paths: logs.append(f"fvSolution:         {paths['fvSolution']}")
        logs += lgs
        log = "\n".join(logs)

except Exception as e:
    case_path = ""
    log = f"[Error] {e}"
