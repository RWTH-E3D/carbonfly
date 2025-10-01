from carbonfly.pythermalcomfort.models import two_nodes_gagge_sleep

result = two_nodes_gagge_sleep(
    tdb=tdb, 
    tr=tr, 
    v=v, 
    rh=rh, 
    clo=clo,
    thickness_quilt=thickness_quilt,
    wme=wme or 0,  
    p_atm=p_atm or 101325,
    height=height or 171,
    weight=weight or 70,
    c_sw=c_sw or 170,
    c_dil=c_dil or 120,
    c_str=c_str or 0.5,
    temp_skin_neutral=temp_skin_neutral or 33.7,
    temp_core_neutral=temp_core_neutral or 36.8,
    e_skin=e_skin or 0.094,
    alfa=alfa or 0.1,
    skin_blood_flow=skin_blood_flow or 6.3,
    met_shivering=met_shivering or 0,
)

e_skin = result["e_skin"]
t_core = result["t_core"]
t_skin = result["t_skin"]
skin_blood_flow=result["skin_blood_flow"]
w = result["wet"]
SET = result["set"]
t_sens = result["t_sens"]
disc = result["disc"]
met_shivering=result["met_shivering"]
alfa=result["alfa"]


