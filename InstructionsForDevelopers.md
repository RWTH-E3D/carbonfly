# Instructions for Developers

Carbonfly consists of two key components: 

1. a Python library that implements the core functionality and provides the necessary interfaces, and 
2. a Grasshopper toolbox that exposes these features through a user-friendly graphical interface.

```
carbonfly (GitHub Repo)/
├─ carbonfly/              # Carbonfly Python library
├─ documentation/          # Carbonfly toolbox documentation
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

### Structure

```
grasshopper/UserObjects/Carbonfly
├─ 01:Create
│  ├─ CreateCFCase        # Create Carbonfly Case
│  ├─ CreateCFGeometry    # Create Carbonfly Geometry
│  │
│  └─ Carbonfly Info      # Information about Carbonfly
│
├─ 02:Boundary
│  ├─ Body                # Manikin body
│  ├─ DynamicRespiration  # Manikin dynamic respiration for transient simulation
│  ├─ DynamicWindow       # Pressure-driven dynamic window for transient simulation
│  ├─ InletVelocity       # For a constant inlet with a given velocity
│  ├─ internalFields      # Initial field definitions
│  ├─ Outlet              # Outlet condition
│  ├─ RecircReturn        # Recirculated return from the room. Pair with RecircSupply.
│  ├─ RecircSupply        # Recirculated supply to the room. Pair with RecircReturn.
│  └─ Wall                # Fixed wall (isothermal solid) condition
│
├─ 03:Recipe
│  ├─ controlDict         # OpenFOAM controlDict settings
│  ├─ fvSchemes           # OpenFOAM fvSchemes settings
│  ├─ fvSolution          # OpenFOAM fvSolution settings
│  │
│  └─ residual control    # Preset residual control list
│
├─ 04:Solution
│  ├─ blockMesh           # Run OpenFOAM blockMesh
│  ├─ runFoam             # Run OpenFOAM
│  ├─ snappyHexMesh       # Run OpenFOAM snappyHexMesh
│  ├─ surfaceFeatures     # Run OpenFOAM surfaceFeatures
│  │
│  ├─ checkMesh           # Run OpenFOAM checkMesh
│  └─ foamMonitor         # Run OpenFOAM foamMonitor
│
└─ 05:Util
   ├─ Air Exchange Rate (Maas)      # Air exchange rate in m3/h using Maas' formula
   ├─ BSA (Du Bois)       # Calculate Body Surface Area using Du Bois' formula
   ├─ CO2 generation rate # Get CO2 generation rate (L/s)
   ├─ Gagge two-node model          # Gagge Two-node model of human temperature regulation
   ├─ Gagge two-node model (sleep)  # Adaption of the Gagge model for sleep thermal environment
   ├─ Surface Wind Pressure         # Computes peak and surface wind pressure
   │
   ├─ Manikin LOD 0       # Manikin model Level of Detail 0
   │
   └─ Carbonfly Met List  # Preset physical activity (met) list
```

The scripts for each GH User Object are saved in `carbonfly/grasshopper/XXXXXX.py`.