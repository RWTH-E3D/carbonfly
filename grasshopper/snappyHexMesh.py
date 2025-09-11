# GH inputs:
#   case_path (Text)
#   run (Boolean)
# GH outputs:
#   log (Text)

from pathlib import Path

from carbonfly.wsl import run_snappy_console

def _win_to_wsl_path(p: str) -> str:
    """Convert a Windows path to a WSL path (/mnt/<drive>/...). Minimal but sufficient here."""
    p = str(p).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        return f"/mnt/{p[0].lower()}/{p[2:]}"
    return p

logs = []
try:
    # Validate inputs
    if not case_path or not str(case_path).strip():
        raise ValueError("case_path is required (full path to the case folder).")

    case_dir = Path(str(case_path)).expanduser()
    dict_file = case_dir / "system" / "snappyHexMeshDict"
    emesh_file = case_dir / "constant" / "triSurface" / "model.eMesh"

    # Basic preflight info
    logs.append(f"Case: {case_dir}")
    logs.append(f"snappyHexMeshDict: {dict_file}")
    logs.append(f"eMesh: {emesh_file}")

    # Existence checks
    dict_exists = dict_file.is_file()
    emesh_exists = emesh_file.is_file()

    if not run:
        # Dry-run: do not execute
        if dict_exists:
            logs.append("[Check] snappyHexMeshDict found.")
        else:
            logs.append("[Check] snappyHexMeshDict NOT found (run CreateCFCase first).")

        if emesh_exists:
            logs.append("[Check] eMesh found.")
        else:
            logs.append("[Check] eMesh NOT found. Run the surfaceFeatures component first.")

        logs.append("")
        logs.append("This component will execute:  snappyHexMesh -overwrite")
        logs.append("\n=== Click RUN to start snappyHexMesh ===")
        log = "\n".join(str(x) for x in logs)

    else:
        # On run: enforce required files
        if not dict_exists:
            raise FileNotFoundError("system/snappyHexMeshDict not found. Generate the case first.")
        if not emesh_exists:
            raise FileNotFoundError("constant/triSurface/model.eMesh not found. Run surfaceFeatures first.")

        logs.append("")
        logs.append("[Run] Launching snappyHexMesh -overwrite ...")

        rc = run_snappy_console(
            case_root=case_dir,
            foam_bashrc=(foam_bashrc or "/opt/openfoam10/etc/bashrc"),
            distro=distro or None,
        )

        if rc == 0:
            logs.append("[OK] Please check the console opened.")
            logs.append("Check constant/polyMesh and logs under 'system/'.")
        else:
            logs.append(f"[Warning] snappyHexMesh exited with return code: {rc}")
            logs.append("Please review the console output and OpenFOAM logs for details.")

        log = "\n".join(str(x) for x in logs)

except Exception as e:
    log = f"[Error] {e}"
