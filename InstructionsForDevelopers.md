# Instructions for Developers

<!-- TOC -->
* [Instructions for Developers](#instructions-for-developers)
  * [Python library](#python-library)
    * [Structure](#structure)
  * [Grasshopper toolbox](#grasshopper-toolbox)
    * [Structure](#structure-1)
  * [FAQ](#faq)
    * [Q1: Does Carbonfly support other OpenFOAM versions, such as v8, for use with urbanMicroclimateFoam?](#q1-does-carbonfly-support-other-openfoam-versions-such-as-v8-for-use-with-urbanmicroclimatefoam)
    * [Q2: Why does Carbonfly use WSL instead of blueCFD-Core?](#q2-why-does-carbonfly-use-wsl-instead-of-bluecfd-core)
    * [Q3: How can I add a new boundary condition in Carbonfly?](#q3-how-can-i-add-a-new-boundary-condition-in-carbonfly)
<!-- TOC -->

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

## FAQ

### Q1: Does Carbonfly support other OpenFOAM versions, such as v8, for use with urbanMicroclimateFoam?

Yes and no. 

You can use most Carbonfly components with OpenFOAM v8 to generate a case and run blockMesh, surfaceFeature, 
snappyHexMesh, and checkMesh.

However, the `buoyantReactingFoam` solver that Carbonfly uses for CO2 simulations is not available in 
OpenFOAM v8. To use [urbanMicroclimateFoam](https://github.com/OpenFOAM-BuildingPhysics/urbanMicroclimateFoam) 
with OpenFOAM v8, for example, you need to edit `run_foam_console()` or better add a new one to `wsl.py` for your 
specific usage. Depending on the solver you used, you may also need to adjust the boundary conditions.

If you would like to try OpenFOAM v8, please follow the steps below:

1. Install OpenFOAM v8 by following the official guide: https://openfoam.org/download/8-ubuntu/

2. Use `/opt/openfoam8/etc/bashrc` as the input for `foam_bashrc`, see the example with Carbonfly `blockMesh` below:

![Example Carbonfly with OpenFOAM v8](pics/Carbonfly_with_OpenFOAM_v8_example.png)

### Q2: Why does Carbonfly use WSL instead of blueCFD-Core?

Carbonfly uses WSL (Windows Subsystem for Linux) on Windows 10 or 11 as a bridge to learning and working with 
native OpenFOAM. Most advanced applications and research workflows are ultimately more convenient in WSL or 
a pure Linux environment.

In contrast, blueCFD-Core offers only a limited selection of OpenFOAM versions, and it also requires a separate 
installation process. The effort required for the latter is roughly comparable to setting up WSL. 
Therefore, adopting WSL provides a more flexible, future-proof solution for beginners and advanced users alike.

### Q3: How can I add a new boundary condition in Carbonfly?

Below are the steps to create a custom boundary condition for your use:

1. Check the classes in `carbonfly/boundary.py` to see if your needed boundary condition is already defined.

2. If so, you can use it directly in Grasshopper. For reference, see the scripts for each GH User Object in `carbonfly/grasshopper/XXXXXX.py`.

3. If not: 

   1. Add a new class in `carbonfly/boundary.py`
   
   2. Update `field_writer.py` for example `_field_block_text()`