from carbonfly.iaq import iaq_co2

results = iaq_co2(
    co2_indoor = CO2_indoor,
    co2_outdoor = CO2_outdoor or 400,
    standard = standard or "EN"
)

reports = results[0]
index = results[1]

standard_name = reports["standard"]
co2_indoor = reports["co2_indoor"]
co2_outdoor = reports["co2_outdoor"]

if standard == "EN":
    description = (
        "Evaluation based on CO2 concentration differences between indoors and outdoors.\n"
        "- [Index = 1] Category I: ΔCO2 <= 550 ppm\n"
        "- [Index = 2] Category II: ΔCO2 <= 800 ppm\n"
        "- [Index = 3] Category III: ΔCO2 <= 1350 ppm\n"
        "- [Index = 4] Category IV: ΔCO2 > 1350 ppm"
    )
elif standard == "LEHB":
    description = (
        "Evaluation based on CO2 concentration indoors.\n"
        "- [Index = 1] Acceptable: CO2 <= 1000 ppm\n"
        "- [Index = 2] Unacceptable: CO2 > 1000 ppm"
    )
elif standard == "SS":
    description = (
        "Evaluation based on CO2 concentration differences between indoors and outdoors.\n"
        "- [Index = 1] Acceptable: ΔCO2 <= 700 ppm\n"
        "- [Index = 2] Unacceptable: ΔCO2 > 700 ppm"
    )
elif standard == "HK":
    description = (
        "Evaluation based on CO2 concentration indoors (averaging time 8-hour)."
        "Here the average is changed to an instantaneous evaluation for each measurment.\n"
        "- [Index = 1] Excellent Class: CO2 <= 800 ppm\n"
        "- [Index = 2] Good Class: CO2 <= 1000 ppm\n"
        "- [Index = 3] Unacceptable: CO2 > 1000 ppm"
    )
elif standard == "UBA":
    description = (
        "Evaluation based on CO2 concentration indoors.\n"
        "- [Index = 1] Hygienically safe: CO2 < 1000 ppm\n"
        "- [Index = 2] Hygienically conspicuous: CO2 <= 2000 ppm\n"
        "- [Index = 3] Hygienically unacceptable: CO2 > 2000 ppm"
    )
elif standard == "DOSH":
    description = (
        "Evaluation based on CO2 concentration indoors.\n"
        "- [Index = 1] Acceptable: CO2 <= 1000 ppm\n"
        "- [Index = 2] Unacceptable: CO2 > 1000 ppm"
    )
elif standard == "NBR":
    description = (
        "Evaluation based on CO2 concentration differences between indoors and outdoors.\n"
        "- [Index = 1] Acceptable: ΔCO2 <= 700 ppm\n"
        "- [Index = 2] Unacceptable: ΔCO2 > 700 ppm"
    )
else:
    description = "N/A"

report = (
    f"Standard: {standard_name}\n"
    f"CO2 indoor: {co2_indoor} ppm\n"
    f"CO2 outdoor: {co2_outdoor} ppm\n"
    f"Index: {index}\n"
    "\n"
    f"{description}"
)