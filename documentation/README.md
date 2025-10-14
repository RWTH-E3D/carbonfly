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
| `CO2` *(float)*: Exhaled CO2 as volume fraction (e.g., 0.000450 for 450 ppm)              |                                                    |

[Back to top ↥](#carbonfly-toolbox-documentation)

#### Dynamic Window

<img src="../grasshopper/icons/DynamicWindow.png" alt="icon" width="60"/>
Dynamic pressure-driven window boundary condition for transient simulation with natural ventilation

![Dynamic Window](_pics/GH_Carbonfly_DynamicWindow.png)

| Inputs                                                                                                                                         | Outputs                                       |
|------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| `velocity` *(Vector3d)*: Velocity (m/s) as a vector, e.g. (0, 0, -1), for initialization. Not enforced during solve (dynamic, pressure-driven) | `boundary`: Carbonfly Dynamic Window boundary |
| `temperature` *(float)*: Outdoor temperature in K                                                                                              |                                               |
| `CO2` *(float)*: Outdoor CO2 concentration as volume fraction (e.g., 0.000450 for 450 ppm)                                                     |                                               |
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
| `CO2_internal` *(float)*: internalFields for CO2 concentration, as volume fraction (e.g., 0.000450 for 450 ppm) |                                            |
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
Recirculated supply to the room. CO2 can mirror the Return average to model no-fresh-air recirculation. Pair with RecircReturn.

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

#### fvSchemes

#### fvSolution

#### Residual Control List

### 04:Solution

#### blockMesh

#### runFoam

#### snappyHexMesh

#### surfaceFeatures

#### checkMesh

#### foamMonitor

### 05:Util

#### BSA (Du Bois)

#### CO2 generation rate

#### Gagge two-node model

#### Gagge two-node model (sleep)

#### Manikin LOD 0

#### Met List

![]()

| Inputs | Outputs |
|--------|---------|
|        |         |
|        |         |
|        |         |
|        |         |

[Back to top ↥](#carbonfly-toolbox-documentation)