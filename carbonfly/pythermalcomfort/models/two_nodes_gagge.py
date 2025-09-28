from __future__ import annotations

import math

from typing import Dict, Any

# posture constants
POSTURE_SITTING = "sitting"
POSTURE_STANDING = "standing"

# 1 met = 58.2 W/m2
met_to_w_m2 = 58.2

def p_sat_torr(tdb: float) -> float:
    """
    Estimate saturation vapor pressure in torr.

    Parameters
    ----------
    tdb : float
        Dry-bulb air temperature [°C]

    Returns
    -------
    float
        Saturation vapor pressure [torr]
    """
    return math.exp(18.6686 - 4030.183 / (tdb + 235.0))
    

def two_nodes_gagge(
    tdb: float,
    tr: float,
    v: float,
    rh: float,
    met: float,
    clo: float,
    wme: float = 0.0,
    body_surface_area: float = 1.8258,
    p_atm: float = 101325.0,
    position: str = POSTURE_STANDING,
    max_skin_blood_flow: float = 90.0,
    round_output: bool = True,
    max_sweating: float = 500.0,
    w_max: float | None = None,
    calculate_ce: bool = False,
) -> Dict[str, Any]:
    """
    Scalar-only implementation of Gagge Two-Node model (Gagge et al., 1986).

    Parameters are identical in meaning to the original function but accept only scalars.

    Returns
    -------
    dict with keys:
      e_skin, e_rsw, e_max, q_sensible, q_skin, q_res, t_core, t_skin, m_bl, m_rsw,
      w, w_max, set, et, pmv_gagge, pmv_set, disc, t_sens
    """
    # vapor pressure (torr)
    vapor_pressure = rh * p_sat_torr(tdb) / 100.0

    # alias for readability (keep variable names close to the original)
    air_speed = max(v, 0.1)
    k_clo = 0.25
    body_weight = 70.0           # kg
    met_factor = met_to_w_m2     # 58.2 W/m2 per met
    sbc = 5.6697e-8              # Stefan-Boltzmann const (W/m2/K^4)
    c_sw = 170.0                 # sweat drive
    c_dil = 120.0                # vasodilation drive (ASHRAE sometimes lists 50)
    c_str = 0.5                  # vasoconstriction drive

    temp_skin_neutral = 33.7
    temp_core_neutral = 36.8
    alfa = 0.1
    temp_body_neutral = alfa * temp_skin_neutral + (1.0 - alfa) * temp_core_neutral
    skin_blood_flow_neutral = 6.3

    # state
    t_skin = temp_skin_neutral
    t_core = temp_core_neutral
    m_bl = skin_blood_flow_neutral

    # initialize outputs
    e_skin = 0.1 * met                 # W
    q_sensible = 0.0                   # W
    w = 0.0                            # skin wettedness
    _set = 0.0                         # Standard Effective Temperature
    e_rsw = 0.0                        # regulatory sweating heat, W
    e_diff = 0.0
    e_max = 0.0
    m_rsw = 0.0
    q_res = 0.0                        # respiration heat loss, W
    et = 0.0
    e_req = 0.0
    r_ea = 0.0
    r_ecl = 0.0
    c_res = 0.0                        # sensible resp heat

    pressure_in_atm = p_atm / 101325.0
    sim_minutes = 60                   # simulation length in minutes (explicit stepping)

    r_clo = 0.155 * clo                # m2K/W
    f_a_cl = 1.0 + 0.15 * clo          # clothing area factor
    lr = 2.2 / pressure_in_atm         # Lewis ratio
    rm = (met - wme) * met_factor      # net metabolic (W/m2)
    m = met * met_factor               # metabolic (W/m2)

    e_comfort = 0.42 * (rm - met_factor)
    e_comfort = max(e_comfort, 0.0)

    i_cl = 1.0
    if clo > 0.0:
        i_cl = 0.45  # vapor permeation eff through clothing

    if w_max is None:
        w_max = 0.38 * (air_speed ** -0.29)      # naked
        if clo > 0.0:
            w_max = 0.59 * (air_speed ** -0.08)  # clothed

    # convective coefficients
    h_cc = 3.0 * (pressure_in_atm ** 0.53)
    h_fc = 8.600001 * ((air_speed * pressure_in_atm) ** 0.53)
    h_cc = max(h_cc, h_fc)
    if (not calculate_ce) and met > 0.85:
        h_c_met = 5.66 * ((met - 0.85) ** 0.39)
        h_cc = max(h_cc, h_c_met)

    h_r = 4.7  # W/m2/K (linearized)
    h_t = h_r + h_cc
    r_a = 1.0 / (f_a_cl * h_t)
    t_op = (h_r * tr + h_cc * tdb) / h_t

    t_body = alfa * t_skin + (1.0 - alfa) * t_core

    # respiration (latent & sensible)
    q_res = 0.0023 * m * (44.0 - vapor_pressure)
    c_res = 0.0014 * m * (34.0 - tdb)

    # time marching (explicit Euler, 1-min steps)
    for _ in range(sim_minutes):
        # clothing surface temperature (fixed-point iteration)
        t_cl = (r_a * t_skin + r_clo * t_op) / (r_a + r_clo)
        for _iter in range(150):
            # clothing emissivity ~0.95; posture area ratio
            if position == POSTURE_SITTING:
                area_ratio = 0.7
            else:
                area_ratio = 0.73
            h_r = 4.0 * 0.95 * sbc * (((t_cl + tr) / 2.0 + 273.15) ** 3.0) * area_ratio
            h_t = h_r + h_cc
            r_a = 1.0 / (f_a_cl * h_t)
            t_op = (h_r * tr + h_cc * tdb) / h_t
            t_cl_new = (r_a * t_skin + r_clo * t_op) / (r_a + r_clo)
            if abs(t_cl_new - t_cl) <= 0.01:
                t_cl = t_cl_new
                break
            t_cl = t_cl_new
        else:
            raise RuntimeError("Clothing temperature iteration did not converge.")

        q_sensible = (t_skin - t_op) / (r_a + r_clo)
        # heat flow core<->skin (5.28 tissue conduct., 1.163 blood thermal cap.)
        hf_cs = (t_core - t_skin) * (5.28 + 1.163 * m_bl)
        s_core = m - hf_cs - q_res - c_res - wme
        s_skin = hf_cs - q_sensible - e_skin
        tc_sk = 0.97 * alfa * body_weight
        tc_cr = 0.97 * (1.0 - alfa) * body_weight
        d_t_sk = (s_skin * body_surface_area) / (tc_sk * 60.0)
        d_t_cr = (s_core * body_surface_area) / (tc_cr * 60.0)
        t_skin += d_t_sk
        t_core += d_t_cr
        t_body = alfa * t_skin + (1.0 - alfa) * t_core

        # control signals
        sk_sig = t_skin - temp_skin_neutral
        warm_sk = sk_sig if sk_sig > 0.0 else 0.0
        colds = (-sk_sig) if (-sk_sig) > 0.0 else 0.0

        c_reg_sig = t_core - temp_core_neutral
        c_warm = c_reg_sig if c_reg_sig > 0.0 else 0.0
        c_cold = (-c_reg_sig) if (-c_reg_sig) > 0.0 else 0.0

        bd_sig = t_body - temp_body_neutral
        warm_b = bd_sig if bd_sig > 0.0 else 0.0

        # blood flow
        m_bl = (skin_blood_flow_neutral + c_dil * c_warm) / (1.0 + c_str * colds)
        m_bl = min(m_bl, max_skin_blood_flow)
        m_bl = max(m_bl, 0.5)

        # sweating
        m_rsw = c_sw * warm_b * math.exp(warm_sk / 10.7)
        m_rsw = min(m_rsw, max_sweating)
        e_rsw = 0.68 * m_rsw

        # evaporative caps
        r_ea = 1.0 / (lr * f_a_cl * h_cc)
        r_ecl = r_clo / (lr * i_cl)
        e_req = rm - q_res - c_res - q_sensible
        e_max = (math.exp(18.6686 - 4030.183 / (t_skin + 235.0)) - vapor_pressure) / (r_ea + r_ecl)
        if e_max == 0.0:
            e_max = 1e-3

        p_rsw = e_rsw / e_max
        w = 0.06 + 0.94 * p_rsw
        e_diff = w * e_max - e_rsw
        if w > w_max:
            w = w_max
            p_rsw = w_max / 0.94
            e_rsw = p_rsw * e_max
            e_diff = 0.06 * (1.0 - p_rsw) * e_max
        if e_max < 0.0:
            e_diff = 0.0
            e_rsw = 0.0
            w = w_max

        e_skin = e_rsw + e_diff
        m_rsw = e_rsw / 0.68  # back-calc mass rate
        met_shivering = 19.4 * colds * c_cold
        m = rm + met_shivering
        alfa = 0.0417737 + 0.7451833 / (m_bl + 0.585417)

    q_skin = q_sensible + e_skin
    p_s_sk = math.exp(18.6686 - 4030.183 / (t_skin + 235.0))

    # Standard environment (for SET)
    h_r_s = h_r
    h_c_s = 3.0 * (pressure_in_atm ** 0.53)
    if (not calculate_ce) and met > 0.85:
        h_c_met = 5.66 * ((met - 0.85) ** 0.39)
        h_c_s = max(h_c_s, h_c_met)
    h_c_s = max(h_c_s, 3.0)
    h_t_s = h_c_s + h_r_s

    r_clo_s = 1.52 / ((met - wme / met_factor) + 0.6944) - 0.1835
    r_cl_s = 0.155 * r_clo_s
    f_a_cl_s = 1.0 + k_clo * r_clo_s
    f_cl_s = 1.0 / (1.0 + 0.155 * f_a_cl_s * h_t_s * r_clo_s)
    i_m_s = 0.45
    i_cl_s = i_m_s * h_c_s / h_t_s * (1 - f_cl_s) / (h_c_s / h_t_s - f_cl_s * i_m_s)
    r_a_s = 1.0 / (f_a_cl_s * h_t_s)
    r_ea_s = 1.0 / (lr * f_a_cl_s * h_c_s)
    r_ecl_s = r_cl_s / (lr * i_cl_s)
    h_d_s = 1.0 / (r_a_s + r_cl_s)
    h_e_s = 1.0 / (r_ea_s + r_ecl_s)

    # SET (Newton secant-like iteration)
    delta = 1e-4
    dx = 1e6
    _set = round(t_skin - q_skin / h_d_s, 2)
    while abs(dx) > 0.01:
        err_1 = q_skin - h_d_s * (t_skin - _set) - w * h_e_s * (p_s_sk - 0.5 * math.exp(18.6686 - 4030.183 / (_set + 235.0)))
        err_2 = q_skin - h_d_s * (t_skin - (_set + delta)) - w * h_e_s * (p_s_sk - 0.5 * math.exp(18.6686 - 4030.183 / (_set + delta + 235.0)))
        new_set = _set - delta * err_1 / (err_2 - err_1)
        dx = new_set - _set
        _set = new_set

    # ET (similar iteration using actual environment)
    h_d = 1.0 / (r_a + r_clo)
    h_e = 1.0 / (r_ea + r_ecl)
    et_old = t_skin - q_skin / h_d
    delta = 1e-4
    dx = 1e6
    while abs(dx) > 0.01:
        err_1 = q_skin - h_d * (t_skin - et_old) - w * h_e * (p_s_sk - 0.5 * math.exp(18.6686 - 4030.183 / (et_old + 235.0)))
        err_2 = q_skin - h_d * (t_skin - (et_old + delta)) - w * h_e * (p_s_sk - 0.5 * math.exp(18.6686 - 4030.183 / (et_old + delta + 235.0)))
        et = et_old - delta * err_1 / (err_2 - err_1)
        dx = et - et_old
        et_old = et

    # thermal sensation & discomfort
    tbm_l = (0.194 / met_to_w_m2) * rm + 36.301
    tbm_h = (0.347 / met_to_w_m2) * rm + 36.669

    t_sens = 0.4685 * (t_body - tbm_l)
    if (t_body >= tbm_l) and (t_body < tbm_h):
        t_sens = w_max * 4.7 * (t_body - tbm_l) / (tbm_h - tbm_l)
    elif t_body >= tbm_h:
        t_sens = w_max * 4.7 + 0.4685 * (t_body - tbm_h)

    disc = 4.7 * (e_rsw - e_comfort) / (e_max * w_max - e_comfort - e_diff) if (e_max * w_max - e_comfort - e_diff) != 0 else t_sens
    if disc <= 0.0:
        disc = t_sens

    # PMV (Gagge)
    pmv_gagge = (0.303 * math.exp(-0.036 * m) + 0.028) * (e_req - e_comfort - e_diff)

    # PMV (SET-based)
    dry_set = h_d_s * (t_skin - _set)
    e_req_set = rm - c_res - q_res - dry_set
    pmv_set = (0.303 * math.exp(-0.036 * m) + 0.028) * (e_req_set - e_comfort - e_diff)

    out = {
        "e_skin": e_skin,
        "e_rsw": e_rsw,
        "e_max": e_max,
        "q_sensible": q_sensible,
        "q_skin": q_skin,
        "q_res": q_res,
        "t_core": t_core,
        "t_skin": t_skin,
        "m_bl": m_bl,
        "m_rsw": m_rsw,
        "w": w,
        "w_max": w_max,
        "set": _set,
        "et": et,
        "pmv_gagge": pmv_gagge,
        "pmv_set": pmv_set,
        "disc": disc,
        "t_sens": t_sens,
    }

    if round_output:
        for k, v in out.items():
            if isinstance(v, (int, float)):
                out[k] = round(v, 2)

    return out