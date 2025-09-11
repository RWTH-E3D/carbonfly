# GH inputs:
#   mode (Text)      # "steady" or "transient"
# GH outputs:
#   fvSchemes_path (Text)   # path of fvSchemes template
import sys, os
from pathlib import Path

from carbonfly.fv_writer import get_template_path

norm = str(mode) if mode else "transient"
p = get_template_path("fvSchemes", norm)
fvSchemes_path = str(p)
