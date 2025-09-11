# GH inputs:
#   case_path (Text)          # full path including the case folder
#   includedAngleDeg (Number) # optional, default 150
#   run (Boolean)
# GH outputs:
#   log (Text)

from pathlib import Path

# Library APIs
from carbonfly.snappy_writer import write_surface_features_dict
from carbonfly.wsl import run_surface_features_console

def _win_to_wsl_path(p: str) -> str:
    """Convert a Windows path to a WSL path (/mnt/<drive>/...). Minimal but sufficient here."""
    p = str(p).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        return f"/mnt/{p[0].lower()}/{p[2:]}"
    return p

logs = []
try:
    if not case_path or not str(case_path).strip():
        raise ValueError("case_path is required (full path including the case folder).")

    target_dir = Path(str(case_path)).expanduser()
    stl_name   = "model.stl"  # fixed name
    angle      = float(includedAngleDeg) if (includedAngleDeg is not None) else 150.0

    dict_file   = target_dir / "system" / "surfaceFeaturesDict"
    emesh_file  = target_dir / "constant" / "triSurface" / "model.eMesh"

    if not run:
        # Dry-run: nothing written, just tell the user what will happen.
        logs.append("surfaceFeaturesDict will be created:")
        logs.append(f"  {dict_file}")
        logs.append(f"STL file: {stl_name}")
        logs.append(f"includedAngle: {angle:.0f} deg")
        logs.append("After that, the component will run `surfaceFeatures` to create the eMesh:")
        logs.append(f"  {emesh_file}")
        logs.append("")
        logs.append("=== Click RUN to write the dict and execute surfaceFeatures ===")
        log = "\n".join(str(x) for x in logs)

    else:
        # 1) Write system/surfaceFeaturesDict
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = write_surface_features_dict(
            case_root=target_dir,
            stl_file_name=stl_name,
            included_angle_deg=angle
        )
        logs.append("[OK] surfaceFeaturesDict written:")
        logs.append(f"  {out_path}")

        # 2) Run surfaceFeatures in a real console via WSL
        logs.append("")
        logs.append("[Run] Executing `surfaceFeatures` to generate the eMesh...")
        
        rc = run_surface_features_console(
            case_root=target_dir,
            foam_bashrc=(foam_bashrc or "/opt/openfoam10/etc/bashrc"),
            distro=distro or None,
        )
        
        if rc == 0:
            logs.append("[OK] Please check the console opened.")
            logs.append(f"eMesh created at (expected):")
            logs.append(f"  {emesh_file}")
        else:
            logs.append(f"[Warning] surfaceFeatures exited with return code: {rc}")
            logs.append("Please check the console output and any OpenFOAM logs for details.")

        log = "\n".join(str(x) for x in logs)

except Exception as e:
    log = f"[Error] {e}"
