from carbonfly.utils import wind_pressure_en1991

results = wind_pressure_en1991(
    vb0 = vb0,
    z = z,
    h = h,
    d = d,
    window_size = window_size,
    zone = zone,
    terrain = terrain or 4,
    c_dir = c_dir or 1.0,
    c_season = c_season or 1.0,
    c0 = c0 or 1.0,
    rho = rho or 1.25,
    k_i = k_i or 1.0
)

we = results["we"]
cpe = results["cpe"]
qp = results["qp"]
vm = results["vm"]
Iv = results["Iv"]
cr = results["cr"]
vb = results["vb"]