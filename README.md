# Carbonfly

[![Downloads](https://img.shields.io/github/downloads/RWTH-E3D/carbonfly/total?label=Downloads)](https://github.com/RWTH-E3D/carbonfly/releases)&nbsp;
[![Release](https://img.shields.io/github/v/release/RWTH-E3D/carbonfly?label=Release&color=4c8eda)](https://github.com/RWTH-E3D/carbonfly/releases)
&nbsp;
[![Platforms](https://img.shields.io/badge/Platforms-Rhino_8_&_Grasshopper-4c8eda)](https://www.rhino3d.com/en/)&nbsp;
[![WSL](https://img.shields.io/badge/WSL_2_|_Ubuntu-7a6fac)](https://learn.microsoft.com/en-us/windows/wsl/install)&nbsp;
[![OpenFOAM](https://img.shields.io/badge/OpenFOAM_v10-7a6fac)](https://openfoam.org/version/10/)&nbsp;
[![License](https://img.shields.io/github/license/RWTH-E3D/carbonfly?color=888)](https://github.com/RWTH-E3D/carbonfly/blob/master/LICENSE)&nbsp;

A lightweight, easy-to-use Python API and toolbox for indoor CO2 CFD simulations in Grasshopper based on OpenFOAM and the Windows Subsystem for Linux (WSL).

## Quick Navigation

- [Key Features](#key-features)
- [Roadmap](#roadmap)
- [How to install?](#how-to-install)
- [Instructions for Developers](#instructions-for-developers)
- [License](#license)
- [How to cite](#how-to-cite)

## Key Features

1. **Indoor ventilation CFD**: Run steady-state and transient simulations of CO2 transport, airflow, and buoyancy-driven temperature.
2. **Rhino-to-CFD in "one click"**: Use Rhino/Grasshopper geometry. Carbonfly handles meshing and other setups - no OpenFOAM text files to edit.
3. **Plug-and-play boundaries**: Presets for inlets, outlets, and walls etc., with sensible defaults you can tweak.
4. **Fast what-if studies**: Change flow rate, supply temperature, CO2 concentration, and diffuser placement and quickly rerun for comparison.
5. **Visualization-ready outputs**: Exports a standard OpenFOAM case for viewing CO2/velocity/temperature/pressure etc. in ParaView.

## Roadmap

| Feature | Status | Implementation Details |
|-|-|-|
| Transient and steady-state CFD simulation of indoor CO2 / temperature / velocity etc. for mechanical ventilation | ✅ Done (v0.1.0) | Based on WSL 2 (Ubuntu-20.04) & OpenFOAM v10. Solver `buoyantReactingFoam` which supports multi-species with enhanced buoyancy treatment. The reaction is disabled and only the mixing, mainly driven by buoyancy, is considered.|
| Natural ventilation through open windows | ⏳ Planned | - |
| Manikins with different levels of detail | ⏳ Planned | - |

[Back to top ↥](#quick-navigation)

## How to install?

See [How to install](./HowToInstall.md)

## Instructions for Developers

Coming soon...

[Back to top ↥](#quick-navigation)

## License

Carbonfly is a free, open-source plugin licensed under [AGPL-3.0](./LICENSE).

There are several ways you can contribute:

- 🐞 Report bugs or issues you encounter
- 💡 Suggest improvements or new features
- 🔧 Submit pull requests to improve the code or documentation
- 📢 Share the plugin with others who may find it useful

Copyright (C) 2025 Qirui Huang, [Institute for Energy Efficiency and Sustainable Building (E3D), RWTH Aachen University](https://www.e3d.rwth-aachen.de/go/id/iyld/?lidx=1)


## How to cite

Coming soon...

[Back to top ↥](#quick-navigation)