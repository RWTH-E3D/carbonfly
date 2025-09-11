# GH inputs:
#   mode (Text)      # "steady" or "transient"
# GH outputs:
#   fvSolution_path (Text)   # path of fvSolution template
from carbonfly.fv_writer import get_template_path

norm = str(mode) if mode else "transient"
fvSolution_path = str(get_template_path("fvSolution", norm))
