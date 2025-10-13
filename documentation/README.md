# Carbonfly Toolbox Documentation

<!-- TOC -->
* [Carbonfly Toolbox Documentation](#carbonfly-toolbox-documentation)
  * [Grasshopper toolbox](#grasshopper-toolbox)
    * [01:Create](#01create)
      * [CreateCFCase](#createcfcase)
      * [CreateCFGeometry](#createcfgeometry)
<!-- TOC -->

## Grasshopper toolbox

### 01:Create

#### CreateCFCase

![CreateCFCase](_pics/GH_CreateCFCase.png)

| Inputs                                                                                 | Outputs                                  |
|----------------------------------------------------------------------------------------|------------------------------------------|
| `case_dir` *(str)*: OpenFOAM case root folder                                          | `log` *(str)*: Log                       |
| `case_name` *(str)*: Carbonfly case name                                               | `case_path` *(str)*: Carbonfly case path |
| `CF_geo` *(from `CreateCFGeometry`)*: List of Carbonfly Geometry objects               |                                          |
| `unit` *(str)*: "mm" (default), "cm", "m" → scaled to meters on export                 |                                          |
| `controlDict` *(from `controlDict`)*: Carbonfly controlDict                            |                                          |
| `fvSchemes_path` *(from `fvSchemes` or custom path (str))*: fvSchemes template path    |                                          |
| `fvSolution_path` *(from `fvSolution` or custom path (str))*: fvSolution template path |                                          |
| `residual` *(float)*: Residual control, e.g. 1e-5                                      |                                          |
| `insidePoint` *(Point3d)*: A reference point inside the mesh/room                      |                                          |
| `internalFields` *(from `internalFields`)*: Carbonfly internalFields                   |                                          |
| `run` *(bool)*: When True, create Carbonfly case                                       |                                          |


[Back to top ↥](#carbonfly-toolbox-documentation)

#### CreateCFGeometry

![CreateCFGeometry](_pics/GH_CreateCFGeometry.png)

| Inputs                                                                                          | Outputs                      |
|-------------------------------------------------------------------------------------------------|------------------------------|
| `name` *(str)*: Region/solid name for STL & regions{}                                           | `log` *(str)*: Log           |
| `geometry` *(GeometryBase)*: Single surface/face/brep or a collection                           | `CF_geo`: Carbonfly Geometry |
| `boundary` *(from `02:Boundary`)*: Carbonfly boundary                                           |                              |
| `refine_levels` *(Interval)*: Refine levels for meshing: (min, max) or as a single float number |                              |

[Back to top ↥](#carbonfly-toolbox-documentation)

[//]: # (### 02:Boundary)

[//]: # ()
[//]: # (#### Carbonfly Body)

[//]: # ()
[//]: # (![]&#40;&#41;)

[//]: # ()
[//]: # (| Inputs | Outputs |)

[//]: # (|--------|---------|)

[//]: # (|        |         |)

[//]: # (|        |         |)

[//]: # (|        |         |)

[//]: # (|        |         |)

[//]: # ()
[//]: # ([Back to top ↥]&#40;#carbonfly-toolbox-documentation&#41;)