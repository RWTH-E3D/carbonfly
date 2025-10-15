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

# carbonfly/wsl.py
"""
WSL runners for OpenFOAM commands from Windows (Rhino/Grasshopper).
Opens a real Windows console window, launches WSL bash, and runs a command with
live output mirrored to an optional log file.
"""
import os
import shlex
import subprocess
from subprocess import CREATE_NEW_CONSOLE
from pathlib import Path
from typing import Optional, Tuple
import shutil


# Path utilities
def win_to_wsl_path(p: str) -> str:
    """
    Convert a Windows path (e.g., C:\\cases\\demo) into a WSL path (/mnt/c/cases/demo).
    This is intentionally minimal and does not resolve symlinks.
    """
    p = str(p).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        return f"/mnt/{p[0].lower()}/{p[2:]}"
    return p

def wsl_to_win_path(p: str) -> str:
    """
    Convert a WSL path (/mnt/c/...) to a Windows path when possible.
    Only handles /mnt/<drive>/...; other forms are returned unchanged.
    """
    if p.startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        drive = p[5].upper()
        rest = p[7:]
        return f"{drive}:\\" + rest.replace("/", "\\")
    return p


# Terminal detection
def _detect_terminal() -> Tuple[str, list[str]]:
    """
    Decide how to open a *new* console window on Windows.
    Returns (launcher_name, argv_prefix).

    We prefer Windows Terminal (wt.exe). If not present, fall back to classic console
    via `cmd.exe /c start`.
    """
    wt = shutil.which("wt.exe")
    if wt:
        # Use Windows Terminal. We'll append: -w 0 nt  (open a new tab in window 0)
        return "wt", [wt, "-w", "0", "nt"]
    # Fallback: classic console via `start`.
    return "cmd", ["cmd.exe", "/c", "start", ""]


# Core runner
def run_wsl_console(
    command: str,
    *,
    cwd_wsl: Optional[str] = None,
    foam_bashrc: Optional[str] = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,           # e.g. "Ubuntu-22.04" (match your WT profile name if you want the same icon/theme)
    log_rel: Optional[str] = None,          # e.g. "system/blockMesh.run.log"
    timeout: Optional[int] = None,
    keep_open: bool = True,
) -> int:
    """
    Launch `command` inside WSL in a Windows console, with live output.

    Args:
        command: Command to run (e.g., "blockMesh -case .").
        cwd_wsl: Working directory in WSL ("/mnt/c/.../case"). If None, no chdir.
        foam_bashrc: OpenFOAM bashrc to source before running the command.
        distro: WSL distro (e.g., "Ubuntu-22.04").
        log_rel: Relative log path (under cwd_wsl) for logging.
        timeout: Optional timeout (seconds).
        keep_open: If True, wait for a key press so the console doesn't close immediately.

    Returns:
        Process return code (int).
    """
    # Prepare the inner bash payload to run inside WSL.
    prefix = []
    if cwd_wsl:
        prefix.append(f'cd {shlex.quote(cwd_wsl)}')

    # Build the core command with real-time logging behavior when requested.
    core = command
    if log_rel:
        # Prefer `script` (PTY) for true progressive output; otherwise force line-buffering.
        quoted_cmd = shlex.quote(command)
        quoted_log = shlex.quote(log_rel)
        core = (
            f'(command -v script >/dev/null 2>&1 && '
            f'script -q -f {quoted_log} -c {quoted_cmd})'
            f' || '
            f'(stdbuf -oL -eL {quoted_cmd} 2>&1 | tee {quoted_log})'
        )

    if keep_open:
        # Keep the console window around so users can read the tail/end of output.
        core += r"; echo; echo '[Done] Press any key to close...'; read -n1 -s -r"

    inner = core
    # Source OpenFOAM bashrc if provided. Silence errors so missing files won't break execution.
    if foam_bashrc:
        inner = f'source "{foam_bashrc}" >/dev/null 2>&1 || true; ' + inner

    if prefix:
        inner = "; ".join(prefix) + "; " + inner

    # Build the WSL invocation that actually runs our bash payload.
    wsl_argv = ["wsl.exe"]
    if distro:
        wsl_argv += ["-d", distro]
    wsl_argv += ["bash", "-lc", inner]

    # Decide which terminal to use.
    launcher, prefix_argv = _detect_terminal()

    if launcher == "wt":
        wt_args = list(prefix_argv)  # [wt.exe, -w, 0, nt]
        if distro:
            wt_args += ["-p", distro]
        wt_args += ["-e"] + wsl_argv   # run wsl.exe ... bash -lc "<inner>"

        # Launch a new tab/window
        proc = subprocess.Popen(wt_args, creationflags=CREATE_NEW_CONSOLE)
    else:
        # Classic console fallback: `cmd.exe /c start "" wsl.exe ...`
        argv = prefix_argv + wsl_argv
        proc = subprocess.Popen(argv, creationflags=CREATE_NEW_CONSOLE)

    try:
        return proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise


# Some wrappers for GH components
## blockMesh
def run_blockmesh_console(
    case_root: str | Path,
    *,
    foam_bashrc: Optional[str] = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,
    timeout: Optional[int] = None,
    log_rel: str = "system/blockMesh.run.log",
) -> int:
    """
    Open a console and run `blockMesh -case .` inside the provided case folder,
    with progressive output mirrored to both the console and a log file.

    Args:
        case_root: Windows path to the case directory.
        foam_bashrc: OpenFOAM bashrc to source in WSL.
        distro: WSL distro/profile name (e.g., "Ubuntu-22.04").
        timeout: Optional max seconds to wait.
        log_rel: Relative log path written.

    Returns:
        The process return code.
    """
    case_root = Path(case_root)
    cwd_wsl = win_to_wsl_path(str(case_root))
    return run_wsl_console(
        "blockMesh -case .",
        cwd_wsl=cwd_wsl,
        foam_bashrc=foam_bashrc,
        distro=distro,
        log_rel=log_rel,
        timeout=timeout,
        keep_open=True,
    )

## surfaceFeatures
def run_surface_features_console(
    case_root: str | Path,
    *,
    foam_bashrc: Optional[str] = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,
    timeout: Optional[int] = None,
    log_rel: str = "system/surfaceFeatures.run.log",
) -> int:
    """Open a console and run `surfaceFeatures` inside the given case folder."""
    case_root = Path(case_root)
    cwd_wsl = win_to_wsl_path(str(case_root))
    return run_wsl_console(
        "surfaceFeatures",
        cwd_wsl=cwd_wsl,
        foam_bashrc=foam_bashrc,
        distro=distro,
        log_rel=log_rel,
        timeout=timeout,
        keep_open=True
    )

## snappyHexMesh
def run_snappy_console(
    case_root: str | Path,
    *,
    foam_bashrc: Optional[str] = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,
    timeout: Optional[int] = None,
    log_rel: str = "system/snappyHexMesh.run.log",
) -> int:
    """Open a console and run `snappyHexMesh -overwrite` inside the given case folder."""
    case_root = Path(case_root)
    cwd_wsl = win_to_wsl_path(str(case_root))
    return run_wsl_console(
        "snappyHexMesh -overwrite",
        cwd_wsl=cwd_wsl,
        foam_bashrc=foam_bashrc,
        distro=distro,
        log_rel=log_rel,
        timeout=timeout,
        keep_open=True
    )

## checkMesh
def run_check_mesh_console(
    case_root: str | Path,
    *,
    foam_bashrc: Optional[str] = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,
    timeout: Optional[int] = None,
    log_rel: str = "system/checkMesh.run.log",
) -> int:
    """Open a console and run `checkMesh` inside the given case folder."""
    case_root = Path(case_root)
    cwd_wsl = win_to_wsl_path(str(case_root))
    return run_wsl_console(
        "checkMesh",
        cwd_wsl=cwd_wsl,
        foam_bashrc=foam_bashrc,
        distro=distro,
        log_rel=log_rel,
        timeout=timeout,
        keep_open=True
    )


## buoyantReactingFoam
def run_foam_console(
    case_root: str | Path,
    *,
    foam_bashrc: Optional[str] = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,
    timeout: Optional[int] = None,
    log_rel: str = "buoyantReactingFoam.run.log",
) -> int:
    """Open a console and run `buoyantReactingFoam` inside the given case folder."""
    case_root = Path(case_root)
    cwd_wsl = win_to_wsl_path(str(case_root))
    return run_wsl_console(
        "buoyantReactingFoam",
        cwd_wsl=cwd_wsl,
        foam_bashrc=foam_bashrc,
        distro=distro,
        log_rel=log_rel,
        timeout=timeout,
        keep_open=True
    )


## foamMonitor for residuals
def run_foam_monitor_console(
    case_root: str | Path,
    *,
    foam_bashrc: Optional[str] = "/opt/openfoam10/etc/bashrc",
    distro: Optional[str] = None,
    timeout: Optional[int] = None,
    log_rel: str = "foamMonitor.run.log",
    start_time: Optional[float] = 0,
) -> int:
    """Open a console and run `foamMonitor` inside the given case folder."""
    case_root = Path(case_root)
    cwd_wsl = win_to_wsl_path(str(case_root))
    return run_wsl_console(
        f"foamMonitor -l postProcessing/residuals/{start_time:g}/residuals.dat",
        cwd_wsl=cwd_wsl,
        foam_bashrc=foam_bashrc,
        distro=distro,
        log_rel=log_rel,
        timeout=timeout,
        keep_open=True
    )