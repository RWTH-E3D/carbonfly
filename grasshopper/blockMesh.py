# GH inputs:
#   case_path (Text)
#   run (Boolean)
#   distro (Text)          # optional, e.g. "Ubuntu-22.04"
#   foam_bashrc (Text)     # optional, e.g. "/opt/openfoam10/etc/bashrc"
# GH outputs:
#   log (Text)

from pathlib import Path
import carbonfly.wsl as cfwsl

if run and case_path:
    rc = cfwsl.run_blockmesh_console(
        Path(case_path),
        distro=distro or None,
        foam_bashrc=(foam_bashrc or "/opt/openfoam10/etc/bashrc"),
    )
    log = "blockMesh finished with return code {}\n".format(rc)
    log += "[OK] Please check the console opened."
else:
    log = "=== Click RUN to open console and run blockMesh ==="
