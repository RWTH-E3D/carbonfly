# Instructions for Developers

Carbonfly consists of two key components: 

1. a Python library that implements the core functionality and provides the necessary interfaces, and 
2. a Grasshopper toolbox that exposes these features through a user-friendly graphical interface.

```
carbonfly (GitHub Repo)/
├─ carbonfly/              # Carbonfly Python library
├─ examples/               # Examples
├─ grasshopper/            # Carbonfly Grasshopper toolbox
│  ├─ UserObjects/         # Grasshopper User Objects
│  └─ icons/               # Icons for GH User Objects
├─ pics/                   # Pictures/screenshots for README
│
├─ CHANGELOG.md            # Changelog
├─ HowToInstall.md         # Installation guide
├─ InstructionsForDevelopers.md  # This file
├─ LICENSE                 # License
└─ README.md               # README
```

## Python library

### Structure

```
carbonfly/
├─ case.py                # OpenFOAM case manager
├─ blockmesh_writer.py    # Writes system/blockMeshDict
├─ constant_writer.py     # Writes constant/*
├─ control_dict.py        # Writes system/controlDict & functionObjects
├─ field_writer.py        # Writes 0/* fields (U, T, CO2, p_rgh, etc.)
├─ fv_writer.py           # Writes fvSchemes/fvSolution
├─ snappy_writer.py       # Writes snappyHexMeshDict & surfaceFeatures dicts
├─ boundary.py            # Boundary conditions
├─ geo.py                 # Geometry normalization
├─ mesh.py                # Rhino Brep -> Mesh conversion & STL export helpers
├─ utils.py               # Helper functions
├─ wsl.py                 # Launches OpenFOAM in WSL
│
├─ templates/             # Shipped OpenFOAM templates
│  ├─ constant/           # e.g., g, thermophysical...
│  ├─ steadystate/        # fvSchemes / fvSolution for steady-state runs
│  ├─ transient/          # fvSchemes / fvSolution for transient runs
│  └─ residuals/          # residuals functionObject
│
└─ pythermalcomfort/      # Thermal comfort models
   └─ models/
      ├─ two_nodes_gagge.py
      └─ two_nodes_gagge_sleep.py

```

## Grasshopper toolbox

coming soon...