# Carbonfly Toolbox Documentation

<!-- TOC -->
* [Carbonfly Toolbox Documentation](#carbonfly-toolbox-documentation)
  * [Grasshopper toolbox](#grasshopper-toolbox)
    * [01:Create](#01create)
      * [CreateCFCase](#createcfcase)
      * [CreateCFGeometry](#createcfgeometry)
    * [02:Boundary](#02boundary)
      * [Body](#body)
      * [Dynamic Respiration](#dynamic-respiration)
      * [Dynamic Window](#dynamic-window)
      * [InletVelocity](#inletvelocity)
      * [internalFields](#internalfields)
      * [Outlet](#outlet)
      * [RecircReturn](#recircreturn)
      * [RecircSupply](#recircsupply)
      * [Wall](#wall)
    * [03:Recipe](#03recipe)
      * [controlDict](#controldict)
      * [fvSchemes](#fvschemes)
      * [fvSolution](#fvsolution)
      * [Residual Control List](#residual-control-list)
    * [04:Solution](#04solution)
      * [blockMesh](#blockmesh)
      * [runFoam](#runfoam)
      * [snappyHexMesh](#snappyhexmesh)
      * [surfaceFeatures](#surfacefeatures)
      * [checkMesh](#checkmesh)
      * [foamMonitor](#foammonitor)
    * [05:Util](#05util)
      * [BSA (Du Bois)](#bsa-du-bois)
      * [CO2 generation rate](#co2-generation-rate)
      * [Gagge two-node model](#gagge-two-node-model)
      * [Gagge two-node model (sleep)](#gagge-two-node-model-sleep)
      * [Manikin LOD 0](#manikin-lod-0)
      * [Met List](#met-list)
<!-- TOC -->

## Grasshopper toolbox

### 01:Create

#### CreateCFCase

<img src="../grasshopper/icons/CreateCFCase.png" alt="icon" width="60"/>

Create Carbonfly case

![CreateCFCase](_pics/GH_CreateCFCase.png)

| Inputs                                                                                                     | Outputs                                  |
|------------------------------------------------------------------------------------------------------------|------------------------------------------|
| `case_dir` *(str)*: OpenFOAM case root folder                                                              | `log` *(str)*: Log                       |
| `case_name` *(str)*: Carbonfly case name                                                                   | `case_path` *(str)*: Carbonfly case path |
| `CF_geo` *(from [CreateCFGeometry](#createcfgeometry))*: List of Carbonfly Geometry objects                |                                          |
| `unit` *(str)*: "mm" (default), "cm", "m", unit setting in Rhino -> STL will be scaled to meters on export |                                          |
| `controlDict` *(from [controlDict](#controldict))*: Carbonfly controlDict                                  |                                          |
| `fvSchemes_path` *(from [fvSchemes](#fvschemes) or custom path (str))*: fvSchemes template path            |                                          |
| `fvSolution_path` *(from [fvSolution](#fvsolution) or custom path (str))*: fvSolution template path        |                                          |
| `residual` *(float)*: Residual control, e.g. 1e-5                                                          |                                          |
| `insidePoint` *(Point3d)*: A reference point inside the mesh/room                                          |                                          |
| `internalFields` *(from [internalFields](#internalfields))*: Carbonfly internalFields                      |                                          |
| `run` *(bool)*: When True, create Carbonfly case                                                           |                                          |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### CreateCFGeometry

<img src="../grasshopper/icons/CreateCFGeometry.png" alt="icon" width="60"/>

Create Carbonfly geometry

![CreateCFGeometry](_pics/GH_CreateCFGeometry.png)

| Inputs                                                                                          | Outputs                      |
|-------------------------------------------------------------------------------------------------|------------------------------|
| `name` *(str)*: Region/solid name for STL & regions{}                                           | `log` *(str)*: Log           |
| `geometry` *(GeometryBase)*: Single surface/face/brep or a collection                           | `CF_geo`: Carbonfly Geometry |
| `boundary` *(from [02:Boundary](#02boundary))*: Carbonfly boundary                              |                              |
| `refine_levels` *(Interval)*: Refine levels for meshing: (min, max) or as a single float number |                              |

[Back to top ↥](#carbonfly-toolbox-documentation)

### 02:Boundary

#### Body

<img src="../grasshopper/icons/Body.png" alt="icon" width="60"/>

Manikin body boundary

![Body](_pics/GH_Carbonfly_Body.png)

| Inputs                                         | Outputs                             |
|------------------------------------------------|-------------------------------------|
| `temperature` *(float)*: Skin temperature in K | `boundary`: Carbonfly Body boundary |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Dynamic Respiration

<img src="../grasshopper/icons/DynamicRespiration.png" alt="icon" width="60"/>

Dynamic respiration boundary condition for transient simulation

![Dynamic Respiration](_pics/GH_Carbonfly_DynamicRespiration.png)

| Inputs                                                                                    | Outputs                                            |
|-------------------------------------------------------------------------------------------|----------------------------------------------------|
| `freq` *(float)*: breaths per minute, default: 12 breaths per minute (0.2 Hz)             | `boundary`: Carbonfly Dynamic Respiration boundary |
| `breathing_flow_rate` *(float)*: Average breathing flow rate in L/min, default: 7.2 L/min |                                                    |
| `temperature` *(float)*: Core temperature in K                                            |                                                    |
| `CO2` *(float)*: Exhaled $\rm CO_2$ as volume fraction (e.g., 0.000450 for 450 ppm)       |                                                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Dynamic Window

<img src="../grasshopper/icons/DynamicWindow.png" alt="icon" width="60"/>

Dynamic pressure-driven window boundary condition for transient simulation with natural ventilation

![Dynamic Window](_pics/GH_Carbonfly_DynamicWindow.png)

| Inputs                                                                                                                                         | Outputs                                       |
|------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| `velocity` *(Vector3d)*: Velocity (m/s) as a vector, e.g. (0, 0, -1), for initialization. Not enforced during solve (dynamic, pressure-driven) | `boundary`: Carbonfly Dynamic Window boundary |
| `temperature` *(float)*: Outdoor temperature in K                                                                                              |                                               |
| `CO2` *(float)*: Outdoor $\rm CO_2$ concentration as volume fraction (e.g., 0.000450 for 450 ppm)                                                     |                                               |
| `pressure` *(float)*: Outdoor air pressure in Pa                                                                                               |                                               |


[Back to top ↥](#carbonfly-toolbox-documentation)

#### InletVelocity

<img src="../grasshopper/icons/InletVelocity.png" alt="icon" width="60"/>

Static air inlet boundary, e.g. for mechanical ventilation

![InletVelocity](_pics/GH_Carbonfly_InletVelocity.png)

| Inputs                                                                     | Outputs                                      |
|----------------------------------------------------------------------------|----------------------------------------------|
| `velocity` *(Vector3d)*: Inlet velocity (m/s) as a vector, e.g. (0, 0, -1) | `boundary`: Carbonfly InletVelocity boundary |
| `temperature` *(float)*: Inlet temperature in K (e.g. 293.15)              |                                              |
| `CO2` *(float)*: Inlet CO₂ as volume fraction (e.g., 0.000450 for 450 ppm) |                                              |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### internalFields

<img src="../grasshopper/icons/internalFields.png" alt="icon" width="60"/>

Initial internal field definitions for the simulation domain

![internalFields](_pics/GH_Carbonfly_internalFields.png)

| Inputs                                                                                                          | Outputs                                    |
|-----------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| `U_internal` *(Vector3d)*: internalFields for velocity (U) in m/s                                               | `log` *(str)*: Log                         |
| `T_internal` *(float)*: internalFields for air temperature in K                                                 | `internalFields`: Carbonfly internalFields |
| `CO2_internal` *(float)*: internalFields for $\rm CO_2$ concentration, as volume fraction (e.g., 0.000450 for 450 ppm) |                                            |
| `p_internal` *(float)*: internalFields for pressure in Pa                                                       |                                            |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Outlet

<img src="../grasshopper/icons/Outlet.png" alt="icon" width="60"/>

Outlet boundary (zeroGradient)

![Outlet](_pics/GH_Carbonfly_Outlet.png)

| Inputs | Outputs                               |
|--------|---------------------------------------|
|        | `boundary`: Carbonfly Outlet boundary |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### RecircReturn

<img src="../grasshopper/icons/RecircReturn.png" alt="icon" width="60"/>

Recirculated return from the room. Pair with RecircSupply.

![RecircReturn](_pics/GH_Carbonfly_RecircReturn.png)

| Inputs                                                                      | Outputs                                     |
|-----------------------------------------------------------------------------|---------------------------------------------|
| `velocity` *(Vector3d)*: Return velocity (m/s) as a vector, e.g. (0, 0, -1) | `boundary`: Carbonfly RecircReturn boundary |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### RecircSupply

<img src="../grasshopper/icons/RecircSupply.png" alt="icon" width="60"/>

Recirculated supply to the room. $\rm CO_2$ can mirror the Return average to model no-fresh-air recirculation. Pair with RecircReturn.

![RecircSupply](_pics/GH_Carbonfly_RecircSupply.png)

| Inputs                                                                      | Outputs                                     |
|-----------------------------------------------------------------------------|---------------------------------------------|
| `velocity` *(Vector3d)*: Supply velocity (m/s) as a vector, e.g. (0, 0, -1) | `boundary`: Carbonfly RecircSupply boundary |
| `temperature` *(float)*: Supply temperature in K (e.g. 293.15)              |                                             |
| `return_name` *(str)*: Region/solid name of Recirculation Return            |                                             |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Wall

<img src="../grasshopper/icons/Wall.png" alt="icon" width="60"/>

Fixed isothermal solid wall boundary condition

![Wall](_pics/GH_Carbonfly_Wall.png)

| Inputs                                                          | Outputs                             |
|-----------------------------------------------------------------|-------------------------------------|
| `temperature` *(float)*: Surface temperature in K (e.g. 293.15) | `boundary`: Carbonfly Wall boundary |

[Back to top ↥](#carbonfly-toolbox-documentation)

### 03:Recipe

#### controlDict

<img src="../grasshopper/icons/controlDict.png" alt="icon" width="60"/>

OpenFOAM controlDict settings

![controlDict](_pics/GH_Carbonfly_controlDict.png)

| Inputs                                                                                                | Outputs                              |
|-------------------------------------------------------------------------------------------------------|--------------------------------------|
| `mode` *(str)*: Simulation mode: transient or steady-state (or steady / steadystate)                  | `log` *(str)*: Log                   |
| `writeInterval` *(float)*: Results write interval, in seconds (transient) / iterations (steady-state) | `controlDict`: Carbonfly controlDict |
| `endTime` *(float)*: Simulation end time, in seconds (transient) / iterations (steady-state)          |                                      |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### fvSchemes

<img src="../grasshopper/icons/fvSchemes.png" alt="icon" width="60"/>

OpenFOAM fvSchemes settings

![fvSchemes](_pics/GH_Carbonfly_fvSchemes.png)

| Inputs                                                                               | Outputs                                           |
|--------------------------------------------------------------------------------------|---------------------------------------------------|
| `mode` *(str)*: Simulation mode: transient or steady-state (or steady / steadystate) | `fvSchemes_path` *(str)*: fvSchemes template path |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### fvSolution

<img src="../grasshopper/icons/fvSolution.png" alt="icon" width="60"/>

OpenFOAM fvSolution settings

![fvSolution](_pics/GH_Carbonfly_fvSolution.png)

| Inputs                                                                               | Outputs                                             |
|--------------------------------------------------------------------------------------|-----------------------------------------------------|
| `mode` *(str)*: Simulation mode: transient or steady-state (or steady / steadystate) | `fvSolution_path` *(str)*: fvSolution template path |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Residual Control List

A preset list for residual control

![Residual Control List](_pics/GH_Carbonfly_Residual_Control_List.png)

[Back to top ↥](#carbonfly-toolbox-documentation)

### 04:Solution

#### blockMesh

<img src="../grasshopper/icons/blockMesh.png" alt="icon" width="60"/>

Run *blockMesh*, creates a simple background mesh from block definitions

![blockMesh](_pics/GH_Carbonfly_blockMesh.png)

| Inputs                                                                                                                                                                                      | Outputs            |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `case_path` *(from [createCFCase](#createcfcase) or custom path (str))*: Carbonfly case path                                                                                                | `log` *(str)*: Log |
| `distro` *(str)*: Name of the WSL distribution/profile to run the command in (e.g., "Ubuntu-20.04"); leave blank to use your default WSL                                                    |                    |
| `foam_bashrc` *(str)*: Path to the OpenFOAM bashrc file to source before running the command (e.g., “/opt/openfoam10/etc/bashrc”); leave blank to skip sourcing/use the current environment |                    |
| `run` *(bool)*: When True, run blockMesh                                                                                                                                                    |                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### runFoam

<img src="../grasshopper/icons/runFoam.png" alt="icon" width="60"/>

Run OpenFOAM solver (*buoyantReactingFoam*) for simulation

![runFoam](_pics/GH_Carbonfly_runFoam.png)

| Inputs                                                                                                                                                                                      | Outputs            |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `case_path` *(from [createCFCase](#createcfcase) or custom path (str))*: Carbonfly case path                                                                                                | `log` *(str)*: Log |
| `distro` *(str)*: Name of the WSL distribution/profile to run the command in (e.g., "Ubuntu-20.04"); leave blank to use your default WSL                                                    |                    |
| `foam_bashrc` *(str)*: Path to the OpenFOAM bashrc file to source before running the command (e.g., “/opt/openfoam10/etc/bashrc”); leave blank to skip sourcing/use the current environment |                    |
| `run` *(bool)*: When True, run OpenFOAM solver                                                                                                                                              |                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### snappyHexMesh

<img src="../grasshopper/icons/snappyHexMesh.png" alt="icon" width="60"/>

Run *snappyHexMesh*, generates a body-fitted mesh around geometry by refining and snapping cells.

![snappyHexMesh](_pics/GH_Carbonfly_snappyHexMesh.png)

| Inputs                                                                                                                                                                                      | Outputs            |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `case_path` *(from [createCFCase](#createcfcase) or custom path (str))*: Carbonfly case path                                                                                                | `log` *(str)*: Log |
| `distro` *(str)*: Name of the WSL distribution/profile to run the command in (e.g., "Ubuntu-20.04"); leave blank to use your default WSL                                                    |                    |
| `foam_bashrc` *(str)*: Path to the OpenFOAM bashrc file to source before running the command (e.g., “/opt/openfoam10/etc/bashrc”); leave blank to skip sourcing/use the current environment |                    |
| `run` *(bool)*: When True, run *snappyHexMesh*                                                                                                                                              |                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### surfaceFeatures

<img src="../grasshopper/icons/surfaceFeatures.png" alt="icon" width="60"/>

Run *surfaceFeatures*, extracts sharp edges/features from surface geometry.

![surfaceFeatures](_pics/GH_Carbonfly_surfaceFeatures.png)

| Inputs                                                                                                                                                                                      | Outputs            |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `case_path` *(from [createCFCase](#createcfcase) or custom path (str))*: Carbonfly case path                                                                                                | `log` *(str)*: Log |
| `distro` *(str)*: Name of the WSL distribution/profile to run the command in (e.g., "Ubuntu-20.04"); leave blank to use your default WSL                                                    |                    |
| `foam_bashrc` *(str)*: Path to the OpenFOAM bashrc file to source before running the command (e.g., “/opt/openfoam10/etc/bashrc”); leave blank to skip sourcing/use the current environment |                    |
| `includedAngleDeg` *(float)*: includedAngleDeg for surfaceFeatures, default: 150                                                                                                            |                    |
| `run` *(bool)*: When True, run *surfaceFeatures*                                                                                                                                            |                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### checkMesh

<img src="../grasshopper/icons/checkMesh.png" alt="icon" width="60"/>

Run *checkMesh*, checks mesh quality (non-orthogonality, skewness, aspect ratio, etc.).

![checkMesh](_pics/GH_Carbonfly_checkMesh.png)

| Inputs                                                                                                                                                                                      | Outputs            |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `case_path` *(from [createCFCase](#createcfcase) or custom path (str))*: Carbonfly case path                                                                                                | `log` *(str)*: Log |
| `distro` *(str)*: Name of the WSL distribution/profile to run the command in (e.g., "Ubuntu-20.04"); leave blank to use your default WSL                                                    |                    |
| `foam_bashrc` *(str)*: Path to the OpenFOAM bashrc file to source before running the command (e.g., “/opt/openfoam10/etc/bashrc”); leave blank to skip sourcing/use the current environment |                    |
| `run` *(bool)*: When True, run *checkMesh*                                                                                                                                                  |                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### foamMonitor

<img src="../grasshopper/icons/foamMonitor.png" alt="icon" width="60"/>

Run *foamMonitor*, live monitoring tool to track residuals during simulation.

![foamMonitor](_pics/GH_Carbonfly_foamMonitor.png)

| Inputs                                                                                                                                                                                      | Outputs            |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `case_path` *(from [createCFCase](#createcfcase) or custom path (str))*: Carbonfly case path                                                                                                | `log` *(str)*: Log |
| `distro` *(str)*: Name of the WSL distribution/profile to run the command in (e.g., "Ubuntu-20.04"); leave blank to use your default WSL                                                    |                    |
| `foam_bashrc` *(str)*: Path to the OpenFOAM bashrc file to source before running the command (e.g., “/opt/openfoam10/etc/bashrc”); leave blank to skip sourcing/use the current environment |                    |
| `start_time` *(float)*: Monitor residuals from time/iteration {start_time}, default: 0                                                                                                      |                    |
| `run` *(bool)*: When True, run *foamMonitor*                                                                                                                                                |                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

### 05:Util

#### BSA (Du Bois)

<img src="../grasshopper/icons/BSA_Du_Bois.png" alt="icon" width="60"/>

Calculate Body Surface Area (BSA) using Du Bois' Formula:

$\rm BSA (m^2)  = 0.007184 \cdot Height (cm)^{0.725} \cdot Weight (kg)^{0.425}$

> Source: D. Du Bois, CLINICAL CALORIMETRY: TENTH PAPER A FORMULA TO ESTIMATE THE APPROXIMATE SURFACE AREA IF HEIGHT AND WEIGHT BE KNOWN, Archives of Internal Medicine XVII (6_2) (1916) 863. doi:10.1001/archinte.1916.00080130010002

![BSA (Du Bois)](_pics/GH_BSA_Du_Bois.png)

| Inputs                           | Outputs                                         |
|----------------------------------|-------------------------------------------------|
| `height` *(float)*: Height in cm | `BSA` *(float)*: Body Surface Area in $\rm m^2$ |
| `weight` *(float)*: Weight in kg |                                                 |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### CO2 generation rate

<img src="../grasshopper/icons/CO2_Generation_Rate.png" alt="icon" width="60"/>

Get $\rm CO_2$ generation rate (L/s) based on mean body mass in each age group.

> Source: Persily and De Jonge, Carbon dioxide generation rates for building occupants, Indoor Air 27 (5) (2017) 868–879. doi:10.1111/ina.12383

![CO2 generation rate](_pics/GH_CO2_generation_rate.png)

| Inputs                                                                                                    | Outputs                                                                                           |
|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `age` *(float)*: Age, between 0-100                                                                       | `mass` *(float)*: mean body mass (kg)                                                             |
| `met` *(float)*: Level of physical activity (met), met must be one of [1.0, 1.2, 1.4, 1.6, 2.0, 3.0, 4.0] | `BMR` *(float)*: Basal Metabolic Rate (MJ/day)                                                    |
| `gender` *(str)*: "male", "female", None (default returns average for both genders)                       | `CO2_Ls` *(float)*: $\rm CO_2$ generation rate (L/s)                                              |
| `breathing_flow_rate` *(float)*: Average breathing flow rate in L/min, default: 7.2 L/min                 | `CO2_ppm` *(float)*: Exhaled $\rm CO_2$ concentration (ppm)                                       |
|                                                                                                           | `CO2` *(float)*: Exhaled $\rm CO_2$ concentration as volume fraction (e.g., 0.000450 for 450 ppm) |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Gagge two-node model

<img src="../grasshopper/icons/ThermalComfort_Gagge_TwoNode.png" alt="icon" width="60"/>

Gagge Two-node model of human temperature regulation Gagge et al. (1986).

> Source: Gagge, A.P., Fobelets, A.P., and Berglund, L.G., 1986. A standard predictive Index of human reponse to thermal enviroment. Am. Soc. Heating, Refrig. Air-Conditioning Eng. 709–731.

![Gagge two-node model](_pics/GH_Gagge_two-node_model.png)

| Inputs                                                                                                    | Outputs                                                                                                                                                                                                                                                                                                       |
|-----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `tdb` *(float)*: Dry bulb air temperature in °C                                                           | `e_skin` *(float)*: Total rate of evaporative heat loss from skin in W/m2. Equal to e_rsw + e_diff                                                                                                                                                                                                            |
| `tr` *(float): Mean radiant temperature in °C                                                             | `e_rsw` *(float)*: Rate of evaporative heat loss from sweat evaporation in W/m2                                                                                                                                                                                                                               |
| `v` *(float)*: Air speed in m/s                                                                           | `e_max` *(float)*: Maximum rate of evaporative heat loss from skin in W/m2                                                                                                                                                                                                                                    |
| `rh` *(float)*: Relative humidity in %                                                                    | `q_sensible` *(float)*: Sensible heat loss from skin in W/m2                                                                                                                                                                                                                                                  |
| `met` *(float)*: Metabolic rate in met                                                                    | `q_skin` *(float)*: Total rate of heat loss from skin in W/m2. Equal to q_sensible + e_skin                                                                                                                                                                                                                   |
| `clo` *(float)*: Clothing insulation in clo                                                               | `q_res` *(float)*: Total rate of heat loss through respiration in W/m2                                                                                                                                                                                                                                        |
| `wme` *(float)*: External work in met. Defaults to 0                                                      | `t_core` *(float)*: Core temperature in °C                                                                                                                                                                                                                                                                    |
| `BSA` *(float)*: Body surface area, default value 1.8258 $\rm m^2$                                        | `t_skin` *(float)*: Skin temperature in °C                                                                                                                                                                                                                                                                    |
| `p_atm` *(float)*: Atmospheric pressure in Pa, default value 101325 Pa                                    | `m_bl` *(float)*: Skin blood flow in kg/h/m2                                                                                                                                                                                                                                                                  |
| `position` *(str)*: Select either "sitting" or "standing". Defaults to "standing"                         | `m_rsw` *(float)*: Rate at which regulatory sweat is generated in mL/h/m2                                                                                                                                                                                                                                     |
| `max_skin_blood_flow` *(float)*: Maximum blood flow from the core to the skin in kg/h/m2. Defaults to 90  | `w` *(float)*: Skin wettedness, adimensional. Ranges from 0 to 1                                                                                                                                                                                                                                              |
| `max_sweating` *(float)*: Maximum rate at which regulatory sweat is generated in kg/h/m2. Defaults to 500 | `w_max` *(float)*: Skin wettedness (w) practical upper limit, adimensional. Ranges from 0 to 1                                                                                                                                                                                                                |
| `w_max` *(float)*: Maximum skin wettedness (w) adimensional. Ranges from 0 and 1. Defaults to False       | `SET` *(float)*: Standard Effective Temperature (SET)                                                                                                                                                                                                                                                         |
|                                                                                                           | `ET` *(float)*: New Effective Temperature (ET)                                                                                                                                                                                                                                                                |
|                                                                                                           | `pmv_gagge` *(float)*: Gagge's version of Fanger's Predicted Mean Vote (PMV)                                                                                                                                                                                                                                  |
|                                                                                                           | `pmv_set` *(float)*: PMV SET                                                                                                                                                                                                                                                                                  |
|                                                                                                           | `disc` *(float)*: Thermal discomfort (DISC). DISC is described numerically as: comfortable and pleasant (0), slightly uncomfortable but acceptable (1), uncomfortable and unpleasant (2), very uncomfortable (3), limited tolerance (4), and intolerable (5). The range of each category is ± 0.5 numerically |
|                                                                                                           | `t_sens` *(float)*: Predicted Thermal Sensation                                                                                                                                                                                                                                                               |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Gagge two-node model (sleep)

<img src="../grasshopper/icons/ThermalComfort_Gagge_TwoNode_Sleep.png" alt="icon" width="60"/>

Adaption of the Gagge two-node model for sleep thermal environment, by Yan et al.

> Source: Yan, S., Xiong, J., Kim, J. & de Dear, R. (2022). Adapting the two-node model to evaluate sleeping thermal environments. Building and Environment. 222, 109417. DOI: doi.org/10.1016/j.buildenv.2022.109417

![Gagge two-node model (sleep)](_pics/GH_Gagge_two-node_model_sleep.png)

| Inputs                                                                                              | Outputs                                                                                                                                                                                                                                                                                                       |
|-----------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `tdb` *(float)*: Dry bulb air temperature in °C                                                     | `e_skin` *(float)*: Total rate of evaporative heat loss from skin in W/m2. Equal to e_rsw + e_diff                                                                                                                                                                                                            |
| `tr` *(float): Mean radiant temperature in °C                                                       | `t_core` *(float)*: Core temperature in °C                                                                                                                                                                                                                                                                    |
| `v` *(float)*: Air speed in m/s                                                                     | `t_skin` *(float)*: Skin temperature in °C                                                                                                                                                                                                                                                                    |
| `rh` *(float)*: Relative humidity in %                                                              | `skin_blood_flow` *(float)*: Skin blood flow in kg/h/m2                                                                                                                                                                                                                                                       |
| `clo` *(float)*: Clothing insulation in clo                                                         | `w` *(float)*: Skin wettedness, adimensional. Ranges from 0 to 1                                                                                                                                                                                                                                              |
| `thickness_quilt` *(float)*: Thickness of the quilt in cm                                           | `SET` *(float)*: Standard Effective Temperature (SET)                                                                                                                                                                                                                                                         |
| `wme` *(float)*: External work in met. Defaults to 0                                                | `disc` *(float)*: Thermal discomfort (DISC). DISC is described numerically as: comfortable and pleasant (0), slightly uncomfortable but acceptable (1), uncomfortable and unpleasant (2), very uncomfortable (3), limited tolerance (4), and intolerable (5). The range of each category is ± 0.5 numerically |
| `p_atm` *(float)*: Atmospheric pressure in Pa, default value 101325 Pa                              | `t_sens` *(float)*: Predicted Thermal Sensation                                                                                                                                                                                                                                                               |
| `height` *(float)*: Height of the person in cm. Defaults to 171                                     | `met_shivering` *(float)*: Metabolic rate due to shivering in W/m2                                                                                                                                                                                                                                            |
| `weight` *(float)*: Weight of the person in kg. Defaults to 70                                      | `alfa` *(float)*: Dynamic fraction of total body mass assigned to the skin node (dimensionless)                                                                                                                                                                                                               |
| `c_sw` *(float)*: Driving coefficient for regulatory sweating. Defaults to 170                      |                                                                                                                                                                                                                                                                                                               |
| `c_dil` *(float)*: Driving coefficient for vasodilation. Defaults to 120                            |                                                                                                                                                                                                                                                                                                               |
| `c_str` *(float)*: Driving coefficient for vasoconstriction. Defaults to 0.5                        |                                                                                                                                                                                                                                                                                                               |
| `temp_skin_neutral` *(float)*: Skin temperature at neutral conditions in °C. Defaults to 33.7       |                                                                                                                                                                                                                                                                                                               |
| `temp_core_neutral` *(float)*: Core temperature at neutral conditions in °C. Defaults to 36.8       |                                                                                                                                                                                                                                                                                                               |
| `e_skin` *(float)*: Total evaporative heat loss in W. Defaults to 0.094                             |                                                                                                                                                                                                                                                                                                               |
| `alfa` *(float)*: Dynamic fraction of total body mass assigned to the skin node. Defaults to 0.1    |                                                                                                                                                                                                                                                                                                               |
| `skin_blood_flow` *(float)*: Skin-blood-flow rate per unit surface area in kg/h/m2. Defaults to 6.3 |                                                                                                                                                                                                                                                                                                               |
| `met_shivering` *(float)*: Metabolic rate due to shivering in met. Defaults to 0                    |                                                                                                                                                                                                                                                                                                               |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Manikin LOD 0

<img src="../grasshopper/icons/Body_LOD0.png" alt="icon" width="60"/>

Create a manikin with Level of Detail of 0.

![Manikin LOD 0](_pics/GH_Manikin_LOD_0.png)

| Inputs                                                                                                                   | Outputs                                                                                 |
|--------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| `Base Point` *(Point3d)*: Location base/reference point of the manikin model                                             | `Body Surface Area` *(float)*: Body Surface Area in $\rm m^2$                           |
| `unit` *(str)*: "mm" (default), "cm", "m", unit setting in Rhino                                                         | `Body` *(Surface)*: Collection of manikin body surfaces                                 |
| `width` *(float)*: Width of the manikin model                                                                            | `Mouth` *(Surface)*: Collection of manikin mouth surfaces                               |
| `height` *(float)*: Height of the manikin model                                                                          | `Breathing_U` *(float)*: Breathing velocity (for simplified constant exhalation) in m/s |
| `StV_height` *(float)*: Stomion (mouth) to vertex height, default: 17 cm *                                               |                                                                                         |
| `activity` *(str)*: The level of activity: "light" (default) / "medium" / "heavy", affects the size of the mouth opening |                                                                                         |
| `breathing_flow_rate` *(float)*: Average breathing flow rate in L/min, default: 7.2 L/min                                |                                                                                         |
| `mouth_scaling` *(float)*: Mouth opening scaling factor: 1 - 5, default: 4 **                                            |                                                                                         |
| `angle` *(float)*: Rotation angle in radians of the manikin model                                                        |                                                                                         |

> *For reference: 1) Adult: ~16-17 cm (females) / ~17-18 cm (males); 2) Children (6–12 years): ~12-15 cm
> 
> **A larger scale factor increases the mouth's opening area, reducing velocity while maintaining flow rate, thereby simplifying the mesh.

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Met List

A preset list for Metabolic rate in met.

![Met List](_pics/GH_Carbonfly_Met_List.png)

[Back to top ↥](#carbonfly-toolbox-documentation)