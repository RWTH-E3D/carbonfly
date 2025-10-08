# GH inputs:
#   age (float), 
#   met (float): must be one of [1.0, 1.2, 1.4, 1.6, 2.0, 3.0, 4.0]
#   gender (optional, str): "male" or "female" or None
#   breathing_flow_rate (float): Average breathing flow rate in L/min
# GH outputs:
#   mass (float): mean body mass in kg
#   BMR (float): Basal Metabolic Rate in MJ/day
#   CO2_Ls (float): CO2 generation rate in L/s
#   CO2 (float): CO2 concentration
#   CO2_ppm (float): CO2 concentration in ppm

from carbonfly.utils import co2_generation_rate
from math import isfinite

if not isfinite(age):
    raise ValueError("age must be a finite number.")
if not isfinite(met):
    raise ValueError("met must be a finite number.")

if breathing_flow_rate is None:
    breathing_flow_rate = 7.2   # default 7.2 L/min

result = co2_generation_rate(
    age=age, 
    met=met, 
    gender=gender or None
)

mass = result["mass"]
BMR = result["BMR"]
CO2_Ls = result["CO2"]

breathing_flow_rate_Ls = breathing_flow_rate / 60   # L/min -> L/s
CO2 = round(CO2_Ls / breathing_flow_rate_Ls, 6)
CO2_ppm = 1e6 * CO2 # ppm
