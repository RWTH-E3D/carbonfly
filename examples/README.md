# Examples

Below is a collection of examples with descriptions to help you get started quickly.

## Quick Navigation

- Example 01: [A simple mechanically ventilated (mixing ventilation) room](#example-01): 
    - [Transient](#example-01a): `01a_simple_mech_vent_transient.gh`
    - [Steady-state](#example-01b): `01b_simple_mech_vent_steadystate.gh`


## Example 01

A simple mechanically ventilated (mixing ventilation) room:

- White: Walls and floor
  - T: 295.15 K
- Green: Air inlet
  - U: 0.5 m/s
  - T: 283.15 K
  - CO2: 400 ppm
- Orange: Air outlet
- Blue: Ceiling (excluding air inlets and outlets)
  - T: 295.15 K
- Dark gray: A solid body with a higher surface temperature
  - T: 305 K
- Internal Fields
  - T: 300 K
  - CO2: 1000 ppm

![Example 01 Room Model](./_pics/01_simple_mech_vent_Rhino.png)

### Example 01a

Transient simulation (0 - 300 s). Results in ParaView:


![Example 01a simulation results GIF](./_pics/01a_simple_mech_vent_transient_ParaView.gif)


<table style="table-layout: fixed; width: 100%;">
  <tr>
    <td align="center" valign="top">
      <img src="./_pics/01a_simple_mech_vent_transient_ParaView_05s.png" width="100%" alt="Example 01a simulation result 05s" />
      <br/>
      <sub>
        time = 5 s
      </sub>
    </td>
    <td align="center" valign="top">
      <img src="./_pics/01a_simple_mech_vent_transient_ParaView_30s.png" width="100%" alt="Example 01a simulation result 30s" />
      <br/>
      <sub>
        time = 30 s
      </sub>
    </td>
    <td align="center" valign="top">
      <img src="./_pics/01a_simple_mech_vent_transient_ParaView_90s.png" width="100%" alt="Example 01a simulation result 90s" />
      <br/>
      <sub>
        time = 90 s
      </sub>
    </td>
    <td align="center" valign="top">
      <img src="./_pics/01a_simple_mech_vent_transient_ParaView_300s.png" width="100%" alt="Example 01a simulation result 300s" />
      <br/>
      <sub>
        time = 300 s
      </sub>
    </td>
  </tr>
</table>

#### Residuals:

![Example 01a residuals](./_pics/01a_simple_mech_vent_transient_residuals.png)

### Example 01b

Steady-state simulation (2000 iterations). Results in ParaView:


![Example 01b simulation result](./_pics/01b_simple_mech_vent_steadystate_ParaView.png)

#### Residuals:

![Example 01b residuals](./_pics/01b_simple_mech_vent_steadystate_residuals.png)


[Back to top ↥](#quick-navigation)