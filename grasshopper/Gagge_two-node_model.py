from carbonfly.pythermalcomfort.models import two_nodes_gagge

result = two_nodes_gagge(
    tdb=tdb, 
    tr=tr, 
    v=v, 
    rh=rh, 
    met=met, 
    clo=clo, 
    wme=wme or 0, 
    body_surface_area=BSA or 1.8258, 
    p_atm=p_atm or 101325, 
    position=position or "standing", 
    max_skin_blood_flow=max_skin_blood_flow or 90, 
    max_sweating=max_sweating or 500, 
    w_max=w_max or False
)

e_skin = result["e_skin"]
e_rsw = result["e_rsw"]
e_max = result["e_max"]
q_sensible = result["q_sensible"]
q_skin = result["q_skin"]
q_res = result["q_res"]
t_core = result["t_core"]
t_skin = result["t_skin"]
m_bl = result["m_bl"]
m_rsw = result["m_rsw"]
w = result["w"]
w_max = result["w_max"]
SET = result["set"]
ET = result["et"]
pmv_gagge = result["pmv_gagge"]
pmv_set = result["pmv_set"]
disc = result["disc"]
t_sens = result["t_sens"]