# Carbonfly

![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/RWTH-E3D/carbonfly/total)&nbsp;
[![Release](https://img.shields.io/github/v/release/RWTH-E3D/carbonfly?label=Release&color=4c8eda)](https://github.com/RWTH-E3D/carbonfly/releases)&nbsp;
[![Platforms](https://img.shields.io/badge/Platforms-Rhino_8_&_Grasshopper-4c8eda)](https://www.rhino3d.com/en/)&nbsp;
[![WSL](https://img.shields.io/badge/Windows-10_&_11_|_with_WSL_2-7a6fac)](https://learn.microsoft.com/en-us/windows/wsl/install)&nbsp;
[![OpenFOAM](https://img.shields.io/badge/OpenFOAM-v10-7a6fac)](https://openfoam.org/version/10/)&nbsp;
[![License](https://img.shields.io/github/license/RWTH-E3D/carbonfly?color=888)](https://github.com/RWTH-E3D/carbonfly/blob/master/LICENSE)&nbsp;
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17117827.svg)](https://doi.org/10.5281/zenodo.17117827)&nbsp;

An easy-to-use Python library and Grasshopper toolbox for indoor CO2 CFD simulation, based on OpenFOAM and the Windows Subsystem for Linux (WSL).

<img src="./pics/carbonfly_logo.svg" width="10%" alt="Carbonfly Logo" />

## Quick Navigation

- [Key Features](#key-features)
- [Roadmap](#roadmap)
- [How to install?](#how-to-install)
- [Carbonfly Video Tutorials](#carbonfly-video-tutorials)
- [Examples](#examples)
- [Documentation](#documentation)
- [Instructions for Developers & FAQs](#instructions-for-developers--faqs)
- [License](#license)
- [How to cite](#how-to-cite)

## Key Features

1. **Indoor ventilation CFD**: Run steady-state and transient simulations of CO2 transport, airflow, and buoyancy-driven temperature.
2. **Rhino-to-CFD in "one click"**: Use Rhino/Grasshopper geometry. Carbonfly handles meshing and other setups - no OpenFOAM text files to edit.
3. **Plug-and-play boundaries**: Presets for inlets, outlets, natural ventilation, and dynamic respiration etc., with sensible defaults you can tweak.
4. **Fast what-if studies**: Change flow rate, supply temperature, CO2 concentration, and diffuser placement and quickly rerun for comparison.
5. **Visualization-ready outputs**: Exports a standard OpenFOAM case for viewing CO2 / velocity / temperature / pressure etc. in ParaView.
6. **In-Grasshopper post-processing & IAQ assessment**: Directly read OpenFOAM results inside Grasshopper for visualization and CO2-based Indoor Air Quality (IAQ) assessment based on different standards.

**Workflow overview:**

<img src="./pics/carbonfly_overview.gif" width="50%" alt="Carbonfly workflow overview" />

**Post-processing in ParaView:**

<img src="./examples/_pics/01a_simple_mech_vent_transient_ParaView.gif" width="50%" alt="Carbonfly post-processing in ParaView" />

**Post-processing in Grasshopper:**

<img src="./pics/carbonfly_postprocessing.gif" width="50%" alt="Carbonfly post-processing workflow" />

## Roadmap

<table style="width:100%">
  <tr>
    <th>Feature</th>
    <th>Status</th>
    <th>Implementation Details</th>
  </tr>
  <tr>
    <td>Transient and steady-state CFD simulation of indoor CO2 / temperature / velocity etc. for mechanical ventilation</td>
    <td>✅ Done (v0.1.0)</td>
    <td>Based on WSL 2 (Ubuntu-20.04) &amp; OpenFOAM v10. Solver <code>buoyantReactingFoam</code> which supports multi-species with enhanced buoyancy treatment. The reaction is disabled and only the mixing, mainly driven by buoyancy, is considered.</td>
  </tr>
  <tr>
    <td>Natural ventilation through open windows</td>
    <td>✅ Done (v0.3.0)</td>
    <td>
      See our <a href="./examples" alt="Examples" target="_blank">Examples</a>: 
      1) Transient: <code>Carbonfly Dynamic Window</code> based on <code>pressureInletOutletVelocity</code>;
      2) Steady-state: simplified split window (top/bottom);
      3) Bounding box (indoor + outdoor).
    </td>
  </tr>
  <tr>
    <td rowspan="2">Manikins with different Levels of Detail (LOD)</td>
    <td>✅ Done (v0.2.0)</td>
    <td>LOD0 Manikin is a simplified human model focused on CO2 dispersion. It is represented by straight lines and basic geometric volumes, without body part subdivision. Breathing is simplified to mouth breathing only, with no nasal passage. This abstraction is well suited for multi-occupant scenarios where reduced CFD mesh size and computational cost are essential.</td>
  </tr>
  <tr>
    <td>⏳ Planned</td>
    <td>LOD1/2/...</td>
  </tr>
  <tr>
    <td rowspan="2">Thermal comfort models</td>
    <td>✅ Done (v0.4.0)</td>
    <td>Gagge two-node model for standing, sitting, and sleeping positions (based on <a href="https://github.com/CenterForTheBuiltEnvironment/pythermalcomfort" alt="pythermalcomfort link">pythermalcomfort</a>)</td>
  </tr>
  <tr>
    <td>⏳ Planned</td>
    <td>Support more models</td>
  </tr>
  <tr>
    <td>Dynamic respiration</td>
    <td>✅ Done (v0.5.0)</td>
    <td>Time-varying mouth boundary for <code>U</code> via <code>codedFixedValue</code> (sine). Parameterized by breathing frequency and average breathing flow rate (L/min). Amplitude is computed from target ventilation and patch area.
    </td>
  </tr>
  <tr>
    <td>Recirculated supply & return</td>
    <td>✅ Done (v0.6.0)</td>
    <td>Paired boundaries for internal (no-fresh-air) air recirculation, applicable to various devices, e.g., split AC indoor units for heating or cooling without fresh air input. The CO2 concentration of the supply air is equal to that of the return air (dynamic).
    </td>
  </tr>
  <tr>
    <td rowspan="3">Post-processing</td>
    <td>✅ Done (v0.8.0)</td>
    <td>Perform analysis and visualization directly in Grasshopper instead of ParaView. See our <a href="./examples" alt="Examples" target="_blank">Examples</a>.</td>
  </tr>
  <tr>
    <td>✅ Done (v0.8.0)</td>
    <td>Indoor Air Quality (IAQ) assessment based on international/national standards. If you know of other CO2-based IAQ standards, please leave a comment in our <a href="https://github.com/RWTH-E3D/carbonfly/discussions/5" alt="discussion board IAQ standards link">discussion board</a>.</td>
  </tr>
  <tr>
    <td>⏳ Planned</td>
    <td>Integration with multi-objective optimization workflow.</td>
  </tr>
</table>

[Back to top ↥](#quick-navigation)

## How to install?

See [How to Install & Update & Uninstall](./HowToInstall.md)

## Carbonfly Video Tutorials

[Carbonfly Tutorial Series (YouTube)](https://www.youtube.com/watch?v=2cnaCHx_9OI&list=PLdKdhraP5SXNjJ81d2iK5UM4sPhSs7X5r)

## Examples

See [Examples](./examples)

## Documentation

See [Documentation](./documentation)

## Instructions for Developers & FAQs

See [Instructions for Developers & FAQs](./InstructionsForDevelopers.md)

## License

Carbonfly is a free, open-source plugin licensed under [LGPL-3.0](./LICENSE).

There are several ways you can contribute:

- 🐞 Report bugs or issues you encounter
- 💡 Suggest improvements or new features
- 🔧 Submit pull requests to improve the code or documentation
- 📢 Share the plugin with others who may find it useful

Copyright (C) 2025 Qirui Huang, [Institute of Energy Efficiency and Sustainable Building (E3D), RWTH Aachen University](https://www.e3d.rwth-aachen.de/go/id/iyld/?lidx=1)

[Back to top ↥](#quick-navigation)

## How to cite

If you want to cite **Carbonfly** in your academic work, there are two ways to do it:

- Each release is archived on [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17117827.svg)](https://doi.org/10.5281/zenodo.17117827). Please either cite the version you used as indexed at Zenodo (for reproducibility) or cite all versions.

  **Examples:**

  BibTeX:

  ```bibtex
  @software{Carbonfly_Huang,
    author    = {Qirui Huang},
    title     = {Carbonfly},
    subtitle  = {An easy-to-use Python library and Grasshopper toolbox for indoor CO2 CFD simulation},
    date      = {2025},
    publisher = {Zenodo},
    url       = {https://github.com/RWTH-E3D/carbonfly},
    note      = {GitHub repository},
    doi       = {10.5281/zenodo.17117827}
  }
  ```

  APA style:
  ```
  Huang, Q. (2025). Carbonfly: An easy-to-use Python library and Grasshopper toolbox for indoor CO2 CFD simulation [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.17117827
  ```

- If you wish to cite **Carbonfly** for its design, methodology, etc. (rather than a specific release), please cite our paper:

  Coming soon...

[Back to top ↥](#quick-navigation)
