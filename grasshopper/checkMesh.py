# GH inputs:
#   case_path (Text)   # full path to the case folder
#   run (Boolean)
# GH outputs:
#   log (Text)

from pathlib import Path

from carbonfly.wsl import run_check_mesh_console

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

    if not run:
        # Dry-run: do not execute
        logs.append("This component will execute:  checkMesh")
        logs.append("\n=== Click RUN to start checkMesh ===")
        log = "\n".join(str(x) for x in logs)

    else:
        # On run: enforce required files
        logs.append("")
        logs.append("[Run] Launching checkMesh ...")

        rc = run_check_mesh_console(
            case_root=case_dir,
            foam_bashrc=(foam_bashrc or "/opt/openfoam10/etc/bashrc"),
            distro=distro or None,
        )

        if rc == 0:
            logs.append("[OK] Please check the console opened.")
        else:
            logs.append(f"[Warning] checkMesh exited with return code: {rc}")
            logs.append("Please review the console output and OpenFOAM logs for details.")

        log = "\n".join(str(x) for x in logs)

except Exception as e:
    log = f"[Error] {e}"
