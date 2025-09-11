# GH inputs:
#   case_path (Text)
#   start_time (Float)
#   run (Boolean)
# GH outputs:
#   log (Text)

from pathlib import Path

from carbonfly.wsl import run_foam_monitor_console

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

    if start_time is None:
        start_time = 0

    if not run:
        # Dry-run: do not execute
        logs.append(f"This component will execute:  `foamMonitor -l postProcessing/residuals/{start_time}/residuals.dat`")
        logs.append("\n=== Click RUN to start foamMonitor ===")
        log = "\n".join(str(x) for x in logs)

    else:
        # On run: enforce required files
        logs.append("")
        logs.append("[Run] Launching foamMonitor ...")

        rc = run_foam_monitor_console(
            case_root=case_dir,
            foam_bashrc=(foam_bashrc or "/opt/openfoam10/etc/bashrc"),
            distro=distro or None,
            start_time=start_time
        )

        if rc == 0:
            logs.append("[OK] Please check the console opened.")
        else:
            logs.append(f"[Warning] foamMonitor exited with return code: {rc}")
            logs.append("Please review the console output and OpenFOAM logs for details.")

        log = "\n".join(str(x) for x in logs)

except Exception as e:
    log = f"[Error] {e}"
