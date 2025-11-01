# GH inputs:
#   case_path (Text)
#   distro (Text)           # optional, e.g. "Ubuntu-20.04"
#   foam_bashrc (Text)      # optional, e.g. "/opt/openfoam10/etc/bashrc"
#   time_selector (Text)    # optional:
                            # None  -> no time option (process all)
                            # "latestTime" or "latest" or "last"  -> -latestTime
                            # "100" -> -time 100
                            # "0:100"   -> -time 0:100
#   run (Boolean)
# GH outputs:
#   log (Text)

from pathlib import Path
import carbonfly.postproc as cfpost

if run and case_path:
    rc = cfpost.run_internal_probes_postprocess(
        Path(case_path),
        distro=distro or None,
        foam_bashrc=(foam_bashrc or "/opt/openfoam10/etc/bashrc"),
        time_selector=time_selector or None,
    )
    log = "postProcess internalProbes finished with return code {}\n".format(rc)
    log += "[OK] Please check the console opened."
else:
    log = f"Time selected: {time_selector}\n\n"
    log += "=== Click RUN to open console and run postProcess -func internalProbes ==="